#!/bin/bash

set -e

# SOURCE=$(python $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/source.py $COUNTRY)

# Move to the directory with the vaccination scripts to install the package
cd $SCRIPTS

pip install .

cp $GITHUB_WORKSPACE/covid-19-data/scripts/src/cowidev/vax/_static/queries/* /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/_static/queries/ ;
cp $GITHUB_WORKSPACE/covid-19-data/scripts/src/cowidev/vax/utils/orgs/* /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/utils/orgs/ ;
cp -r $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/cowidev_old/* /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/cmd/ ;
rm /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/incremental/incremental/bulgaria.py
rm /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/incremental/incremental/colombia.py
rm /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/incremental/incremental/moldova.py
rm /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/incremental/incremental/philippines.py
rm /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/incremental/incremental/qatar.py
rm /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/incremental/incremental/sri_lanka.py
rm /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/incremental/incremental/zambia.py
rm /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/incremental/incremental/who.py

rm /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/incremental/bulgaria.py
rm /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/incremental/colombia.py
rm /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/incremental/moldova.py
rm /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/incremental/philippines.py
rm /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/incremental/qatar.py
rm /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/incremental/sri_lanka.py
rm /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/incremental/zambia.py
rm /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/incremental/who.py

rm /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/batch/batch/ecdc.py
rm /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/batch/batch/luxembourg.py
rm /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/batch/batch/romania.py
rm /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/batch/batch/saudi_arabia.py
rm /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/batch/batch/spc.py
rm /opt/hostedtoolcache/Python/3.9.6/x64/lib/python3.9/site-packages/cowidev/vax/batch/batch/united_states.py


python $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/update.py
