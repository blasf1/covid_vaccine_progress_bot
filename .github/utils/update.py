# =============================================================================
# Imports
# =============================================================================
import argparse
import os
import sys
import pandas as pd

from cowidev.vax.cmd._config import get_config
from cowidev.vax.cmd import main_get_data
from cowidev.vax.utils.paths import Paths
from cowidev.vax.cmd.get_data import country_to_module

# =============================================================================
# Constants
# =============================================================================
SKIPPED_COUNTRIES = ['croatia', 'hungary', 'latvia', 'ecdc',
                     'mexico',
                     'albania',
                     'africacdc',
                     'andorra',
                     'antigua_barbuda',
                     'armenia',
                     'australia',
                     'bangladesh',
                     'canada',
                     'chile',
                     'china',
                     'ecuador',
                     'gambia',
                     'gabon',
                     'georgia',
                     'hong_kong',
                     'israel',
                     'jamaica',
                     'jersey',
                     'jordan',
                     'new_zealand',
                     'peru',
                     'paho',
                     'panama',
                     'saudi_arabia',
                     'spc',
                     'switzerland',
                     'trinidad_and_tobago',
                     'united_kingdom',
                     'uruguay',
                     'vietnam',
                     'argentina',
                     'aruba',
                     'azerbaijan',
                     'bahrain',
                     'bolivia',
                     'brazil',
                     'cayman_islands',
                     'colombia',
                     'costa_rica',
                     'cuba',
                     'curacao',
                     'dominican_republic',
                     'el_salvador',
                     'equatorial_guinea',
                     'faeroe_islands',
                     'ghana',
                     'greenland',
                     'guatemala',
                     'guernsey',
                     'iceland',
                     'india',
                     'indonesia',
                     'isle_of_man',
                     'japan',
                     'kazakhstan',
                     'kyrgyzstan',
                     'lebanon',
                     'macao',
                     'malaysia',
                     'moldova',
                     'monaco',
                     'mongolia',
                     'montenegro',
                     'morocco',
                     'nepal',
                     'north_macedonia',
                     'northern_cyprus',
                     'norway',
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
                     'uzbekistan',
                     'who',
                     'zambia',
                     'kenya',
                     'zimbabwe']


# =============================================================================
# Arguments
# =============================================================================
description = "Update data for all countries."
parser = argparse.ArgumentParser(description=description)

arg = "--directory"
default = os.environ.get("OWID_COVID_PROJECT_DIR")
parser.add_argument(arg, default=default)

args = sys.argv[1:]
args = parser.parse_args(args)

project_dir = args.directory

# =============================================================================
# Main
# =============================================================================
paths = Paths(project_dir)

# greece_api_token=greece_api_token,
main_get_data(paths, n_jobs=4, skip_countries=SKIPPED_COUNTRIES)

path = os.path.join(os.environ.get("OWID_COVID_PROJECT_DIR") +
                    "/scripts/output/vaccinations/main_data/", "Ireland" + ".csv")

index_col = "date"
data = pd.read_csv(path, index_col=index_col)
data = data.sort_values(by="date")
data.to_csv(path)
