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

##### METEOFRANCE #####
# Avalanche reports URL
BPA_METEOFRANCE_URL = "https://meteofrance.com/meteo-montagne/pyrenees/risques-avalanche"
BPA_METEOFRANCE_HISTORY_URL = "https://donneespubliques.meteofrance.fr/?fond=produit&id_produit=265&id_rubrique=50"

##### ANDORRA #####
BPA_ANDORRA_URL = "http://www.meteo.ad/estatneu"

##### ARAGON #####
BPA_ARAGON_NAV_URL = "http://www.aemet.es/documentos/es/eltiempo/prediccion/montana/boletin_peligro_aludes/BPA_Pirineo_Nav_Ara.pdf"
