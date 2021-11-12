#!/usr/bin/python3
############################################################
#
#   ATESMaps - BPA Extractors - ARAN
#
#   Python script that obtains data of avalanche  bulletin
#   generated and managed by Lauegi & Conselh d'Aran.
#
#   +INFO: https://lauegi.report
#
#   Collaborators:
#       * Nil Torrano: <ntorrano@atesmaps.org>
#       * Atesmaps Team: <info@atesmaps.org>
#
#   November 2021
#
############################################################
from datetime import datetime
import sys
import time
import requests
from bs4 import BeautifulSoup
import bpa_urls
import db_connector as db
import constants as const
import atesmaps_utilities as ates_utils


def get_report(date: str=datetime.today().strftime("%Y-%m-%d")):
    '''
    Do an API call and return BPA data in BeatifulSoup object.

    :param date: Select especific date for BPA. Default today.
                 Format: YYYY-MM-DD   
    '''

    try:
        print(f"Downloading Aran BPA report...")
        response = requests.get(
            url=bpa_urls.BPA_ARAN_URL.format(date=date)
        )
        # Parsing html content with beautifulsoup
        if response.status_code != 200:
            print(f"Avalanche report for zone Aran using date {date} is not available yet.")
            sys.exit(1)
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as exc:
        raise Exception("Couldn't get Aran BPA.") from exc


def danger_level_from_bpa(bpa) -> int:
    '''
    Return avalanche danger level from BPA report.
    
    :param bpa: BeatifulSoup parsed HTML.
    '''

    try:
        print("Processing danger level from report...")
        for div in bpa.body.find_all("div", attrs={"class": "dangerImg"}):
            if "conselharan2" in div.img["src"]:
                danger_level = div.img["src"].split("/")[-1].split(".")[0].split("_")[1:]
                break

        danger_levels = [int(x) for x in danger_level]
        print(f"Danger level for 'Aran' zone: {max(danger_levels)}.")
        return max(danger_levels)
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
    '''Extract BPA data from Lauegi archive.'''

    # Init
    start_time = time.time()

    # Today date in format YYYY-MM-DD
    today = datetime.today().strftime("%Y-%m-%d")
    today = "2021-04-30"
    print("** ATESMaps Avalanche Report Extractor **")
    print(f"Updating avalanche danger level...")
    print(f"Zone: Aran")
    print(f"Date: {today}")

    # Load zone ID for Aran
    zone_id = ates_utils.refresh_zone_ids()["Aran"]

    # Get danger level
    report = get_report(date=today)
    danger_lvl = danger_level_from_bpa(bpa=report)

    # Insert data to DB
    save_data(
        zone=zone_id,
        date=today,
        level=danger_lvl
    )

    # End
    print("Total time elapsed: {:.2f} seconds.".format(time.time() - start_time))
    print("Bye.")


# Trigger
main()