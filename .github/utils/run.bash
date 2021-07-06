#!/bin/bash

set -e

COUNTRIES=(Austria Belgium Bulgaria Croatia Cyprus Czechia Denmark Estonia Finland France Germany Greece Hungary Italy Latvia Lithuania Luxembourg Malta Netherlands Poland Portugal Romania Slovakia Slovenia Spain Sweden "United Kingdom" "United States")
#Ireland

python $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/publish.py --data $SCRIPTS/output \
                                                                             --data-unsupported $DATA_UNSUPPORTED \
                                                                             --input $INPUT \
                                                                             --output $OUTPUT \
                                                                             --population $POPULATION
for f in "${components[@]}"
do
    cp $GITHUB_WORKSPACE/covid-19-data/scripts/scripts/vaccinations/output/$f.csv $GITHUB_WORKSPACE/covid_vaccine_progress_bot/output/
done