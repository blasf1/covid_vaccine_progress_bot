#!/bin/bash

set -e

# SOURCE=$(python $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/source.py $COUNTRY)

# Move to the directory with the vaccination scripts to install the package
cd $SCRIPTS

pip install .

cp $GITHUB_WORKSPACE/covid-19-data/scripts/src/cowidev/vax/_static/queries/* /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/_static/queries/ ;
cp $GITHUB_WORKSPACE/covid-19-data/scripts/src/cowidev/vax/utils/orgs/* /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/utils/orgs/ ;
cp -r $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/cowidev_old/* /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/cmd/ ;
rm /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/incremental/colombia.py
rm /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/batch/ecdc.py

python $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/update.py