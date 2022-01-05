#!/bin/bash

set -e

# SOURCE=$(python $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/source.py $COUNTRY)

# Move to the directory with the vaccination scripts to install the package
cd $SCRIPTS

pip install .

cp $GITHUB_WORKSPACE/covid-19-data/scripts/src/cowidev/vax/_static/queries/* /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/_static/queries/ ;
cp $GITHUB_WORKSPACE/covid-19-data/scripts/src/cowidev/vax/utils/orgs/* /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/utils/orgs/ ;
cp $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/get_data.py /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/cmd/get_data.py ;
cat $GITHUB_WORKSPACE/covid-19-data/scripts/src/cowidev/vax/cmd/get_data.py ;
python $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/update.py