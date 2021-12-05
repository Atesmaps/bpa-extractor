#!/usr/bin/python3
############################################################
#
#   ATESMaps - BPA Extractors - Credentials File
#
#   Use environment variables for set credentials.
#
#   Collaborators:
#       * Nil Torrano: <ntorrano@atesmaps.org>
#       * Atesmaps Team: <info@atesmaps.org>
#
#   November 2021
#
############################################################
from os import getenv

# Database credentials
DB_HOST = getenv("DB_HOST")
DB_NAME = getenv("DB_NAME")
DB_USER = getenv("DB_USER")
DB_PASSWD = getenv("DB_PASSWD")
