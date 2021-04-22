#!/bin/bash

set -e

python $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/publish_manuals.py --country $COUNTRY \
                                                                                --data $DATA\
                                                                                --output $OUTPUT \
                                                                                --population $POPULATION