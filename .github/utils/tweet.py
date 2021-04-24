"""String to publish in Twitter for a particular country."""


# =============================================================================
# Imports
# =============================================================================

# Standard
import os
import sys

# Third party
from tqdm import tqdm
import emoji
import flag
import numpy as np
import pandas as pd

# Local application
from statistics import (get_current_data,
                        get_rolling_average_day,
                        get_rolling_average_week,
                        get_current_data_increment,
                        get_rolling_average_day_increment,
                        get_rolling_average_week_increment)


# =============================================================================
# Constants
# =============================================================================

# Map the country name to the country flag
FLAGS = {
    "European Union": "",
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

def get_progress_bar(percentage, increment):
    """Get a progress bar string given a percentage."""
    initial = percentage
    total = 100
    bar_format = "|{bar:6}| {percentage:04.1f}%" + f" [{increment:+03.1f}]"

    with tqdm(initial=initial, total=total, bar_format=bar_format) as bar:
        # Convert the bar to string for concatenating
        bar_string = str(bar)

    pattern = "|"
    bar_separator_ix = bar_string.rfind(pattern)

    prefix = bar_string[:bar_separator_ix].replace(" ", "\u3000")
    suffix = bar_string[bar_separator_ix:]

    return prefix + suffix


def get_tweet_header(country):
    """Get the header of the tweet."""
    country_flag = FLAGS[country]

    return (flag.flagize(":EU:")
            + flag.flagize(country_flag)
            + str.upper(country)
            + flag.flagize(country_flag)
            + flag.flagize(":EU:")
            + "\n")


def get_progress_section(data):
    """Get the progress section of the tweet."""
    parameter = "people_vaccinated"
    people_vaccinated = get_current_data(data, parameter)
    people_vaccinated_increment = get_current_data_increment(data, parameter)

    parameter = "people_fully_vaccinated"
    fully_vaccinated = get_current_data(data, parameter)
    fully_vaccinated_increment = get_current_data_increment(data, parameter)

    return ("Progress:"
            + "\n"
            + get_progress_bar(people_vaccinated, people_vaccinated_increment)
            + " (1 dose)"
            + "\n"
            + get_progress_bar(fully_vaccinated, fully_vaccinated_increment)
            + " (Fully)"
            + "\n")


def get_total_admin_string(data):
    """Get the string of the normalized administered doses."""
    parameter = "total_vaccinations"
    current_data = get_current_data(data, parameter)
    current_data_increment = get_current_data_increment(data, parameter)

    return (emoji.emojize(":syringe:")
            + "Total:"
            + "\u3000" * 4
            + f"{current_data:05.2f}"
            + " ["
            + f"{current_data_increment:+04.2f}"
            + "]"
            + "\n")


def get_last_admin_string(data):
    """Get the string of the normalized last day administered doses."""
    parameter = "total_vaccinations"
    average_day = get_rolling_average_day(data, parameter)
    average_day_increment = get_rolling_average_day_increment(data, parameter)

    return (emoji.emojize(":syringe:")
            + "Last day:"
            + "\u3000" * 2
            + f"{average_day:04.2f}"
            + " ["
            + f"{average_day_increment:+04.2f}"
            + "]"
            + "\n")


def get_seven_days_string(data):
    """Get the string of the normalized 7-day average administered doses."""
    parameter = "total_vaccinations"
    average_week = get_rolling_average_week(data, parameter)
    average_week_increment = get_rolling_average_week_increment(data, parameter)

    return (emoji.emojize(":syringe:")
            + "7 days average:"
            + "\u3000"
            + f"{average_week:04.2f}"
            + " ["
            + f"{average_week_increment:+04.2f}"
            + "]"
            + "\n")

def get_total_administered(data):
    """Get total administered section of the tweet."""
    total = get_current_data(data, "total_vaccinations")
    increment = get_current_data_increment(data, "total_vaccinations")
    return ("\nAdministered:\n"
            + emoji.emojize(":syringe:")
            + "Total:"
            + "\u3000" * 3
            + f"{total:,.0f}"
            + " ["
            + f"{increment:+,.0f}"
            + "]"
            + "\n")


def get_administered_section(data):
    """Get the administered section of the tweet."""
    print(get_seven_days_string(data))
    return ("\n"
            + "Per 100 people:\n"
            + get_total_admin_string(data)
            #+ get_last_admin_string(data))
            + get_seven_days_string(data))
            


def get_tweet(country, data, data_normalized):
    """Get the tweet to publish in Twitter for a particular country."""
    return (get_tweet_header(country)
            + get_progress_section(data_normalized)
            + get_total_administered(data)
            + get_administered_section(data_normalized))
