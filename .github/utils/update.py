# =============================================================================
# Imports
# =============================================================================
import argparse
import os
import sys

from vax.cmd._config import get_config
from vax.cmd import main_get_data
from vax.utils.paths import Paths
from vax.cmd.get_data import country_to_module

# =============================================================================
# Constants
# =============================================================================
SKIPPED_COUNTRIES = ['australia',
                     'bangladesh',
                     'canada',
                     'chile',
                     'ecuador',
                     'gambia',
                     'hong_kong',
                     'israel',
                     'jersey',
                     'new_zealand',
                     'peru',
                     'saudi_arabia',
                     'spc',
                     'switzerland',
                     'trinidad_and_tobago',
                     'united_kingdom',
                     'uruguay',
                     'argentina',
                     'aruba',
                     'azerbaijan',
                     'bahrain',
                     'bolivia',
                     'brazil',
                     'cayman_islands',
                     'colombia',
                     'costa_rica',
                     'curacao',
                     'dominican_republic',
                     'el_salvador',
                     'equatorial_guinea',
                     'faeroe_islands',
                     'ghana',
                     'greenland',
                     'guatemala',
                     'iceland',
                     'india',
                     'isle_of_man',
                     'japan',
                     'kazakhstan',
                     'lebanon',
                     'macao',
                     'malaysia',
                     'moldova',
                     'mongolia',
                     'montenegro',
                     'morocco',
                     'nepal',
                     'north_macedonia',
                     'northern_cyprus',
                     'pakistan',
                     'philippines',
                     'qatar',
                     'russia',
                     'saint_lucia',
                     'san_marino',
                     'serbia',
                     'singapore',
                     'south_africa',
                     'south_korea',
                     'sri_lanka',
                     'suriname',
                     'taiwan',
                     'thailand',
                     'turkey',
                     'ukraine',
                     'united_arab_emirates',
                     'united_states',
                     'who']



# =============================================================================
# Arguments
# =============================================================================
description = "Update data for all countries."
parser = argparse.ArgumentParser(description=description)

arg = "--directory"
default = os.environ.get("OWID_COVID_PROJECT_DIR")
parser.add_argument(arg, default=default)

arg = "--greece-api-token"
default = os.environ.get("GREECE_SECRET")
parser.add_argument(arg, default=default)

args = sys.argv[1:]
args = parser.parse_args(args)

project_dir = args.directory
greece_api_token = args.greece_api_token

# =============================================================================
# Main
# =============================================================================
paths = Paths(project_dir)

main_get_data(paths, n_jobs=4, greece_api_token=greece_api_token, skip_countries=SKIPPED_COUNTRIES)
