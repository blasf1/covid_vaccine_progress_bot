# =============================================================================
# Imports
# =============================================================================
# Standard
import argparse
import os
import sys
import glob

import pandas as pd
import json
import numpy as np
import datetime

# =============================================================================
# Constants
# =============================================================================
COUNTRIES = [
    "European Union",
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
    "Sweden",
    #"United Kingdom",
]

# =============================================================================
# Functions
# =============================================================================

def get_population(path, country):
    """Get the population for a country."""
    # Use the country to identify the population data
    index_col = "entity"
    data = pd.read_csv(path, index_col=index_col)

    return data.loc[country]["population"].values[0]


def get_data_hundred_people(data, path):
    """Get the vaccination data per hundred people."""
    # Filter the numerical data to avoid errors
    population = get_population(path, data["location"])
    numeric_columns = data.select_dtypes("number").columns.tolist()

    data[numeric_columns] = data[numeric_columns] * 100 / population

    return data


def read_data(path, path_population):
    """Read the last vaccination data for all countries."""
    files = glob.glob(path + "*.csv")
    def read_csv(file): 
        data = pd.read_csv(file).iloc[[-1]]
        data = get_data_hundred_people(data, path_population)
        return data

    data = pd.concat(map(read_csv, files))
    columns = ["date", "location", "people_vaccinated", "people_fully_vaccinated", "total_vaccinations"]
    data = data[columns]
    
    return data.set_index("location").round(2)

def sort_values_dict(dict, sort_by="people_fully_vaccinated"):
    countries = [country for country in dict]
    values = [dict[country][sort_by] for country in dict]
    index_sorted = np.argsort(-np.array(values))
    return list(np.array(countries)[index_sorted])

def get_dict_vaccination_per_country(df):
    dict_people_vaccinated = {"data": {}}
    for country in COUNTRIES:
        people_vaccinated = df["people_vaccinated"][country]
        people_fully_vaccinated = df["people_fully_vaccinated"][country]
        dict_people_vaccinated["data"][country] = {"people_vaccinated": people_vaccinated,
                                                   "people_fully_vaccinated": people_fully_vaccinated}
    dict_people_vaccinated["countries_sorted"] = sort_values_dict(dict_people_vaccinated["data"])
    dict_people_vaccinated["max_date"] = df.date.max()
    return dict_people_vaccinated

def export_dict_people_vaccinated(data, path):
    file = open(path, "w")
    file.write(json.dumps(data))

def export_csv(data, path):
    path = os.path.join(path, "latest.csv")
    data.to_csv(path)
# =============================================================================
# Arguments
# =============================================================================
description = "Publish vaccination data for a country."
parser = argparse.ArgumentParser(description=description)

arg = "--data"
default = os.environ.get("DATA")
parser.add_argument(arg, default=default)

arg = "--output"
default = os.environ.get("OUTPUT")
parser.add_argument(arg, default=default)

arg = "--csv"
default = os.environ.get("CSV")
parser.add_argument(arg, default=default)

arg = "--population"
default = os.environ.get("POPULATION")
parser.add_argument(arg, default=default)

args = sys.argv[1:]
args = parser.parse_args(args)

# Rename the command line arguments for easier reference
data = args.data
output = args.output
csv = args.csv
population = args.population

# =============================================================================
# Main
# =============================================================================

data = read_data(data, population)
print(data)
export_csv(data, csv)
data = get_dict_vaccination_per_country(data)
export_dict_people_vaccinated(data, output)