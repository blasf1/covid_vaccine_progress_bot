#!/bin/bash
set -e

SOURCE=$(python $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/source.py $COUNTRY)

# Move to the directory with the vaccination scripts
# since the destination files are relative from here
cd $SCRIPTS

mkdir $GITHUB_WORKSPACE/covid-19-data/scripts/scripts/vaccinations/src/vax/batch/vax/
mkdir $GITHUB_WORKSPACE/covid-19-data/scripts/scripts/vaccinations/src/vax/incremental/vax/

cp -r $GITHUB_WORKSPACE/covid-19-data/scripts/scripts/vaccinations/src/vax/utils $GITHUB_WORKSPACE/covid-19-data/scripts/scripts/vaccinations/src/vax/batch/vax/
cp -r $GITHUB_WORKSPACE/covid-19-data/scripts/scripts/vaccinations/src/vax/utils $GITHUB_WORKSPACE/covid-19-data/scripts/scripts/vaccinations/src/vax/incremental/vax/

cat $GREECE_TOKEN > $GITHUB_WORKSPACE/covid-19-data/scripts/scripts/vaccinations/src/vax/batch/vax_dataset_config.json

python $(ls -d src/vax/*/$SOURCE.py)
