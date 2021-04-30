"""Publish the graphs vaccination for all countries in Twitter."""


# =============================================================================
# Imports
# =============================================================================
# Standard
import argparse
import os
import sys

# Third party
import tweepy
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime

# Local application
from statistics import (get_population,
                        get_data_hundred_people)

# =============================================================================
# Constants
# =============================================================================

# Map the country name to the country flag
FLAGS = {
    "European Union": ":EU:",
    "Austria": ":AT:",
    "Belgium": ":BE:",
    "Bulgaria": ":BG:",
    "Croatia": ":HR:",
    "Cyprus": ":CY:",
    "Czechia": ":CZ:",
    "Denmark": ":DK:",
    "Estonia": ":EE:",
    "Finland": ":FI:",
    "France": ":FR:",
    "Germany": ":DE:",
    "Greece": ":GR:",
    "Hungary": ":HU:",
    "Ireland": ":IE:",
    "Italy": ":IT:",
    "Latvia": ":LV:",
    "Lithuania": ":LT:",
    "Luxembourg": ":LU:",
    "Malta": ":MT:",
    "Netherlands": ":NL:",
    "Poland": ":PL:",
    "Portugal": ":PT:",
    "Romania": ":RO:",
    "Slovakia": ":SK:",
    "Slovenia": ":SI:",
    "Spain": ":ES:",
    "Sweden": ":SE:"
}

COLUMNS = ["date", "total_vaccinations", "people_vaccinated", "people_fully_vaccinated", "country"]
# =============================================================================
# Functions
# =============================================================================

def read_data(path):
    """Read the last vaccination data for all countries."""
    index_col = "date"
    data = pd.DataFrame(columns = COLUMNS)
    for country in FLAGS.keys():
        path_file = os.path.join(path, country.replace(" ", "") + ".csv")
        data_country = pd.read_csv(path_file)
        data_country = data_country.iloc[-1]#.insert(1, "country", [country] * len(data_country), False)
        data_country["country"] = country
        data = data.append(data_country)

    return data

def plot_data(data, parameter):
    """Plot data in parameter for all countries in dataframe"""

    x = "country"
    kind = "bar"
    
    data.plot(x = x, y = parameter, kind = kind)
    plt.show()

# =============================================================================
# Arguments
# =============================================================================

description = "Publish vaccination data for a country."
parser = argparse.ArgumentParser(description=description)

arg = "--data"
parser.add_argument(arg)

# arg = "--output"
# parser.add_argument(arg)

# arg = "--population"
# parser.add_argument(arg)

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

args = sys.argv[1:]
args = parser.parse_args(args)

# Rename the command line arguments for easier reference
#country = args.country
data = args.data
#output = args.output
#population = args.population
#api = args.api
#api_secret = args.api_secret
#access = args.access
#access_secret = args.access_secret

#Read data
data = read_data(data)
print(data)
#Plot
plot_data(data, "total_vaccinations")