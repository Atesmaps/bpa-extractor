#!/usr/bin/python3
############################################################
#
#   ATESMaps - BPA Extractors - ICGC (Institut Cartogràfic
#   i Geològic de Catalunya)
#
#   Python script that obtains data of avalanche bulletin
#   generated and managed by ICGC for Catalunya Pyrenees.
#
#   +INFO: https://bpa.icgc.cat
#
#   Collaborators:
#       * Nil Torrano: <ntorrano@atesmaps.org>
#       * Atesmaps Team: <info@atesmaps.org>
#
#   November 2021
#
############################################################
import sys
import time
from datetime import datetime
from typing import Iterable, List

import requests
from PyPDF2 import PdfReader

import atesmaps_utilities as ates_utils
import bpa_urls

# ----- CONFIGURATION ----- #

# ----- Zones managed by ICGC ----- #
ICGC_ZONES = [
    "Aran - Franja Nord Pallaresa",
    "Ribagorçana - Vall Fosca",
    "Pallaresa",
    "Perafita - Puigpedrós",
    "Vessant Nord Cadí - Moixeró",
    "Prepirineu",
    "Ter - Freser",
]

# ----- Avalanche Levels ----- #
AVALANCHE_LEVELS = {
    "Feble (1)": 1,
    "Moderat (2)": 2,
    "Marcat (3)": 3,
    "Fort (4)": 4,
    "Molt fort (5)": 5,
}


def get_report(
    output_file: str, date: str = datetime.today().strftime("%Y-%m-%d")
) -> None:
    """
    Do an API call and return BPA data in PDF.

    :param output_file: String with the full path for the new PDF file.
    :param date: Select specific date for BPA. Default today.
                 Format: YYYY-MM-DD
    """

    try:
        print("Downloading ICGC BPA report...")
        response = requests.get(url=bpa_urls.BPA_ICGC_URL.format(date=date))
        if response.status_code != 200:
            print(
                f"Avalanche report for zone ICGC using date {date} is not available yet."
            )
            sys.exit(1)
        # Download report as PDF
        with open(output_file, "wb") as f:
            f.write(response.content)
        return
    except Exception as exc:
        raise Exception("Couldn't get ICGC BPA.") from exc


def remove_duplicates(dup_list: Iterable) -> List:
    """
    Remove list duplicates.

    :param dup_list: Python list that you want to remove duplicates.
    """

    return list(set(dup_list))


def levels_to_numeric(danger_levels: Iterable) -> List:
    """
    Extract avalanche danger level from string and return numeric value.

    :param danger_levels: List with avalanche levels as string.
    """

    num_levels = []
    for bpa_level in danger_levels:
        # for str_level in set(AVALANCHE_LEVELS).intersection(bpa_level.split()):
        num_levels.append(AVALANCHE_LEVELS[bpa_level])

    return num_levels


def danger_levels_from_bpa(bpa_file: str) -> list:
    """
    Return avalanche danger level from BPA report for each zone.

    :param bpa_file: PDF file path with BPA report.
    """

    try:
        levels_from_bpa = []

        # Parse BPA in PDF format.
        with open(bpa_file, "rb") as f:
            reader = PdfReader(f)
            for page in range(1, len(reader.pages)):
                contents = reader.pages[page].extract_text().split("\n")
                danger_levels = []
                zone = []
                for elem in contents:
                    zone += [
                        zone
                        for zone in ICGC_ZONES
                        if zone.replace(" ", "") == elem.replace(" ", "")
                    ]
                    danger_levels += [
                        level
                        for level in AVALANCHE_LEVELS
                        if (level in elem or level.upper() in elem)
                    ]

                # Check values
                if zone and danger_levels:
                    danger_level = max(levels_to_numeric(danger_levels=danger_levels))
                    # FIXME: Aran zone is updated using BPA managed by Lauegi.
                    if zone[0] == ICGC_ZONES[0]:
                        zone[0] = zone[0].replace("Aran - ", "")
                    # FIXME: Vessant Nord Cadí have different name in atesmaps DB
                    if zone[0] == ICGC_ZONES[4]:
                        new_name = zone[0].split(" ")
                        new_name.insert(2, "del")
                        zone[0] = " ".join(new_name)

                    # Get zone ID
                    zone_id = ates_utils.refresh_zone_ids()[zone[0]]

                    # Save values
                    print(f"Danger level for '{zone[0]}' zone: {danger_level}")
                    levels_from_bpa.append(
                        {
                            "zone_id": zone_id,
                            "zone_name": zone[0],
                            "level": danger_level,
                        }
                    )
                elif zone and not danger_levels:
                    print(
                        f"WARNING: Couldn't get avalanche danger level for '{zone}' zone."
                    )
                else:
                    print(
                        f"Couldn't extract data from page '{page}' using '{bpa_file}' report."
                    )

        return levels_from_bpa
    except Exception as exc:
        raise Exception("Couldn't get avalanche danger level from ICGC BPA.") from exc


def main() -> None:
    """Extract BPA data from ICGC web portal."""

    # Init
    start_time = time.time()
    print("** ATESMaps Avalanche Report Extractor **")

    # Today date in format YYYY-MM-DD
    today = datetime.today().strftime("%Y-%m-%d")

    print("Updating avalanche danger level...")
    print("Zone: ICGC - Catalunya Pyrenees")
    print(f"Date: {today}")

    # Get danger level
    pdf_bpa = f"/tmp/icgc_bpa_{today}.pdf"
    get_report(output_file=pdf_bpa)
    danger_lvls = danger_levels_from_bpa(bpa_file=pdf_bpa)

    # Insert data to DB
    for zone in danger_lvls:
        ates_utils.save_data(
            zone_name=zone["zone_name"],
            zone_id=zone["zone_id"],
            date=today,
            level=zone["level"],
        )

    # End
    print("Total time elapsed: {:.2f} seconds.".format(time.time() - start_time))
    print("Bye.")


# Trigger
main()
