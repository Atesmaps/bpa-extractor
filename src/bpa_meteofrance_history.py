#!/usr/bin/python3
###############################################################################
#
#   ATESMaps - BPA Extractors - MeteoFrance
#
#   Python script that obtains data of avalanche bulletin
#   generated and managed by MeteoFrance.
#
#   +INFO: https://donneespubliques.meteofrance.fr/?fond=produit&id_produit=265&id_rubrique=50
#
#   Collaborators:
#       * Nil Torrano: <ntorrano@atesmaps.org>
#       * Atesmaps Team: <info@atesmaps.org>
#
#   November 2021
#
###############################################################################
from typing import Optional
from PyPDF2 import PdfFileReader
import time
import requests
from datetime import datetime
import atesmaps_utilities as ates_utils
import bpa_urls

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

############ CONFIGURATION ################
# Set custom date with format YYYY-MM-DD or leave blank
# to use default.
# Default: Today
CUSTOM_DATE = ""

FRANCE_PYRENEES_ZONES = {
    "PAYS-BASQUE": "Pays Basque",
    "ASPE-OSSAU": "Aspe-Ossau",
    "HAUTE-BIGORRE": "Haute-Bigorre",
    "AURE-LOURON": "Aure-Louron",
    "LUCHONNAIS": "Luchonnais",
    "COUSERANS": "Couserans",
    "HAUTE-ARIEGE": "Haute-Ariege",
    "ORLU__ST_BARTHELEMY": "Orlu St Barthelemy",
    "CAPCIR-PUYMORENS": "Capcir-Puymorens",
    "CERDAGNE-CANIGOU": "Cerdagne-Canigou"
}

# Selenium variables
WAIT_TIME = 20  # Seconds wait (timeout)


def accept_cookies_policy(driver):
    '''
    Accpet coolies policy if it's needed.

    :param driver: Selenium Webdriver.
    '''

    # Accept cookies policy if it's needed
    try:
        cookiesAcceptElement = WebDriverWait(driver, WAIT_TIME).until(
            EC.element_to_be_clickable((By.ID, 'cookieChoiceDismiss')))
        cookiesAcceptElement.click()
        print('The cookies policy must be accepted. Policy will be accepted below.')
    except:
        print('Acceptance of the cookie policy is not required or has already been accepted previously.')


def get_report(download_link: str, output_file: str) -> bool:
    '''
    Do an API call and return BPA data from provided URL.

    :param download_link: The full URL to download endpoint.
    :param output_file: String with the full path for the new PDF file.
    '''

    try:
        print(f"Downloading Meteofrance BPA report using this URL: {download_link}")
        response = requests.get(
            url=download_link
        )
        if response.status_code != 200:
            print(f"Avalanche report for zone Meteofrance using download link {download_link} is not available.")
            return False
        # Download report as PDF
        with open(output_file, "wb") as f:
            f.write(response.content)
        return True
    except Exception as exc:
        print(f"Couldn't download BPA report. ERROR: {exc}")
        return False


def get_download_link(driver, zone_name: str, date: str, extension: str):
    '''
    Return available download link for BPA report in selected format.

    :param driver: Selenium Webdriver.
    :param zone_name: The name of zone that match with selectable items from
                      Metefrance website. See "FRANCE_PYRENEES_ZONES" variable.
    :param date: BPA report date in format YYYY-MM-DD.
    :param extension: Select the type of downloaded file.
    '''

    # Click section for download selected BPA report
    DownloadReportSectionElement = WebDriverWait(driver, WAIT_TIME).until(
        EC.element_to_be_clickable((By.XPATH, "//h3[text()='Téléchargement']")))
    DownloadReportSectionElement.click()

    # Insert date
    inputBPADateElement = driver.find_element(By.ID, "datepicker")
    inputBPADateElement.clear()
    inputBPADateElement.send_keys(date.replace("-",""))  # Date in format YYYYMMDD
    inputBPADateElement.send_keys(Keys.TAB)

    # Select zone
    time.sleep(2)  # Wait for onchange JS action
    zoneSelectorElement = driver.find_element(By.NAME, "station").click()
    zoneSelectorElement = Select(driver.find_element(By.NAME, "station"))
    zoneSelectorElement.select_by_value(zone_name)

    # Select extension
    time.sleep(2)
    extensionSelectorElement = driver.find_element(By.NAME, "extension").click()
    extensionSelectorElement = Select(driver.find_element(By.NAME, "extension"))
    extensionSelectorElement.select_by_value(extension)

    # Click download button
    time.sleep(1)
    driver.find_element(By.XPATH, "//input[@value='Télécharger' and @type='submit']").click()
    time.sleep(10)

    return driver.current_url


