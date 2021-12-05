#!/bin/bash
#########################################################
#
#    Run avalanche BPA extractors using docker image.
#
#   Set your environment variables values.
#
#    Collaborators:
#     * Nil Torrano: <ntorrano@atesmaps.org>
#     * Atesmaps Team: <info@atesmaps.org>
#
#    December 2021
#
#########################################################

# Log filename
LOG_FILE=atesmaps_bpa_extractor_`date +%Y%m%d`.log

# Set log trace
echo -e "\n\n########### ATESMaps BPA Extractor - $(date +%Y-%m-%d) $(date +%H:%M:%S) ###########" >> ${LOG_FILE}

# Run docker image
docker run \
    -e "DB_HOST=YOUR_DB_HOST" \
    -e "DB_NAME=YOUR_DB_NAME" \
    -e "DB_USER=YOUR_DB_USER" \
    -e "DB_PASSWD=YOUR_DB_PASSWORD" \
    --rm \
    --name atesmaps-bpa-extractor \
    atesmaps/atesmaps-bpa-extractor:latest >> ${LOG_FILE} 2>&1

# End log trace
echo -e "\n\n#########################################################################" >> ${LOG_FILE}

exit 0
