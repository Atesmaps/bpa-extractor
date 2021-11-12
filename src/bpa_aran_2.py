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
from typing import Iterable, Dict
from datetime import datetime
import requests
import json
import xmltodict
import bpa_urls


def get_report(date: str=datetime.today().strftime("%Y-%m-%d")) -> Dict:
    '''
    Do an API call and return BPA data in dictionary

    :param date: Select especific date for BPA.
                 Format: YYYY-MM-DD   
    '''

    try:
        print("Downloading Aran BPA report...")
        response = requests.get(
            url=bpa_urls.BPA_ARAN_URL_2.format(date=date)
        )
        report = xmltodict.parse(response.text)

        # Convert OrderedDict to Dict (json) object
        return json.loads(json.dumps(report))
    except Exception as exc:
        raise Exception("Couldn't get Aran BPA.") from exc


def parse_report(bpa: Iterable):
    '''Return specific data filtered from BPA report.'''

    # print(bpa["bulletins"]["bulletin"])
    # for elem in bpa["bulletins"]["bulletin"]:
    #     print()
    bpa_buletin = bpa["bulletins"]["bulletin"]

    response = {
        "publicationTime": bpa["publicationTime"],
        "validStartTime": bpa["validTime"]["startTime"],
        "validEndTime": bpa["validTime"]["endTime"],
    }


def main():
    '''Extract BPA data from Lauegi archive.'''

    report = get_report(date="2020-11-28")
    prsd_report = parse_report(bpa=report)


# Trigger
main()


############## JSON EXAMPLE ####################
# {
#   "@id": "90c923c0-c844-41e8-9ba3-af6b6b61efa1",
#   "@lang": "es",
#   "metaData": {
#     "extFile": [
#       {
#         "type": "dangerRatingMap",
#         "description": "Mapa simplificado de grados de peligro de aludes de la región",
#         "fileReferenceURI": "http://conselharan2.cyberneticos.net//albina_files_local/2020-11-28/2020-11-28_07-00-00/90c923c0-c844-41e8-9ba3-af6b6b61efa1.jpg"
#       },
#       {
#         "type": "website",
#         "description": "Enlace a la región en la web",
#         "fileReferenceURI": "http://conselharan2.cyberneticos.net//bulletin/2020-11-28?region=90c923c0-c844-41e8-9ba3-af6b6b61efa1"
#       }
#     ]
#   },
#   "publicationTime": "2020-11-28T07:00:00Z",
#   "validTime": {
#     "startTime": "2020-11-27T23:00:00Z",
#     "endTime": "2020-11-28T23:00:00Z"
#   },
#   "source": {
#     "operation": {
#       "name": "Avalanche.report",
#       "website": "http://conselharan2.cyberneticos.net/"
#     }
#   },
#   "region": [
#     {
#       "@id": "ES-CT-L-02",
#       "name": "Límite sur de Aran"
#     },
#     {
#       "@id": "ES-CT-L-03",
#       "name": "Vertiente sur de Aran"
#     },
#     {
#       "@id": "ES-CT-L-01",
#       "name": "Norte y centro de Aran"
#     }
#   ],
#   "dangerRating": [
#     {
#       "mainValue": "considerable",
#       "elevation": {
#         "@uom": "m",
#         "lowerBound": "2300"
#       },
#       "artificialDangerRating": "no_rating",
#       "naturalDangerRating": "no_rating"
#     },
#     {
#       "mainValue": "moderate",
#       "elevation": {
#         "@uom": "m",
#         "upperBound": "2300"
#       },
#       "artificialDangerRating": "no_rating",
#       "naturalDangerRating": "no_rating"
#     }
#   ],
#   "avalancheProblem": [
#     {
#       "type": "wind_drifted_snow",
#       "dangerRating": {
#         "aspect": [
#           "N",
#           "W",
#           "NW",
#           "NE"
#         ],
#         "elevation": {
#           "@uom": "m",
#           "lowerBound": "2300"
#         },
#         "mainValue": "considerable",
#         "artificialDangerRating": "considerable",
#         "artificialAvalancheSize": "3",
#         "artificialAvalancheReleaseProbability": "3",
#         "artificialHazardSiteDistribution": "3"
#       }
#     },
#     {
#       "type": "new_snow",
#       "dangerRating": {
#         "aspect": [
#           "N",
#           "S",
#           "W",
#           "NW",
#           "SW",
#           "NE",
#           "SE",
#           "E"
#         ],
#         "mainValue": "moderate",
#         "artificialDangerRating": "moderate",
#         "artificialAvalancheSize": "2",
#         "artificialAvalancheReleaseProbability": "2",
#         "artificialHazardSiteDistribution": "2"
#       }
#     }
#   ],
#   "tendency": {
#     "type": "decreasing",
#     "validTime": {
#       "startTime": "2020-11-28T23:00:00Z",
#       "endTime": "2020-11-29T23:00:00Z"
#     }
#   },
#   "highlights": "Actualmente, el servicio de predicción de aludes tiene información limitada de las zonas de alta montaña. Por lo tanto, debe evaluarse detenidamente el peligro de aludes local.",
#   "avalancheActivityHighlights": "El problema de nieve venteada reciente requiere atenciónn.",
#   "avalancheActivityComment": "A consecuencia de la nieve reciente y el viento, son posibles avalanchas de placa seca, pero en su mayoría pequeñas. Los lugares peligrosos se encuentran sobre todo en laderas cercanas a los cordales umbrías en cotas altas. La unión con la nieve antigua de las placas de viento es localmente desfavorable.",
#   "snowpackStructureComment": "El manto de nieve es inestable del límite oeste por la zonal sur hasta el límite este del Arán.",
#   "tendencyComment": "A consecuencia del aumento de la temperatura diurna, progresivo descenso del peligro de aludes de nieve seca."
# }

###################################################################