def danger_level_from_bpa(bpa_file: str) -> int:
    '''
    Return avalanche danger level from BPA report.

    :param bpa_file: PDF file path with BPA report.
    '''

    # Parse BPA in PDF format.
    # with open(bpa_file, 'rb') as f:
    #     reader = PdfFileReader(f)
    #     print(reader.getNumPages())
    #     for page in range(reader.getNumPages()):
    #         print(f)
    #         contents = reader.getPage(page)
    #         text = contents.extractText()
    #         print(text)
    #         danger_levels = []
    #         zone = []
    #         for elem in text:
    #             print("###############")
    #             print(elem)
    #             # zone += [zone for zone in ICGC_ZONES if zone.replace(" ","") == elem.replace(" ","")]
    #             # danger_levels += [level for level in AVALANCHE_LEVELS if level in elem]

    # text = textract.process(bpa_file)
    # for elem in text.split("\n"):
    #     print(elem)

    import fitz  # this is pymupdf

    with fitz.open(bpa_file) as doc:
        text = ""
        print(doc[0].getImageList())
        for page in doc:
            text += page.getText()

    # print(text)


def get_danger_level_by_zone(driver, zone_name: str, date: str, extension: str="pdf"):
    '''
    Return dangel level for each zone and date selected.

    :param driver: Selenium Webdriver.
    :param zone_name: The name of zone that match with selectable items from
                      Metefrance website. See "FRANCE_PYRENEES_ZONES" variable.
    :param date: BPA report date in format YYYY-MM-DD.
    :param extension: Select the type of downloaded file. Default: PDF
    '''

    # BPA filename
    bpa_file = f"/tmp/meteofrance/bpa_report_{zone_name}_{date}.{extension}"

    # Get Zone ID from name
    zone_id = ates_utils.refresh_zone_ids()[FRANCE_PYRENEES_ZONES[zone_name]]

    # Check if BPA for selected date already exists.
    if ates_utils.bpa_exists(date=date, zone_id=zone_id):
        print(f"Avalanche danger level already exists for the date '{date}' and zone {zone_name}")

    # # Get download link
    # download_url = get_download_link(
    #     driver=driver,
    #     zone_name=zone_name,
    #     date=date,
    #     extension=extension
    # )

    # # Download BPA
    # get_report(
    #     download_link=download_url,
    #     output_file=bpa_file
    # )

    # Get danger level from downloaded BPA report
    danger_level = danger_level_from_bpa(bpa_file=bpa_file)

    # print(f"Danger level for '{zone_name}' zone: {danger_level}")
    # danger_levels.append({
    #     "zone_name": zone_name,
    #     "zone_id": zone_id,
    #     "danger_level": danger_level,
    #     "bpa_date": report_date
    #     })

    # return danger_levels


def main():
    '''
    Fetch avalanche danger level by zone from Meteo France BPA.
    You must set METEOFRANCE_ZONE_POS variable with each zone coordinates.
    '''

    # Init
    start_time = time.time()
    print("** ATESMaps Avalanche Report Extractor **")

    # Today date in format YYYY-MM-DD
    if CUSTOM_DATE:
        today = CUSTOM_DATE
    else:
        today = datetime.today().strftime("%Y-%m-%d")

    print(f"Updating avalanche danger level...")
    print(f"Zone: MeteoFrance - Pyrenees Français")
    print(f"Date: {today}")

    # Open the avalanche report URL using Firefox in headless mode
    firefox_options = Options()
    firefox_options.headless = False
    # firefox_options.set_preference('profile', "../resources/FirefoxProfile")
    driver = webdriver.Firefox(options=firefox_options)
    driver.get(bpa_urls.BPA_METEOFRANCE_HISTORY_URL)

    # Manage cookies policy pop-up
    accept_cookies_policy(driver=driver)

    # Fetch danger levels from Meteofrance web
    for zone in FRANCE_PYRENEES_ZONES:
        danger_lvls = get_danger_level_by_zone(driver=driver, zone_name=zone, date=today)
        # for zone in danger_lvls:
        #     ates_utils.save_data(
        #         zone_name=zone["zone_name"],
        #         zone_id=zone["zone_id"],
        #         level=zone["danger_level"],
        #         date=zone["bpa_date"]
        #     )

    # Close browser
    driver.quit()

    # End
    print("Total time elapsed: {:.2f} seconds.".format(time.time() - start_time))
    print("Bye.")


# Trigger
main()
