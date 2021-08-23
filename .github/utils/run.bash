#!/bin/bash

set -e

declare -a COUNTRIES=("Austria" \
"Bulgaria" \
"Belgium" \
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


python $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/publish.py --data $DATA \
                                                                             --data-unsupported $DATA_UNSUPPORTED \
                                                                             --input $INPUT \
                                                                             --output $OUTPUT \
                                                                             --population $POPULATION
for f in "${COUNTRIES[@]}";
do
    cp $GITHUB_WORKSPACE/covid-19-data/scripts/output/vaccinations/main_data/$f.csv $GITHUB_WORKSPACE/covid_vaccine_progress_bot/output/
done

cp "$GITHUB_WORKSPACE/covid-19-data/scripts/output/vaccinations/main_data/United Kingdom.csv" $GITHUB_WORKSPACE/covid_vaccine_progress_bot/output/external/UnitedKingdom.csv
cp "$GITHUB_WORKSPACE/covid-19-data/scripts/output/vaccinations/main_data/United States.csv" $GITHUB_WORKSPACE/covid_vaccine_progress_bot/output/external/UnitedStates.csv
cp "$GITHUB_WORKSPACE/covid-19-data/scripts/output/vaccinations/main_data/Norway.csv" $GITHUB_WORKSPACE/covid_vaccine_progress_bot/output/external/Norway.csv
cp "$GITHUB_WORKSPACE/covid-19-data/scripts/output/vaccinations/main_data/Iceland.csv" $GITHUB_WORKSPACE/covid_vaccine_progress_bot/output/external/Iceland.csv
cp "$GITHUB_WORKSPACE/covid-19-data/scripts/output/vaccinations/main_data/Switzerland.csv" $GITHUB_WORKSPACE/covid_vaccine_progress_bot/output/external/Switzerland.csv
