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
import numpy as np
import datetime
import emoji


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


def read_data(path, path_population):
    """Read the last vaccination data for all countries."""
    files = glob.glob(path + "*.csv")
    read_csv = lambda file: get_data_hundred_people(pd.read_csv(file).iloc[[-1]], path_population)

    data = pd.concat(map(read_csv, files))

    return data


def get_flag(code):
    """Gets flag icon"""
    img = plt.imread(f'../../flags/{code}.png')
    img = OffsetImage(img, zoom=0.2)

    return img


def offset_image(coord, name, ax):
    """Determines flags locations"""
    img = get_flag(FLAGS[name])
    img.image.axes = ax
    ab = AnnotationBbox(img, (0, coord),  xybox=(-15, 0), frameon=False,
                        xycoords='data',  boxcoords="offset points", pad=-1)

    ax.add_artist(ab)


def plot_data(data, unit, parameter, title, output):
    """Plot data in parameter for all countries in dataframe"""
    data = data.sort_values(by=parameter, ascending=True)
    x = "location"
    figsize = (14,12)
    legend = False
    width = 0.75

    # Font 
    plt.rcParams['font.sans-serif'] = "Arial"
    plt.rcParams['font.family'] = "sans-serif"

    data_to_plot = data[["location", parameter]].dropna()
    ax = data_to_plot.plot.barh(x = x, y = parameter, figsize = figsize, legend = legend, width = width, xlabel="", fontsize = 16, color = "#3C4E66")
    
    # Despine
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(False)

    ax.xaxis.set_label("")

    # Title
    ax.set_title(title + ", " + datetime.datetime.now().strftime("%d-%m-%Y"), fontsize = 28, loc = "left", fontname = "Arial", fontweight = "bold", pad = 10)

    # Draw vertical axis lines
    vals = ax.get_xticks()
    for tick in vals:
        ax.axvline(x=tick, linestyle='dashed', alpha=0.2, color='#293133', zorder=0)

    # Show number at the end of the bar
    [ax.text(v + 0.4, i - (width / 4), "{:.2f}".format(v) + unit, fontsize=16) for i, v in enumerate(data[parameter])]

    # configure y axis labels (add flags)
    ax.tick_params(axis = "y", which = "both", left = False, right = False, pad = 10, size = 20)
    ax.tick_params(axis = "x", which = "both", bottom = False, top = False)
    for i, c in enumerate(data["location"]):
        offset_image(i, c, ax)

    file = os.path.join(output + title.replace(" ", "_") + ".png")
    plt.figtext(0.01,0.01,"@VaccinationEu\nSource: Our World in Data")
    plt.tight_layout()
    
    plt.savefig(file, dpi=300)

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

arg = "--population"
default = os.environ.get("POPULATION")
parser.add_argument(arg, default=default)

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
data = args.data
output = args.output
population = args.population
api = args.api
api_secret = args.api_secret
access = args.access
access_secret = args.access_secret


# =============================================================================
# Main
# =============================================================================

# Authenticate in Twitter using the secret variables
auth = tweepy.OAuthHandler(api, api_secret)
auth.set_access_token(access, access_secret)

# Get the API to use Twitter
api = tweepy.API(auth)

# Do not expose any user information to avoid malicious attacks
include_email = False
user = api.verify_credentials(include_email=include_email)

#Read data
data = read_data(data, population)

#Plot
title1 = "Doses administered per 100 people"
plot_data(data, "", "total_vaccinations", title1, output)

# title2 = "% population fully vaccinated"
# plot_data(data, "%", "people_fully_vaccinated", title2, output)

# title3 = "% population vaccinated with at least one dose"
# plot_data(data, "%", "people_vaccinated", title3, output)

tweet = (emoji.emojize(":calendar::bar_chart:") 
        + " It's time for a daily sum up! "
        +emoji.emojize(":syringe:"))

print(tweet)

image_path = os.path.join(output + title1.replace(" ", "_") + ".png")

tweet_id = api.update_with_media(image_path, status)