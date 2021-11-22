#!/usr/bin/python3
############################################################
#
#   ATESMaps - BPA Extractors - ATESMaps utilities
#
#   +INFO: https://lauegi.report/
#
#   Collaborators:
#       * Nil Torrano: <ntorrano@atesmaps.org>
#       * Atesmaps Team: <info@atesmaps.org>
#
#   November 2021
#
############################################################
from datetime import datetime
import db_connector as db
import constants as const


def refresh_zone_ids() -> dict:
    '''
    Return dictionary with relation between zone
    and zone ID.
    '''

    q = f"SELECT zona, codi_zona FROM {const.TABLE_BPA}"
    response = db.select_data(query=q)
    zone_ids = {}
    for rec in response:
        zone_ids[rec[0]] = rec[1]
    
    return zone_ids


def bpa_exists(date: str, zone_id: str) -> bool:
    '''
    Check if BPA exists for selected date and zone.

    :param date: the date you want to validate that there is
                 a available BPA. Format: YYYY-MM-DD
    :param zone_id: The code corresponding with the zone that
                    you want to validate.
    '''

    q = f"""SELECT
                id
            FROM
                {const.TABLE_BPA_HISTORY}
            WHERE
                bpa_date = '{date}'
                and zone_id = '{zone_id}'"""

    response = db.select_data(query=q)
    if response:
        return True

    return False


def save_data(zone_name: str, zone_id: str, date: str, level: str) -> None:
    '''
    Save data into database.

    :param zone_name: The name of the zone to save data.
    :param zone_id: The zone code that identifies uniquely zone.
    :param date: The BPA report date in format YYYY-MM-DD.
    :param level: Avalanche danger level as string. Ex: 2
    '''

    # Insert dangel level to BPA table
    print("Updating data to zones information table...")
    q = f"UPDATE {const.TABLE_BPA} SET bpa='{level}' WHERE codi_zona = '{zone_id}'"
    db.update_data(query=q)

    # Insert data into BPA history
    print("Updating data to bpa history table...")
    q = f"INSERT INTO {const.TABLE_BPA_HISTORY} (zone_name, zone_id, created_at, danger_level, bpa_date) " \
        f"VALUES ('{zone_name}', '{zone_id}', '{datetime.now()}', '{level}', '{date}')"
    db.update_data(query=q)
