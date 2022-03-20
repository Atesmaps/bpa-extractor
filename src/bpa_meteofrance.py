#!/usr/bin/python3
###############################################################################
#
#   ATESMaps - BPA Extractors - METEOFRANCE
#
#   Python script that obtains data of avalanche bulletin
#   generated and managed by MeteoFrance.
#
#   +INFO: https://meteofrance.com/meteo-montagne/pyrenees/risques-avalanche
#
#   Collaborators:
#       * Nil Torrano: <ntorrano@atesmaps.org>
#       * Atesmaps Team: <info@atesmaps.org>
#
#   November 2021
#
###############################################################################
from typing import Optional
import sys
import time
import re
from datetime import datetime
import atesmaps_utilities as ates_utils
import bpa_urls

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

############ CONFIGURATION ################

# METEOFRANCE - Zone matrix positions
METEOFRANCE_ZONE_POS = {
    "Pays Basque": [202, 228],
    "Aspe-Ossau": [265, 247],
    "Haute-Bigorre": [334, 257],
    "Aure-Louron": [385,265],
    "Luchonnais": [408, 269],
    "Couserans": [478, 267],
    "Haute-Ariege": [540, 290],
    "Orlu St Barthelemy": [571, 283],
    "Capcir-Puymorens": [600, 311],
    "Cerdagne-Canigou": [631,334]
}

# Selenium variables
WAIT_TIME = 20  # Seconds wait (timeout)


def get_zone_from_2d_matrix(x: int, y: int) -> Optional[str]:
    '''
    Return zone name for provided coordinates (X,Y)
    '''

    for zone in METEOFRANCE_ZONE_POS:
        if METEOFRANCE_ZONE_POS[zone] == [x, y]:
            return zone

    return


def accept_cookies_policy(driver):
    '''
    Accpet coolies policy if it's needed.

    :param driver: Selenium Webdriver.
    '''

    # Accept cookies policy if it's needed
    try:
        cookiesAcceptElement = WebDriverWait(driver, WAIT_TIME).until(
            EC.element_to_be_clickable((By.ID, 'didomi-notice-agree-button')))
        cookiesAcceptElement.click()
        print('The cookies policy must be accepted. Policy will be accepted below.')
    except:
        print('Acceptance of the cookie policy is not required or has already been accepted previously.')


def get_danger_level_by_zone(driver, date: str):
    '''
    Return dangel level for each zone and date selected.

    :param driver: Selenium Webdriver.
    :param date: BPA report date in format YYYY-MM-DD.
    '''

    # Danger levels
    danger_levels = []

    # Find the avalanche risk icons within the map
    avalancheIconElements = driver.find_elements(By.CLASS_NAME, "iconMap")
    for area in avalancheIconElements:
        # Get position in map and avalanche icon value
        css_pos_matrix = area.value_of_css_property("transform")
        pos_matrix = css_pos_matrix[css_pos_matrix.find("(")+1:css_pos_matrix.find(")")].replace(" ", "").split(",")[-2:]
        pos_matrix = [int(i) for i in pos_matrix]
        icon = area.find_elements(By.XPATH, ".//img")
        for src in icon:
            url = src.get_attribute('src').split('/')[-1]
            danger_level = url.split('_')[0]

        zone_name = get_zone_from_2d_matrix(x=pos_matrix[0], y=pos_matrix[1])
        if not zone_name:
            print(f"Skipping zone with coordinates x:{pos_matrix[0]} and y:{pos_matrix[1]} because is not declared.")
            continue

        # Get Zone ID from name
        zone_id = ates_utils.refresh_zone_ids()[zone_name]

        print(f"Danger level for '{zone_name}' zone: {danger_level}")
        danger_levels.append({
            "zone_name": zone_name,
            "zone_id": zone_id,
            "danger_level": danger_level,
            "bpa_date": date
        })

    return danger_levels


def main():
    '''
    Fetch avalanche danger level by zone from Meteo France BPA.
    You must set METEOFRANCE_ZONE_POS variable with each zone coordinates.
    '''

    # Init
    start_time = time.time()
    print("** ATESMaps Avalanche Report Extractor **")

    # Today date in format YYYY-MM-DD
    today = datetime.today().strftime("%Y-%m-%d")

    print(f"Updating avalanche danger level...")
    print(f"Zone: MeteoFrance - Pyrenees Français")
    print(f"Date: {today}")

    # Open the avalanche report URL using Firefox in headless mode
    firefox_options = Options()
    firefox_options.headless = True
    driver = webdriver.Firefox(options=firefox_options)
    driver.get(bpa_urls.BPA_METEOFRANCE_URL)

    # Manage cookies policy pop-up
    accept_cookies_policy(driver=driver)

    # Fetch danger levels from Meteofrance web
    danger_lvls = get_danger_level_by_zone(driver=driver, date=today)
    for zone in danger_lvls:
        ates_utils.save_data(
            zone_name=zone["zone_name"],
            zone_id=zone["zone_id"],
            level=zone["danger_level"],
            date=zone["bpa_date"]
        )

    # Close browser
    driver.quit()

    # End
    print("Total time elapsed: {:.2f} seconds.".format(time.time() - start_time))
    print("Bye.")


# Trigger
main()
