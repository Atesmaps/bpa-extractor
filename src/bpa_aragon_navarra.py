#!/usr/bin/python3
######################################################################################
#
#   ATESMaps - BPA Extractors - ARAGON / NAVARRA
#
#   Python script that obtains data of avalanche bulletin
#   generated and managed by AEMET.
#
#   +INFO: https://www.aemet.es/es/eltiempo/prediccion/montana/boletin_peligro_aludes
#
#   Collaborators:
#       * Nil Torrano: <ntorrano@atesmaps.org>
#       * Atesmaps Team: <info@atesmaps.org>
#
#   November 2021
#
######################################################################################
from datetime import datetime
import sys
import time
import requests
import fitz

import bpa_urls
import atesmaps_utilities as ates_utils


############ CONFIGURATION ################
ARAGON_NAV_ZONES = [
    "Navarra",
    "Jacetania",
    "Gállego",
    "Sobrarbe",
    "Ribagorza"
]

##### Avalanche Levels #####
AVALANCHE_LEVELS = {
    "Débil": 1,
    "Limitado": 2,
    "Notable": 3,
    "Fuerte": 4,
    "Muy Fuerte": 5
}


def get_report(output_file: str) -> None:
    '''
    Do an API call and return BPA data in PDF format.

    :param output_file: String with the full path for the new PDF file.
    :param download link: URL for download PDF.
    '''

    try:
        print(f"Downloading Aragon-Navarra BPA report from: {bpa_urls.BPA_ARAGON_NAV_URL}...")
        response = requests.get(
            url=bpa_urls.BPA_ARAGON_NAV_URL
        )
        if response.status_code != 200:
            print(f"Avalanche report for Aragon & Navarra zones is not available.")
            sys.exit(1)
        # Download report as PDF
        with open(output_file, "wb") as f:
            f.write(response.content)
        return
    except Exception as exc:
        raise Exception("Couldn't get Aragon-Navarra BPA.") from exc


def get_danger_levels_from_bpa(bpa_file: str) -> int:
    '''
    Return avalanche danger levels from BPA.

    :param bpa_file: Full path to PDF file with BPA.
    '''

    print("Obtaining danger levels from BPA report...")
    levels_from_bpa = []
    with fitz.open(bpa_file) as f:
        for page in f:
            p_text = page.get_text().split("\n")
            for index, line_text in enumerate(p_text):
                if line_text in ARAGON_NAV_ZONES:
                    # Get zone ID from zone name
                    zone_id = ates_utils.refresh_zone_ids()[line_text]

                    danger_lvl = AVALANCHE_LEVELS[p_text[index + 1]]
                    print(f"Danger level for '{line_text}' zone: {danger_lvl}")
                    levels_from_bpa.append({
                        "zone_id": zone_id,
                        "zone_name": line_text,
                        "level": danger_lvl
                    })

    return levels_from_bpa


def main() -> None:
    '''Extract BPA data from AEMET website.'''

    # Init
    start_time = time.time()
    print("** ATESMaps Avalanche Report Extractor **")

    # Today date in format YYYY-MM-DD
    today = datetime.today().strftime("%Y-%m-%d")

    print(f"Updating avalanche danger level...")
    print(f"Zone: Aragon & Navarra Pyrenees")
    print(f"Current date: {today}")

    # Get danger level
    pdf_bpa = f"/tmp/aragon_nav_bpa_{today}.pdf"
    get_report(output_file=pdf_bpa)

    # Get danger levels from BPA
    danger_lvls = get_danger_levels_from_bpa(
        bpa_file=pdf_bpa
    )

    # Insert data to DB
    for zone in danger_lvls:
        ates_utils.save_data(
            zone_name=zone["zone_name"],
            zone_id=zone["zone_id"],
            date=today,
            level=zone["level"]
        )

    # End
    print("Total time elapsed: {:.2f} seconds.".format(time.time() - start_time))
    print("Bye.")


# Trigger
main()
