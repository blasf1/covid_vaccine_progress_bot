#!/bin/bash

set -e

SOURCE=$(python $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/source.py $COUNTRY)

# Move to the directory with the vaccination scripts to install the package
cd $SCRIPTS

pip install .

python $(ls -d src/vax/*/$SOURCE.py)
