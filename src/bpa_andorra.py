#!/usr/bin/python3
############################################################
#
#   ATESMaps - BPA Extractors - ANDORRA
#
#   Python script that obtains data of avalanche bulletin
#   generated and managed by Andorra National Weather
#   Service.
#
#   +INFO: http://www.meteo.ad/estatneu
#
#   Collaborators:
#       * Nil Torrano: <ntorrano@atesmaps.org>
#       * Atesmaps Team: <info@atesmaps.org>
#
#   November 2021
#
############################################################
from datetime import datetime
from os import getenv
import re
import fitz
import sys
import time
import requests
from bs4 import BeautifulSoup
import bpa_urls
import atesmaps_utilities as ates_utils


############ CONFIGURATION ################
# Set custom date with format YYYY-MM-DD using
# environment variable "CUSTOM_DATE". If it's not
# set default date will be used.
# Default: Today
CUSTOM_DATE = getenv("CUSTOM_DATE")
ANDORRA_ZONES = {
    "iconos1": "Andorra nord",
    "iconos2": "Andorra centre",
    "iconos3": "Andorra sud"
}


def get_bpa_html():
    '''
    Return Andorra BPA report in HTML format from
    oficial website.
    '''

    print(f"Obtaining Andorra BPA report html...")
    response = requests.get(
        url=bpa_urls.BPA_ANDORRA_URL
    )
    # Parsing html content with beautifulsoup
    if response.status_code != 200:
        print(f"Andorra avalanche reporting web is not available.")
        sys.exit(1)
    
    return BeautifulSoup(response.text, 'html.parser')


def get_download_link() -> str:
    '''
    Return URL for download BPA print version as PDF format.
    '''

    try:
        print(f"Obtaining Andorra BPA report link...")
        bpa_html = get_bpa_html()
        return bpa_html.body.find("a", attrs={"title": "Versió per imprimir"})["href"]
    except Exception as exc:
        raise Exception("Couldn't get Andorra BPA link.") from exc


def get_report(download_link: str, output_file: str) -> None:
    '''
    Do an API call and return BPA file in PDF format.

    :param output_file: String with the full path for the new PDF file.
    :param download link: URL for download PDF.
    '''

    try:
        print(f"Downloading Andorra BPA report from: {download_link}...")
        response = requests.get(
            url=download_link
        )
        if response.status_code != 200:
            print(f"Avalanche report for Andorra zone is not available.")
            sys.exit(1)
        # Download report as PDF
        with open(output_file, "wb") as f:
            f.write(response.content)
        return
    except Exception as exc:
        raise Exception("Couldn't get Andorra BPA.") from exc


def get_bpa_danger_levels(date: str) -> list:
    '''
    Return BPA danger levels for each Andorra zone defined
    in ANDORRA_ZONES variable.

    :param date: The selected date that you want to check danger level.
    '''

    try:
        print("Obtaining danger levels from BPA report...")
        levels_from_bpa = []

        bpa_html = get_bpa_html()
        for zone in ANDORRA_ZONES:
            # Check if BPA for selected date already exists.
            zone_id = ates_utils.refresh_zone_ids()[ANDORRA_ZONES[zone]]
            if ates_utils.bpa_exists(date=date, zone_id=zone_id):
                print(f"Avalanche danger level already exists for the date '{date}' and zone '{ANDORRA_ZONES[zone]}'")
                continue

            img = bpa_html.body.find("div", attrs={"class": f"{zone}"})
            danger_ok = False
            for a in img.find_all("a"):
                img_icon = a.find('img', src=re.compile(r'/images/ico-neu/ico-risque/*'))
                if img_icon:
                    danger_lvls = img_icon["src"].split("/")[-1].split(".")[0]
                    # Get max level if has multiple levels
                    danger_lvls = [int(i) for i in danger_lvls.split() if i.isdigit()]
                    danger_lvl = max(danger_lvls)
                    print(f"Danger level for '{ANDORRA_ZONES[zone]}' zone: {danger_lvl}")
                    levels_from_bpa.append({
                        "zone_id": zone_id,
                        "zone_name": ANDORRA_ZONES[zone],
                        "level": danger_lvl
                    })
                    danger_ok = True
            if not danger_ok:
                print(f"WARNING: Couldn't determine danger level for zone '{ANDORRA_ZONES[zone]}'")
                print("This zone will not be updated on database.")

        return levels_from_bpa
    except Exception as exc:
        raise Exception(f"Couldn't get danger levels from BPA report. ERROR: {exc}")


def get_bpa_publication_date(bpa_file: str) -> str:
    '''
    Return BPA report publication date.

    :param bpa_file: Full path to PDF file.
    '''

    print("Obtaining report date from BPA report...")
    with fitz.open(bpa_file) as f:
        for page in f:
            p_text = page.get_text()
            if "Elaborat el" in p_text:
                bpa_dates = re.findall(r'\d{2}/\d{2}/\d{4}', p_text)
                break

    if bpa_dates:
        # Return earliest date
        return datetime.strptime(min(bpa_dates), "%d/%m/%Y").strftime("%Y-%m-%d")
    else:
        raise Exception("Couldn't determine BPA report date.")


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
    print(f"Zone: Andorra Pyrenees")
    print(f"Date: {today}")

    # Get danger level
    pdf_bpa = f"/tmp/andorra_bpa_{today}.pdf"
    report_url = get_download_link()
    get_report(download_link=report_url, output_file=pdf_bpa)
    
    # Only compute danger level if selected date is equals than BPA report date.
    if today == get_bpa_publication_date(bpa_file=pdf_bpa):
        danger_lvls = get_bpa_danger_levels(date=today)

        # Insert data to DB
        for zone in danger_lvls:
            ates_utils.save_data(
                zone_name=zone["zone_name"],
                zone_id=zone["zone_id"],
                date=today,
                level=zone["level"]
            )
    else:
        print(f"BPA report for Andorra zones are not available yet for selected date '{today}'.")

    # End
    print("Total time elapsed: {:.2f} seconds.".format(time.time() - start_time))
    print("Bye.")


# Trigger
main()
