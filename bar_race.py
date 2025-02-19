"""Publish the bar race in Twitter."""
# Malta: grey
# Spain: #f2b701
# Germany: black
# European Union: blue
# Denmark: red
# Italy: green
# Sweden: #5799f4
# Latvia: brown
# Netherlands: #e68310
# Romania: #7f3c8d
# Luxembourg: #66c5cc
# France:#cf1c90
# Bulgaria: #80ba5a
# Portugal: #11a579
# Croatia: #4b4b8f
# Finland: #c7c7c7
# Austria: #cc503e
# Belgium: #D7BE69
# Estonia: #5f4690
# Cyprus: #b2df8a
# Ireland: #bf5b17
# Greece: #0D5EAF
# Hungary: #6c9d7b
# Poland: #555353
# Czechia: #11437e
# Lithuania: #73af48

# =============================================================================
# Imports
# =============================================================================
# Standard
import argparse
import os
import sys

import pandas as pd
import datetime
import numpy as np

# =============================================================================
# Constants
# =============================================================================

# Map the country name to the country flag
FLAGS = {
    "European Union": "EU",
    "Austria": "AT",
    "Belgium": "BE",
    "Bulgaria": "BG",
    "Croatia": "HR",
    "Cyprus": "CY",
    "Czechia": "CZ",
    "Denmark": "DK",
    "Estonia": "EE",
    "Finland": "FI",
    "France": "FR",
    "Germany": "DE",
    "Greece": "GR",
    "Hungary": "HU",
    "Ireland": "IE",
    "Italy": "IT",
    "Latvia": "LV",
    "Lithuania": "LT",
    "Luxembourg": "LU",
    "Malta": "MT",
    "Netherlands": "NL",
    "Poland": "PL",
    "Portugal": "PT",
    "Romania": "RO",
    "Slovakia": "SK",
    "Slovenia": "SI",
    "Spain": "ES",
    "Sweden": "SE"}

EXTERNAL = {
    "Norway": "NO",
    "Iceland": "IS",
    "United Kingdom": "UK",
    "United States": "US"}


# =============================================================================
# Functions
# =============================================================================

def get_population(path, country):
    """Get the population for a country."""
    # Use the country to identify the population data
    index_col = "entity"
    data = pd.read_csv(path, index_col=index_col)
    
    return data.loc[country]["population"]


def get_data_hundred_people(data, population_path, country):
    """Get the vaccination data per hundred people."""
    # Filter the numerical data to avoid errors
    population = get_population(population_path, country)
    numeric_columns = data.select_dtypes("number").columns.tolist()

    data[numeric_columns] = data[numeric_columns] * 100 / population

    return data

def get_arranged_data(path, non_eu_path, parameter, population_path):
    """Read the last vaccination data for all countries."""
    #files = glob.glob(path + "*.csv")
    data = pd.DataFrame(columns = FLAGS.keys())
    #data.set_index(inplace = true)
    for country in FLAGS.keys():
        path_country = os.path.join(path + country.replace(" ", "") + ".csv")
        data_country = get_data_hundred_people(pd.read_csv(path_country, index_col="date"), population_path, country)
        data[country] = data_country[parameter]
        data.reindex_like(data_country)

    for country in EXTERNAL.keys():
        path_country = os.path.join(non_eu_path + country.replace(" ", "") + ".csv")
        data_country = get_data_hundred_people(pd.read_csv(path_country, index_col="date"), population_path, country)
        data[country] = data_country[parameter]
        data.reindex_like(data_country)

    return data

def add_flags_column(data):
    data = data.transpose()
    data["flag"] = np.nan
    for country in FLAGS.keys():
        data["flag"][country] = ("https://github.com/blasf1/covid_vaccine_progress_bot/raw/main/flags/"
                    + FLAGS[country]
                    + ".png")

    for country in EXTERNAL.keys():
        data["flag"][country] = ("https://github.com/blasf1/covid_vaccine_progress_bot/raw/main/flags/"
                    + EXTERNAL[country]
                    + ".png")
    return data


# =============================================================================
# Arguments
# =============================================================================

description = "arrange data for a bar chart race."
parser = argparse.ArgumentParser(description=description)

arg = "--input"
parser.add_argument(arg)

arg = "--noneu"
parser.add_argument(arg)

arg = "--population"
parser.add_argument(arg)


args = sys.argv[1:]
args = parser.parse_args(args)

# Rename the command line arguments for easier reference
input = args.input
non_eu_path = args.noneu
population = args.population


# =============================================================================
# Main
# =============================================================================

data = get_arranged_data(input, non_eu_path, "people_vaccinated", population)
data = add_flags_column(data)
print(data)
data.to_csv("bar_race.csv")