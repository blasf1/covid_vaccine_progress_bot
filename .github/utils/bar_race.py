"""Publish the bar race in Twitter."""

# =============================================================================
# Imports
# =============================================================================
# Standard
import argparse
import os
import sys

import bar_chart_race as bcr
import pandas as pd
import datetime


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

def get_arranged_data(path, parameter, population_path):
    """Read the last vaccination data for all countries."""
    #files = glob.glob(path + "*.csv")
    data = pd.DataFrame(columns = FLAGS.keys())
    #data.set_index(inplace = true)
    for country in FLAGS.keys():
        path_country = os.path.join(path + country.replace(" ", "") + ".csv")
        data_country = get_data_hundred_people(pd.read_csv(path_country, index_col="date"), population_path)
        data[country] = data_country[parameter]
        data.reindex_like(data_country)

    return data


# =============================================================================
# Arguments
# =============================================================================


# description = "Publish vaccination data for a country."
# parser = argparse.ArgumentParser(description=description)

# arg = "--data"
# default = os.environ.get("DATA")
# parser.add_argument(arg, default=default)

# arg = "--output"
# default = os.environ.get("OUTPUT")
# parser.add_argument(arg, default=default)

# arg = "--population"
# default = os.environ.get("POPULATION")
# parser.add_argument(arg, default=default)

# arg = "--flags"
# default = os.environ.get("FLAGS")
# parser.add_argument(arg, default=default)

# arg = "--api"
# default = os.environ.get("BOT_API")
# parser.add_argument(arg, default=default)

# arg = "--api-secret"
# default = os.environ.get("BOT_API_SECRET")
# parser.add_argument(arg, default=default)

# arg = "--access"
# default = os.environ.get("BOT_ACCESS")
# parser.add_argument(arg, default=default)

# arg = "--access-secret"
# default = os.environ.get("BOT_ACCESS_SECRET")
# parser.add_argument(arg, default=default)

# args = sys.argv[1:]
# args = parser.parse_args(args)

# # Rename the command line arguments for easier reference
# data = args.data
# output = args.output
# population = args.population
# flags = args.flags
# api = args.api
# api_secret = args.api_secret
# access = args.access
# access_secret = args.access_secret


# =============================================================================
# Main
# =============================================================================

get_arranged_data("../../output/", "total_vaccinations", "../../population_2020.csv")