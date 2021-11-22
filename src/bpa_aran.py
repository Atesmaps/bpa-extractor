#!/usr/bin/python3
############################################################
#
#   ATESMaps - BPA Extractors - ARAN
#
#   Python script that obtains data of avalanche bulletin
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
import atesmaps_utilities as ates_utils


########### CONFIGURATION ###########
# Set custom date with format YYYY-MM-DD or leave blank
# to use default.
# Default: Today
CUSTOM_DATE = "" # "2021-04-25"
ZONE_NAME = "Aran"


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


def main() -> None:
    '''Extract BPA data from Lauegi archive.'''

    # Init
    start_time = time.time()
    print("** ATESMaps Avalanche Report Extractor **")

    # Today date in format YYYY-MM-DD
    if CUSTOM_DATE:
        today = CUSTOM_DATE
    else:
        today = datetime.today().strftime("%Y-%m-%d")

    print(f"Updating avalanche danger level...")
    print(f"Zone: {ZONE_NAME}")
    print(f"Date: {today}")

    # Load zone ID for Aran
    zone_id = ates_utils.refresh_zone_ids()[ZONE_NAME]

    # Check if BPA for selected date already exists.
    if ates_utils.bpa_exists(date=today, zone_id=zone_id):
        print(f"Avalanche danger level already exists for the date '{today}' and zone '{ZONE_NAME}'")
        print("Bye.")
        sys.exit()

    # Get danger level
    report = get_report(date=today)
    danger_lvl = danger_level_from_bpa(bpa=report)

    # Insert data to DB
    ates_utils.save_data(
        zone_name=ZONE_NAME,
        zone_id=zone_id,
        date=today,
        level=danger_lvl
    )

    # End
    print("Total time elapsed: {:.2f} seconds.".format(time.time() - start_time))
    print("Bye.")


# Trigger
main()
