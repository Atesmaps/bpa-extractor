#!/usr/bin/python3
############################################################
#
#   ATESMaps - BPA Extractors - ICGC (Institu Cartogràfic 
#   i Geològic de Catalunya)
#
#   Python script that obtains data of avalanche  bulletin
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
from datetime import datetime
from hashlib import new
import sys
import time
from typing import Iterable, List
import requests
from py_pdf_parser.loaders import load_file
from PyPDF2 import PdfFileReader
import bpa_urls
import db_connector as db
import constants as const
import atesmaps_utilities as ates_utils


##### Zones managed by ICGC #####
ICGC_ZONES = [
    "Aran - Franja Nord Pallaresa",
    "Ribagorçana - Vall Fosca",
    "Pallaresa",
    "Perafita - Puigpedrós",
    "Vessant Nord Cadí - Moixeró",
    "Prepirineu",
    "Ter - Freser"
]

##### Avalanche Levels #####
AVALANCHE_LEVELS = {
    "FEBLE": 1,
    "MODERAT": 2,
    "MARCAT": 3,
    "FORT": 4,
    "MOLT FORT": 5
}


def get_report(output_file: str, date: str=datetime.today().strftime("%Y-%m-%d")) -> None:
    '''
    Do an API call and return BPA data in PDF.

    :param output_file: String with the full path for the new PDF file.
    :param date: Select especific date for BPA. Default today.
                 Format: YYYY-MM-DD
    '''

    try:
        print(f"Downloading ICGC BPA report...")
        response = requests.get(
            url=bpa_urls.BPA_ICGC_URL.format(date=date)
        )
        if response.status_code != 200:
            print(f"Avalanche report for zone ICGC using date {date} is not available yet.")
            sys.exit(1)
        # Download report as PDF
        with open(output_file, "wb") as f:
            f.write(response.content)
        return
    except Exception as exc:
        raise Exception("Couldn't get ICGC BPA.") from exc


def remove_duplicates(dup_list: Iterable) -> List:
    '''
    Remove list duplicates.

    :param dup_list: Python list that you want to remove duplicates.
    '''

    return list(set(dup_list))


def levels_to_numeric(danger_levels: Iterable) -> List:
    '''
    Extract avalanche danger level from string and return numeric value.

    :param danger_levels: List with avalanche levals as string.
    '''

    num_levels = []
    for bpa_level in danger_levels:
        # for str_level in set(AVALANCHE_LEVELS).intersection(bpa_level.split()):
        num_levels.append(AVALANCHE_LEVELS[bpa_level])
    
    return num_levels


def danger_levels_from_bpa(bpa_file) -> int:
    '''
    Return avalanche danger level from BPA report for each zone.
    
    :param bpa_file: PDF file path with BPA report.
    '''

    try:
        levels_from_bpa = []
        
        # Parse BPA in PDF format.
        with open(bpa_file, 'rb') as f:
            reader = PdfFileReader(f)
            for page in range(1, reader.getNumPages()):
                contents = reader.getPage(page).extractText().split('\n')
                danger_levels = []
                zone = []
                for elem in contents:
                    zone += [zone for zone in ICGC_ZONES if zone.replace(" ","") == elem.replace(" ","")]
                    danger_levels += [level for level in AVALANCHE_LEVELS if level in elem]

                # Check values
                if zone and danger_levels:
                    danger_level = max(levels_to_numeric(danger_levels=danger_levels))
                    # FIXME: Aran zone is updated using from Lauegi.
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
                    levels_from_bpa.append({
                        "zone_id": zone_id,
                        "level": danger_level
                    })
                elif zone and not danger_levels:
                    print(f"WARNING: Couldn't get avalanche danger level for '{zone}' zone.")
                else:
                    print(f"Couldn't extract data from page '{page}' using '{bpa_file}' report.")
        
        return levels_from_bpa
    except Exception as exc:
        raise Exception("Couldn't get avalanche danger level from Aran BPA.") from exc


def save_data(zone: str, date: str, level: str) -> None:
    '''
    Save data into database.
    '''

    # Insert dangel level to BPA table
    print("Updating data to zones information table...")
    q = f"UPDATE {const.TABLE_BPA} SET bpa='{level}' WHERE codi_zona = '{zone}'"
    db.update_data(query=q)
    
    # Insert data into BPA history
    print("Updating data to bpa history table...")
    q = f"INSERT INTO {const.TABLE_BPA_HISTORY} (zona, codi_zona, date_time, perill) " \
        f"VALUES ('Aran', '{zone}', '{datetime.now()}', '{level}')"
    db.update_data(query=q)


def main() -> None:
    '''Extract BPA data from ICGC web portal.'''

    # Init
    start_time = time.time()

    # Today date in format YYYY-MM-DD
    today = datetime.today().strftime("%Y-%m-%d")
    today = "2021-02-10"
    print("** ATESMaps Avalanche Report Extractor **")
    print(f"Updating avalanche danger level...")
    print(f"Zone: ICGC - Catalunya Pyrenees")
    print(f"Date: {today}")

    # Get danger level
    pdf_bpa = f"/tmp/icgc_bpa_{today}.pdf"
    # get_report(output_file=pdf_bpa, date=today)
    danger_lvls = danger_levels_from_bpa(bpa_file=pdf_bpa)

    # Insert data to DB
    for zone in danger_lvls:
        save_data(
            zone=zone["zone_id"],
            date=today,
            level=zone["level"]
        )

    # End
    print("Total time elapsed: {:.2f} seconds.".format(time.time() - start_time))
    print("Bye.")


# Trigger
main()