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

python $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/publish.py --data $SCRIPTS/output \
                                                                             --data-unsupported $DATA_UNSUPPORTED \
                                                                             --output $OUTPUT \
                                                                             --population $POPULATION
for f in $COUNTRIES
do
    cp $GITHUB_WORKSPACE/covid-19-data/scripts/scripts/vaccinations/$f $GITHUB_WORKSPACE/covid_vaccine_progress_bot/output/
done