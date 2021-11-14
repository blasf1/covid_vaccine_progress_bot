# coding=utf-8
"""Publish the graphs vaccination for all countries in Twitter."""

# =============================================================================
# Imports
# =============================================================================
# Standard
import argparse
import os
import sys
import glob
from cycler import cycler

# Third party
import tweepy
import flag
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib
import numpy as np
import datetime
import emoji

# Local application
from statistics import (get_current_data,
                        get_current_data_increment)
from statistics import read_data as read_data_eu

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


def get_rolling_average(data, parameter, days):
    """Get the rolling average of the vaccination data."""
    # Use one period for the rolling average
    periods = 1
    # keep days + 1 so that diff can cçompare with the last day out of the average
    data_for_average = data.tail(days + 1)
    data_for_average.reset_index(inplace=True)
    data_for_average["date"] = pd.to_datetime(
        data_for_average["date"], format='%Y-%m-%d')

    # data_for_average.iloc[-1]["date"] - data_for_average.iloc[0]["date"]
    date_limit = data_for_average.iloc[-1]["date"] - \
        datetime.timedelta(days=days + 1)

    data_for_average = data_for_average[data_for_average["date"] > date_limit]

    data_for_average = data_for_average[parameter]

    data_for_average = data_for_average.dropna()  # remove empty rows for diff()
    difference = data_for_average.diff(periods)

    return (difference.sum() / days)


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
    print(path)

    def read_csv(file):
        data = pd.read_csv(file)
        data["people_vaccinated"].fillna(
            data["people_fully_vaccinated"], inplace=True)
        data = data.ffill()
        data = data.iloc[[-1]]
        data["7_days_average"] = get_rolling_average(
            pd.read_csv(file), "total_vaccinations", 7)
        data = get_data_hundred_people(data, path_population)
        print(data)
        return data

    data = pd.concat(map(read_csv, files))
    data = data.sort_values(by="date")
    return data


def get_flag(code, flags):
    """Gets flag icon"""
    path = os.path.join(flags + code + ".png")
    img = plt.imread(path)
    img = OffsetImage(img, zoom=0.2)

    return img


def offset_image(coord, name, ax, flags):
    """Determines flags locations"""
    img = get_flag(FLAGS[name], flags)
    img.image.axes = ax
    ab = AnnotationBbox(img, (0, coord),  xybox=(-15, 0), frameon=False,
                        xycoords='data',  boxcoords="offset points", pad=-1)

    ax.add_artist(ab)


def plot_data(data, unit, parameter, title, output, flags):
    """Plot data in parameter for all countries in dataframe"""
    x = "location"
    figsize = (14, 12)
    legend = False
    width = 0.75

    # Font
    plt.rcParams['font.sans-serif'] = "Arial"
    plt.rcParams['font.family'] = "sans-serif"

    data_to_plot = data[["location", parameter]].sort_values(
        by=parameter, ascending=True).dropna()

    ax = data_to_plot.plot.barh(x=x, y=parameter, figsize=figsize,
                                legend=legend, width=width, xlabel="",
                                fontsize=16, color="#3C4E66")

    # Despine
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(False)

    ax.xaxis.set_label("")

    # Title
    ax.set_title(title + ", " + datetime.datetime.now().strftime("%d-%m-%Y"),
                 fontsize=24, loc="left", fontname="Arial", fontweight="bold", pad=16)

    # Draw vertical axis lines
    vals = ax.get_xticks()
    for tick in vals:
        ax.axvline(x=tick, linestyle='dashed',
                   alpha=0.2, color='#293133', zorder=0)

    if data_to_plot[parameter].iloc[-1] > 5:
        # Show number at the end of the bar
        [ax.text(v + 0.4, i - (width / 4), "{:.2f}".format(v) +
                 unit, fontsize=16) for i, v in enumerate(data_to_plot[parameter])]
    else:
        # Show number at the end of the bar
        [ax.text(v + 0.02, i - (width / 4), "{:.2f}".format(v) +
                 unit, fontsize=16) for i, v in enumerate(data_to_plot[parameter])]

    # configure y axis labels (add flags)
    ax.tick_params(axis="y", which="both", left=False,
                   right=False, pad=10, size=20)
    ax.tick_params(axis="x", which="both", bottom=False, top=False)
    for i, c in enumerate(data_to_plot["location"]):
        offset_image(i, c, ax, flags)

    file = os.path.join(output + title.replace(" ", "_") + ".png")
    plt.figtext(0.01, 0.01, "@VaccinationEu\nMissing EU countries did not report enough data | Check data sources and extra info at https://blasf1.github.io/VaccinatEU/", fontsize=11)
    plt.tight_layout(pad=2)

    plt.savefig(file, dpi=300)


