#!/bin/bash

set -e

# Update in a different script to stay in the current working directory
bash $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/update.bash

python $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/publish.py --country $COUNTRY \
                                                                             --data $SCRIPTS/output \
                                                                             --output $OUTPUT \
                                                                             --population $POPULATION
