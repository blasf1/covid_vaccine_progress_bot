#!/bin/bash
set -e

SOURCE=$(python $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/source.py $COUNTRY)

# Move to the directory with the vaccination scripts
# since the destination files are relative from here
cd $SCRIPTS

python $(ls -d src/vax/*/$SOURCE.py)
