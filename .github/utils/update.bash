#!/bin/bash

set -e

# SOURCE=$(python $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/source.py $COUNTRY)

# Move to the directory with the vaccination scripts to install the package
cd $SCRIPTS

pip install .

cd

ls /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/
cp -r $GITHUB_WORKSPACE/covid-19-data/scripts/scripts/vaccinations/src/vax/_static/queries/ireland-doses.json /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/vax/_static/queries/ireland-doses.json ;
cp -r $GITHUB_WORKSPACE/covid-19-data/scripts/scripts/vaccinations/src/vax/_static/queries/poland-all.json /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/vax/_static/queries/poland-all.json ;

python $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/update.py