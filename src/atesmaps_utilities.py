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
import db_connector as db


def refresh_zone_ids():
    '''
    Return dictionary with relation between zone
    and zone ID.
    '''

    response = db.select_data("SELECT zona, codi_zona FROM limitszonesbpa")
    zone_ids = {}
    for rec in response:
        zone_ids[rec[0]] = rec[1]
    
    return zone_ids
