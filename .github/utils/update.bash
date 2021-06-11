#!/bin/bash

set -e

# SOURCE=$(python $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/source.py $COUNTRY)

# Move to the directory with the vaccination scripts to install the package
cd $SCRIPTS

pip install .

cd

cp -r $GITHUB_WORKSPACE/covid-19-data/scripts/scripts/vaccinations/src/vax/_static /opt/hostedtoolcache/Python/3.9.5/x64/lib/python3.9/site-packages/vax/

echo "ls result"
ls /opt/hostedtoolcache/Python/3.9.5/x64/lib/python3.9/site-packages/vax/_static

python $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/update.py