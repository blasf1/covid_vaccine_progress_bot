#!/bin/bash

set -e

declare -a COUNTRIES=("Austria" \
"Belgium" \
"Bulgaria" \
"Croatia" \
"Cyprus" \
"Czechia" \
"Denmark" \
"Estonia" \
"Finland" \
"France" \
"Germany" \
"Greece" \
"Hungary" \
"Ireland" \
"Italy" \
"Latvia" \
"Lithuania" \
"Luxembourg" \
"Malta" \
"Netherlands" \
"Poland" \
"Portugal" \
"Romania" \
"Slovakia" \
"Slovenia" \
"Spain" \
"Sweden")


python $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/publish.py --data $SCRIPTS/output \
                                                                             --data-unsupported $DATA_UNSUPPORTED \
                                                                             --input $INPUT \
                                                                             --output $OUTPUT \
                                                                             --population $POPULATION
for f in "${COUNTRIES[@]}";
do
    cp $GITHUB_WORKSPACE/covid-19-data/scripts/scripts/vaccinations/output/$f.csv $GITHUB_WORKSPACE/covid_vaccine_progress_bot/output/
done

cp "$GITHUB_WORKSPACE/covid-19-data/scripts/scripts/vaccinations/output/United Kingdom.csv" $GITHUB_WORKSPACE/covid_vaccine_progress_bot/output/external/UnitedKingdom.csv
cp "$GITHUB_WORKSPACE/covid-19-data/scripts/scripts/vaccinations/output/United States.csv" $GITHUB_WORKSPACE/covid_vaccine_progress_bot/output/external/UnitedStates.csv
cp "$GITHUB_WORKSPACE/covid-19-data/scripts/scripts/vaccinations/output/Norway.csv" $GITHUB_WORKSPACE/covid_vaccine_progress_bot/output/external/Norway.csv
cp "$GITHUB_WORKSPACE/covid-19-data/scripts/scripts/vaccinations/output/Iceland.csv" $GITHUB_WORKSPACE/covid_vaccine_progress_bot/output/external/Iceland.csv
cp "$GITHUB_WORKSPACE/covid-19-data/scripts/scripts/vaccinations/output/Switzerland.csv" $GITHUB_WORKSPACE/covid_vaccine_progress_bot/output/external/Switzerland.csv