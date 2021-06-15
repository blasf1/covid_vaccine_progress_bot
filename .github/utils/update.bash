#!/bin/bash

set -e

COUNTRIES="Austria
Belgium
Bulgaria
Croatia
Cyprus
Czechia
Denmark
Estonia
Finland
France
Germany
Greece
Hungary
Ireland
Italy
Latvia
Lithuania
Luxembourg
Malta
Netherlands
Poland
Portugal
Romania
Slovakia
Slovenia
Spain
Sweden"

# SOURCE=$(python $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/source.py $COUNTRY)

# Move to the directory with the vaccination scripts to install the package
cd $SCRIPTS

pip install .

cd

cp -r $GITHUB_WORKSPACE/covid-19-data/scripts/scripts/vaccinations/src/vax/_static /opt/hostedtoolcache/Python/3.9.5/x64/lib/python3.9/site-packages/vax/

for f in $COUNTRIES
do
    cp $GITHUB_WORKSPACE/covid-19-data/scripts/scripts/vaccinations/output/$f.csv $GITHUB_WORKSPACE/covid_vaccine_progress_bot/output/
done

python $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/update.py