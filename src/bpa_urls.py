#!/usr/bin/python3
############################################################
#
#   ATESMaps - BPA Extractors - BPA URLs
#
#   Python with URLs used for fetch BPA data collected
#   from the different areas.
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

##### ARAN #####
# Date should be provided in format YYYY-MM-DD
BPA_ARAN_URL = "https://conselharan2.cyberneticos.net/simple_local/{date}/ES-CT-L_ca.html"
BPA_ARAN_URL_2 = "https://conselharan2.cyberneticos.net/albina_files_local/{date}/{date}_es_CAAMLv6.xml"

##### ICGC #####
# Date should be provided in format YYYY-MM-DD
BPA_ICGC_URL = "https://bpa.icgc.cat/butlletigenerator/bpadoc/bpa_{date}_cat.pdf"
