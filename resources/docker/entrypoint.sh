#!/bin/bash
#################################################################
#
#   ATESMaps - BPA Extractors - Docker Entrypoint
#
#   Bash script that triggers selected BPA report 
#   extractor for selected zone.
#
#   Environment Variables:
#    * CUSTOM_DATE: Select a specific date for BPA report
#                   extractors. Default Today.
#                   Format: YYYY-MM-DD
#    * CUSTOM_ZONE: Selec a specific zone that you want to
#                   extract BPA report and update data.
#                   If it's not set, all zones will be updated.
#                   Zones: andorra,aran,icgc,meteofrance.
#
#   Collaborators:
#       * Nil Torrano: <ntorrano@atesmaps.org>
#       * Atesmaps Team: <info@atesmaps.org>
#
#   November 2021
#
#################################################################

# List with available zones. The name should match with Python filename.
AVAILABLE_ZONES="andorra aran icgc meteofrance aragon_navarra"


printf "\nRunning ATESMaps BPA extractors...\n"

# If no zone is specified, all will be executed.
if [[ -z "${CUSTOM_ZONE}" ]];
	then
        for zone in ${AVAILABLE_ZONES}; do
            printf "\nRunning BPA extractor for zone '${zone}'...\n"
            python3 -u /src/bpa_${zone}.py
        done
	else
  		printf "\nRunning BPA extractor for zone '${CUSTOM_ZONE}'...\n"
  		python3 -u /src/bpa_${CUSTOM_ZONE}.py
fi
