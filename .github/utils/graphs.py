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
from matplotlib.offsetbox import OffsetImage,AnnotationBbox
import matplotlib
import pandas as pd
import numpy as np
import datetime
import requests
from io import BytesIO
from cycler import cycler


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
    "Sweden": "SE"
}

COLOR_MAP = ["#3C4E66",
             "#B13507",
             "#00847E",
             "#6D3E91",
             "#CF0A66",
             "#883039",
             "#00823F",
             "#4C6A9C",
             "#C05917",
             "#D73C50",
             "#287669",
             "#CD2285",
             "#0F739C",
             "#9A5129",
             "#C45267",
             "#008860",
             "#8C4569",
             "#B36216",
             "#366388",
             "#A2559C",
             "#578145",
             "#D7263F",
             "#18470F",
             "#BC8E5A",
             "#585C64"
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
    read_csv = lambda file: get_data_hundred_people(pd.read_csv(file).iloc[[-1]], path_population)

    data = pd.concat(map(read_csv, files))

    return data


def get_flag(code):
    """Gets flag icon"""
    img = plt.imread(f'../../flags/{code}.png')
    img = OffsetImage(img, zoom=0.15)

    return img


def offset_image(coord, name, ax):
    """Determines flags locations"""
    img = get_flag(FLAGS[name])
    img.image.axes = ax
    ab = AnnotationBbox(img, (0, coord),  xybox=(-12, 0), frameon=False,
                        xycoords='data',  boxcoords="offset points", pad=-1)

    ax.add_artist(ab)


def plot_data(data, parameter, title):
    """Plot data in parameter for all countries in dataframe"""
    data = data.sort_values(by=parameter, ascending=True)
    x = "location"
    figsize = (12,12)
    legend = False
    width = 0.7

    # Font 
    plt.rcParams['font.sans-serif'] = "Arial"
    plt.rcParams['font.family'] = "sans-serif"


    # Color 
    cy = cycler('color', COLOR_MAP)
    #ax.set_prop_cycle(cy)
    plt.rcParams['axes.prop_cycle'] = cy

    ax = data.plot.barh(x = x, y = parameter, figsize = figsize, legend = legend, width = width, xlabel="", fontsize = 12)
    
    # Despine
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(False)

    ax.xaxis.set_label("")

    # Title
    ax.set_title(title, fontsize=20, loc="left", fontname='Oswald')

    # Draw vertical axis lines
    vals = ax.get_xticks()
    for tick in vals:
        ax.axvline(x=tick, linestyle='dashed', alpha=0.25, color='#293133', zorder=0)

    # Show number at the end of the bar
    [ax.text(v + 0.4, i - (width / 4), '{:.2f}'.format(v), fontsize=11) for i, v in enumerate(data[parameter])]

    # configure y axis labels (add flags)
    ax.tick_params(axis = "y", which = "both", left = False, right = False, pad = 5, size = 20)
    ax.tick_params(axis = "x", which = "both", bottom = False, top = False)
    for i, c in enumerate(data["location"]):
        offset_image(i, c, ax)

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