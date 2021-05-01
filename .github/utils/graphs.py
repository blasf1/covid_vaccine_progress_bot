"""Publish the graphs vaccination for all countries in Twitter."""


# =============================================================================
# Imports
# =============================================================================
# Standard
import argparse
import os
import sys
import glob

# Third party
import tweepy
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np
import datetime

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
    read_csv = lambda file: get_data_hundred_people(pd.read_csv(file).iloc[[-1]], path_population)

    data = pd.concat(map(read_csv, files))

    return data


def plot_data(data, parameter, title):
    """Plot data in parameter for all countries in dataframe"""
    data = data.sort_values(by=parameter, ascending=True)
    x = "location"
    figsize = (12,12)
    legend = False
    width = 0.75

    matplotlib.rcParams['axes.axisbelow'] = True
    ax = data.plot.barh(x = x, y = parameter, figsize = figsize, legend = legend, title = title, width = width)

    # Despine
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(False)

    # Switch off ticks
    #ax.tick_params(axis="both", which="both", bottom="off", top="off", labelbottom="off", left="off", right="off", labelleft="on")

    # Draw vertical axis lines
    vals = ax.get_xticks()
    for tick in vals:
        ax.axvline(x=tick, linestyle='dashed', alpha=0.5, color='#293133', zorder=0)

    [ax.text(v, i, '{:.2f}'.format(v)) for i, v in enumerate(data[parameter])]

    #autolabel(ax.xaxis.barh)

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

arg = "--population"
parser.add_argument(arg)

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
population = args.population
#api = args.api
#api_secret = args.api_secret
#access = args.access
#access_secret = args.access_secret

#Read data
data = read_data(data, population)
print(data)


#Plot
plot_data(data, "total_vaccinations", "Doses administered per 100 people")