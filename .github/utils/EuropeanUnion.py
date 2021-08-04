# Standard
import argparse
import os
import sys

import pandas as pd

# =============================================================================
# Constants
# =============================================================================
COUNTRIES = [
    "Austria",
    "Belgium",
    "Bulgaria",
    "Croatia",
    "Cyprus",
    "Czechia",
    "Denmark",
    "Estonia",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Hungary",
    "Ireland",
    "Italy",
    "Latvia",
    "Lithuania",
    "Luxembourg",
    "Malta",
    "Netherlands",
    "Poland",
    "Portugal",
    "Romania",
    "Slovakia",
    "Slovenia",
    "Spain",
    "Sweden"]

# =============================================================================
# Arguments
# =============================================================================
description = "Publish vaccination data for a country."
parser = argparse.ArgumentParser(description=description)

arg = "--data"
parser.add_argument(arg)

arg = "--output"
parser.add_argument(arg)

args = sys.argv[1:]
args = parser.parse_args(args)

# Rename the command line arguments for easier reference
path = args.data
output = args.output

# =============================================================================
# Functions
# =============================================================================


# =============================================================================
# Main
# =============================================================================

columns=["date", "total_vaccinations", "people_vaccinated", "people_fully_vaccinated"]
eu_data = pd.DataFrame(columns = columns)

for country in COUNTRIES:
    path_file = os.path.join(path, country.replace(" ", "") + ".csv")
    data = pd.read_csv(path_file, usecols = columns, index_col="date")
    if eu_data.empty:
        eu_data = data
    else:
        #eu_data = data.reindex_like(eu_data).fillna(0) + eu_data.fillna(0)
        data = data.reindex_like(eu_data).fillna(method="ffill")
        print("DATA")
        print(data)
        print("EU_DATA")
        print(eu_data)
        eu_data = eu_data.add(data, fill_value=0)
