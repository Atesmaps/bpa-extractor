#!/bin/bash
#################################################################
#
#   ATESMaps - BPA Extractors - Dockerfile
#
#   Collaborators:
#       * Nil Torrano: <ntorrano@atesmaps.org>
#       * Atesmaps Team: <info@atesmaps.org>
#
#   November 2021
#
#################################################################
FROM python:3.13
LABEL maintainer="ntorrano@atesmaps.org"

WORKDIR /

# Install Firefox
RUN apt-get update \
    && apt-get dist-upgrade -y \
    && apt-get install -y \
    wget \
    firefox-esr \
    locales

# Install geckodriver (selenium extractors)
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.35.0/geckodriver-v0.35.0-linux64.tar.gz
RUN tar -xvzf geckodriver-v0.35.0-linux64.tar.gz
RUN chmod +x geckodriver 
RUN mv geckodriver /usr/local/bin/

# Install Catalan Locale
RUN echo "ca_ES.UTF-8 UTF-8" | tee -a /etc/locale.gen
RUN locale-gen
RUN locale -a

# Install requirements (Python libraries)
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src ./src

# Copy entrypoint
COPY resources/docker/entrypoint.sh entrypoint.sh

# Run AWS Inventory
ENTRYPOINT ["./entrypoint.sh"]
