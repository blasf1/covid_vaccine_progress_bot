#!/bin/bash

set -e

python $GITHUB_WORKSPACE/covid_vaccine_progress_bot/.github/utils/publish.py --country $COUNTRY \
                                                                             --data $SCRIPTS/output \
                                                                             --data-unsupported $DATA_UNSUPPORTED \
                                                                             --output $OUTPUT \
                                                                             --population $POPULATION
