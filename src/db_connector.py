#!/usr/bin/python3
############################################################
#
#   ATESMaps - BPA Extractors - ARAN
#
#   Python script that obtains data of avalanche  bulletin
#   generated and managed by Lauegi & Conselh d'Aran.
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
from typing import Dict
import psycopg2
import credentials as creds


def db_conn():
    '''
    Return opened session with database.
    '''

    try:
        return psycopg2.connect(
            host=creds.DB_HOST,
            database=creds.DB_NAME,
            user=creds.DB_USER,
            password=creds.DB_PASSWD
        )
    except Exception as exc:
        raise Exception("Couldn't connect to database.") from exc


def update_data(query: str) -> bool:
    '''
    Do an SQL insert/update to database. Used for save BPA data.

    :param query: String with SQL insert query with record.
    '''

    try:
        db = db_conn()
        with db.cursor() as cursor:
            cursor.execute(query)
        db.commit()
    except Exception as exc:
        raise Exception("An error ocurred executing SQL select statement.") from exc


def select_data(query: str) -> Dict:
    '''
    Do an SQL query to database and return list with
    records.

    :param query: String with SQL select query to do.
    '''

    try:
        db = db_conn()
        with db.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
    except Exception as exc:
        raise Exception("An error ocurred executing SQL select statement.") from exc