def plot_stacked(data, unit, parameter1, parameter2, title, output, flags):
    """Plot data in parameter for all countries in dataframe"""
    x = "location"
    figsize = (14, 12)
    legend = False
    width = 0.75

    # Font
    #plt.rcParams['font.sans-serif'] = "Arial"
    #plt.rcParams['font.family'] = "sans-serif"
    plt.rcParams["axes.prop_cycle"] = cycler('color', [
                                             '#3C4E66', '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'])

    data_to_plot = data[["location"] + [parameter1] + [parameter2]].sort_values(
        by=parameter2, ascending=True).dropna()

    data_to_plot["substraction"] = data_to_plot[parameter2] - \
        data_to_plot[parameter1]
    data_to_stack = data_to_plot[["location"] +
                                 [parameter1] + ["substraction"]]
    data_to_stack.rename(
        columns={"substraction": "Partially vaccinated", parameter1: "Fully vaccinated"})
    ax = data_to_stack.plot.barh(x=x, figsize=figsize,
                                 legend=legend, width=width, xlabel="",
                                 fontsize=16, stacked=True)  # , color=["#3C4E66", "#2C4E66"]) , labels=["Fully vaccinated", "Partially vaccinated"]

    # Despine
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(False)

    ax.xaxis.set_label("")
    plt.xlim([0, 100])
    # Title
    plt.suptitle(title + ", " + datetime.datetime.now().strftime("%d-%m-%Y"),
                 fontsize=22, fontweight="bold", x=0.532, y=0.96)
    ax.set_title("Share of the total population fully vaccinated, partly vaccinated, and with at least 1 dose",
                 fontsize=16, loc="left", pad=10)

    # Draw vertical axis lines
    vals = ax.get_xticks()
    for tick in vals:
        ax.axvline(x=tick, linestyle='dashed',
                   alpha=0.2, color='#293133', zorder=0)

    [ax.text(v/2 - 2, i - (width / 4), "{:.1f}".format(v) +
             unit, fontsize=16, color="#FFFFFF") for i, v in enumerate(data_to_plot[parameter1])]

    for i, v in enumerate(data_to_plot[parameter2] - data_to_plot[parameter1]):
        if v > 6:
            ax.text(v/2 + data_to_plot.iloc[i][parameter1] - 2.5, i - (width / 4), "{:.1f}".format(v) +
                    unit, fontsize=16, color="#FFFFFF")

    [ax.text(v + 0.5, i - (width / 4), "{:.1f}".format(v) +
             unit, fontsize=16) for i, v in enumerate(data_to_plot[parameter2])]

    # configure y axis labels (add flags)
    ax.tick_params(axis="y", which="both", left=False,
                   right=False, pad=10, size=20)
    ax.tick_params(axis="x", which="both", bottom=False, top=False)
    for i, c in enumerate(data_to_plot["location"]):
        offset_image(i, c, ax, flags)

    file = os.path.join(output + title.replace(" ", "_") + ".png")
    labels = ["Fully vaccinated", "Partly vaccinated"]
    colors = {"full": "#3C4E66", "partial": "#1f77b4"}
    handles = [plt.Rectangle((0, 0), 3, 3, color=colors[color])
               for color in colors]
    plt.legend(handles, labels, loc="lower right", fontsize=16)
    plt.figtext(
        0.01, 0.01, "@VaccinationEu\nCheck data sources and extra info at https://blasf1.github.io/VaccinatEU/", fontsize=11)
    plt.tight_layout(pad=2)

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

arg = "--flags"
default = os.environ.get("FLAGS")
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
flags = args.flags
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

# Read data
data = read_data(data, population)

# Plot
# Remove countries whose average cannot be calculated
countries_to_skip = ["Luxembourg"]

for country in countries_to_skip:
    data = data[data["location"] != country]

title1 = "Share of people vaccinated against COVID-19"
plot_stacked(data, "%", "people_fully_vaccinated",
             "people_vaccinated", title1, output, flags)

title2 = "Doses administered per 100 people"
plot_data(data, "", "total_vaccinations", title2, output, flags)

# title2 = "% population fully vaccinated"
# plot_data(data, "%", "people_fully_vaccinated", title2, output, flags)

title3 = "% population that has received a booster"
plot_data(data, "%", "total_boosters", title3, output, flags)

# Remove countries whose average cannot be calculated
countries_without_average = ["Hungary", "Malta"]

for country in countries_without_average:
    data = data[data["location"] != country]

title4 = "Daily doses per 100 people (7 days average)"
plot_data(data, "", "7_days_average", title4, output, flags)

data_eu = read_data_eu(output, "European Union", output)
data_eu.drop(data_eu.tail(1).index, axis=0, inplace=True)

doses_in_eu = get_current_data_increment(data_eu, "total_vaccinations")

tweet = (emoji.emojize(":calendar::bar_chart:")
         + "Daily summary!"
         + "\n\n"
         + flag.flagize(":EU:")
         + emoji.emojize(":syringe:")
         + "Yesterday, "
         + f"{doses_in_eu:,.0f}"
         + " doses"
         + emoji.emojize(":syringe:")
         + " were administered in the EU"
         + flag.flagize(":EU:")
         )
print(tweet)
images = [os.path.join(output + title1.replace(" ", "_") + ".png"),
          os.path.join(output + title2.replace(" ", "_") + ".png"),
          os.path.join(output + title3.replace(" ", "_") + ".png"),
          os.path.join(output + title4.replace(" ", "_") + ".png")
          ]
media_ids = []

for image in images:
    res = api.media_upload(image)
    media_ids.append(res.media_id)

tweet_id = api.update_status(status=tweet, media_ids=media_ids)

reminder = (emoji.emojize(":pushpin:")
            + "Shares over the total population (not just adults)"
            + "\n\n"
            #+ emoji.emojize(":pushpin:")
            #+ "Hungary is not providing enough data"
            #+ "\n\n"
            + emoji.emojize(":pushpin:")
            + "Remember that this is just information, not a competition. We all are in this together"
            + emoji.emojize(":blue_heart:")
            + flag.flagize(":EU:")
            + "\n\n"
            + emoji.emojize(":pushpin:")
            + "Check the data sources and extra info here: https://blasf1.github.io/VaccinatEU/"
            )

api.update_status(status=reminder,
                  in_reply_to_status_id=tweet_id.id,
                  auto_populate_reply_metadata=True)
