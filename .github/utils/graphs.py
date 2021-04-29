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
import matplotlib as mpl
import pandas as pd
import numpy as np
import datetime

# Local application
from statistics import (read_data,
                        get_population,
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
# =============================================================================
# Functions
# =============================================================================

def read_data(path):
    """Read the vaccination data for a country."""
    # Use the date to identify the vaccination data
    path = os.path.join(path, country + ".csv")

    index_col = "date"
    data = pd.read_csv(path, index_col=index_col)

    return data

# =============================================================================
# Arguments
# =============================================================================

description = "Publish vaccination data for a country."
parser = argparse.ArgumentParser(description=description)

arg = "--country"
parser.add_argument(arg)

arg = "--data"
parser.add_argument(arg)

arg = "--output"
parser.add_argument(arg)

arg = "--population"
parser.add_argument(arg)

arg = "--api"
default = os.environ.get("BOT_API")
parser.add_argument(arg, default=default)

arg = "--api-secret"
default = os.environ.get("BOT_API_SECRET")
parser.add_argument(arg, default=default)

arg = "--access"
default = os.environ.get("BOT_ACCESS")
parser.add_argument(arg, default=default)

arg = "--access-secret"
default = os.environ.get("BOT_ACCESS_SECRET")
parser.add_argument(arg, default=default)

args = sys.argv[1:]
args = parser.parse_args(args)

# Rename the command line arguments for easier reference
country = args.country
data = args.data
output = args.output
population = args.population
api = args.api
api_secret = args.api_secret
access = args.access
access_secret = args.access_secret

#Read data
data = read_data(data)