# BPA Extractor

Tool for extract avalanche danger levels from Pyrenees zones.

### Usage

Run using [docker image]("https://hub.docker.com/repository/docker/atesmaps/atesmaps-bpa-extractor") from Docker HUB.

```sh
docker run \
    -e "DB_HOST=YOUR_DB_HOST" \
    -e "DB_NAME=YOUR_DB_NAME" \
    -e "DB_USER=YOUR_DB_USER" \
    -e "DB_PASSWD=YOUR_DB_PASSWORD" \
    --rm \
    --name atesmaps-bpa-extractor \
    atesmaps/atesmaps-bpa-extractor:latest >> ${LOG_FILE} 2>&1
```
