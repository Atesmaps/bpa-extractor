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
import sys
import time
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

import atesmaps_utilities as ates_utils
import bpa_urls

# ----- CONFIGURATION ----- #
ZONE_NAME = "Aran"


def get_report(date: str):
    """
    Do an API call and return BPA data in BeautifulSoup object.

    :param date: Select specific date for BPA. Default today.
                 Format: YYYY-MM-DD
    """

    try:
        print("Downloading Aran BPA report...")

        # Check if BPA report for tomorrow are available
        selected_date = datetime.strptime(date, "%Y-%m-%d")
        tomorrow = (selected_date + timedelta(days=1)).strftime("%Y-%m-%d")
        print(f"Checking if BPA report are available for tomorrow '{tomorrow}'...")
        response = requests.get(url=bpa_urls.BPA_ARAN_URL.format(date=tomorrow))
        # Parsing html content with beautifulsoup
        if response.status_code != 200:
            print(
                f"Avalanche report for zone Aran using date {tomorrow} is not available yet."
            )
            print(f"Checking BPA report for current date '{date}'...")
            response = requests.get(url=bpa_urls.BPA_ARAN_URL.format(date=date))
            if response.status_code != 200:
                print(
                    f"Avalanche report for zone Aran using date {date} is not available yet."
                )
                sys.exit(1)
        return BeautifulSoup(response.text, "html.parser")
    except Exception as exc:
        raise Exception("Couldn't get Aran BPA.") from exc


def get_bpa_publication_date(bpa) -> str:
    """
    Return BPA date from report.

    :param bpa: BeautifulSoup parsed HTML.
    """
    import locale

    try:
        # Save current locale
        original_locale = locale.getlocale(locale.LC_TIME)

        print("Obtaining BPA report date...")
        bpa_date_container = bpa.body.find_all("div", attrs={"class": "bTitle"})[0].text
        locale.setlocale(locale.LC_TIME, "ca_ES.UTF-8")  # Aran BPA is in Catalan
        bpa_date_obj = datetime.strptime(
            bpa_date_container.encode("latin1").decode("utf-8").split(",")[1].strip(), "%d %B de %Y"
        )
        bpa_date = bpa_date_obj.strftime("%Y-%m-%d")

        # Restore locale
        locale.setlocale(locale.LC_TIME, original_locale)

        return bpa_date
    except Exception as exc:
        raise Exception("Couldn't get avalanche report date from Aran BPA.") from exc


def danger_level_from_bpa(bpa) -> int:
    """
    Return avalanche danger level from BPA report.

    :param bpa: BeautifulSoup parsed HTML.
    """

    try:
        print("Processing danger level from report...")
        danger_level = []
        for div in bpa.body.find_all("div", attrs={"class": "dangerImg"}):
            if "conselharan2" in div.img["src"] or "warning_pictos" in div.img["src"]:
                danger_level = (
                    div.img["src"].split("/")[-1].split(".")[0].split("_")[1:]
                )
                break

        danger_levels = [int(x) for x in danger_level]
        print(f"Danger level for 'Aran' zone: {max(danger_levels)}.")
        return max(danger_levels)
    except Exception as exc:
        raise Exception("Couldn't get avalanche danger level from Aran BPA.") from exc


def main() -> None:
    """Extract BPA data from Lauegi website."""

    # Init
    start_time = time.time()
    print("** ATESMaps Avalanche Report Extractor **")

    # Today date in format YYYY-MM-DD
    today = datetime.today().strftime("%Y-%m-%d")

    print("Updating avalanche danger level...")
    print(f"Zone: {ZONE_NAME}")
    print(f"Current date: {today}")

    # Load zone ID for Aran
    zone_id = ates_utils.refresh_zone_ids()[ZONE_NAME]

    # Get BPA date from report
    report = get_report(date=today)
    bpa_date = get_bpa_publication_date(bpa=report)

    # Check if BPA danger levels for BPA report date already exists.
    print(f"BPA report date: {bpa_date}")

    # Get danger level
    danger_lvl = danger_level_from_bpa(bpa=report)

    # Insert data to DB
    ates_utils.save_data(
        zone_name=ZONE_NAME, zone_id=zone_id, date=bpa_date, level=danger_lvl
    )

    # End
    print("Total time elapsed: {:.2f} seconds.".format(time.time() - start_time))
    print("Bye.")


# Trigger
main()
