#!/bin/bash
set -e

# Update in a different script to stay in the current working directory
bash $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/update.bash

python $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/publish.py --country $COUNTRY \
                                                                             --population $POPULATION \
                                                                             --previous_data $PREVIOUS_DATA \
                                                                             --data $SCRIPTS/output
