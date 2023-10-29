# Atesmaps BPA Extractor

Tool for extract avalanche danger levels from Pyrenees zones.

Available zones:
- **Andorra** - [Andorra National Weather Service](http://www.meteo.ad/estatneu)
- **Aragón & Navarra** - [AEMET](https://www.aemet.es/es/eltiempo/prediccion/montana/boletin_peligro_aludes)
- **Aran** - [Lauegi](https://lauegi.report/)
- **Catalunya** - [ICGC](https://bpa.icgc.cat)
- **France** - [Meteofrance](https://meteofrance.com/meteo-montagne/pyrenees/risques-avalanche)

## Usage

#### Default Date (Today)

Run using [docker image]("https://hub.docker.com/repository/docker/atesmaps/atesmaps-bpa-extractor") from Docker HUB.

```sh
docker run \
    -e "DB_HOST=YOUR_DB_HOST" \
    -e "DB_NAME=YOUR_DB_NAME" \
    -e "DB_USER=YOUR_DB_USER" \
    -e "DB_PASSWD=YOUR_DB_PASSWORD" \
    --rm \
    --name atesmaps-bpa-extractor \
    atesmaps/atesmaps-bpa-extractor:latest >> {PATH_LOG_FILE} 2>&1
```

#### Custom Date

The extractor allows you to select a specific date keeping in mind that if it is not specified this will always be the current day.
To run the extractor with a specific date use the **environment variable** `CUSTOM_DATE` when run docker image:

```sh
docker run \
    -e "DB_HOST=YOUR_DB_HOST" \
    -e "DB_NAME=YOUR_DB_NAME" \
    -e "DB_USER=YOUR_DB_USER" \
    -e "DB_PASSWD=YOUR_DB_PASSWORD" \
	-e "CUSTOM_DATE=1970-01-01"
    --rm \
    --name atesmaps-bpa-extractor \
    atesmaps/atesmaps-bpa-extractor:latest >> {PATH_LOG_FILE} 2>&1
```
**IMPORTANT**: The date format must be **YYYY-MM-DD**.

## Deploy

Deploy BPA extractor service requires [Docker engine](https://docs.docker.com/engine/install/) in your host.

Follow this steps:

1. Create **Log directory** to be able to review the executions.
```bash
mkdir /var/log/atesmaps-bpa-extractor
```

2. Create **Log rotate** configuration file copying the file from repository `resources/deploy/logrotate/atesmaps-bpa-extractor`.
```bash
cp resources/deploy/logrotate/atesmaps-bpa-extractor /etc/logrotate.d/atesmaps-bpa-extractor
```

3. Create **trigger** script in `/opt/atesmaps/scripts` copying the file from repository `resources/deploy/run_bpa_extractor.sh`:
```bash
cp resources/deploy/run_bpa_extractor.sh /opt/atesmaps/scripts/run_bpa_extractor.sh
```

4. Edit trigger script with your **credentials**. You should replace the following fields:
    - YOUR_DB_HOST
    - YOUR_DB_NAME
    - YOUR_DB_USER
    - YOUR_DB_PASSWORD

5. Change trigger script permissions to be able execution:
```bash
chmod +x /opt/atesmaps/scripts/run_bpa_extractor.sh
```

6. Add the following lines to **crontab** to schedule BPA extractor job.
```text
> 0 * * * * /opt/atesmaps/scripts/run_bpa_extractor.sh >/dev/null 2>&1
```

### SQL Resources

Available SQL scripts for deploy BPA extractor are in `resources/SQL`.

- **create_bpa_history_table.sql**: DDL for create new table for danger levels and BPA extracted data.
- **load_history_from_bbdd.sql**: SQL script for extract old data collected in table "bpa_bbdd" and load to new table.

## Build

If you have made changes to the code you will need to generate a new version. Keep in mind that [Docker engine](https://docs.docker.com/engine/install/) is required in your development environment.

1. Change to root project directory where is the Dockerfile.

2. Build docker image.
> docker build . -t atesmaps-bpa-extractor:vX.Y.Z

3. Tag docker image with docker hub user.
> docker tag atesmaps-bpa-extractor:vX.Y.Z atesmaps/atesmaps-bpa-extractor:vX.Y.Z

4. Push docker image to [Docker HUB](https://hub.docker.com/r/atesmaps/atesmaps-bpa-extractor).
> docker push atesmaps/atesmaps-bpa-extractor:vX.Y.Z


## Authors

- **Nil Torrano**: <ntorrano@atesmaps.org>
- **Atesmaps Team**: <info@atesmaps.org>
