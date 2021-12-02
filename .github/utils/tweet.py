"""String to publish in Twitter for a particular country."""


# =============================================================================
# Imports
# =============================================================================

# Standard
import os
import sys
import datetime
import math

# Third party
from tqdm import tqdm
import emoji
import flag
import numpy as np
import pandas as pd

# Local application
from statistics import (get_current_data,
                        get_rolling_average_week,
                        get_current_data_increment,
                        get_rolling_average_week_increment,
                        is_record,
                        get_days_reported)


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

NO_7_DAYS = {
}

COUNTRIES_BOOSTERS = [
    "Malta",
    "Germany",
    "Luxembourg",
    "Hungary",
    "Belgium",
    "France",
    "Italy",
    "Lithuania",
    "Spain",
    "Austria",
    "Cyprus",
    "Greece",
    "Czechia",
    "Poland",
    "Ireland",
    "Denmark",
    "Portugal",
    "Sweden",
    "European Union"
]
# =============================================================================
# Functions
# =============================================================================


def generateProgressbar(percentage):
    num_chars = 15
    num_filled = round((percentage / 100) * num_chars)
    num_empty = num_chars-num_filled
    msg = '{}{}'.format('█'*num_filled, '░'*num_empty)
    return msg


def get_progress_bar(percentage, increment):
    """Get a progress bar string given a percentage."""
    initial = percentage
    total = 100
    bar_format = generateProgressbar(
        percentage) + "\n" + "{percentage:04.1f}%" + f"[{increment:+03.1f}]"

    with tqdm(initial=initial, total=total, bar_format=bar_format) as bar:
        # Convert the bar to string for concatenating
        bar_string = str(bar)

    pattern = "|"
    bar_separator_ix = bar_string.rfind(pattern)

    prefix = bar_string[:bar_separator_ix].replace(" ", "\u3000")
    suffix = bar_string[bar_separator_ix:]

    return prefix + suffix


def get_tweet_header(country, data):
    """Get the header of the tweet."""
    country_flag = FLAGS[country]
    string = (flag.flagize(":EU:")
              + flag.flagize(country_flag)
              + str.upper(country)
              + flag.flagize(country_flag)
              + flag.flagize(":EU:")
              + "\n")

    # if is_record(data, "total_vaccinations"):
    #     string = (string
    #               + emoji.emojize(":trophy:")
    #               + "Daily Record"
    #               + emoji.emojize(":trophy:")
    #               + "\n")

    return string


def get_progress_section(data):
    """Get the progress section of the tweet."""
    parameter = "people_vaccinated"
    people_vaccinated = get_current_data(data, parameter)
    people_vaccinated_increment = get_current_data_increment(data, parameter)

    parameter = "people_fully_vaccinated"
    fully_vaccinated = get_current_data(data, parameter)
    fully_vaccinated_increment = get_current_data_increment(data, parameter)

    if (people_vaccinated):
        return ("\nAt least 1 dose:\n"
                + get_progress_bar(people_vaccinated,
                                   people_vaccinated_increment)
                + "\n\n"
                + "Fully:\n"
                + get_progress_bar(fully_vaccinated,
                                   fully_vaccinated_increment)
                + "\n"
                + "\n")
    else:
        return ("\n"
                + "Fully:\n"
                + get_progress_bar(fully_vaccinated,
                                   fully_vaccinated_increment)
                + "\n"
                + "\n")


def get_boosters_section(data):
    """Get the progress section of the tweet."""
    parameter = "total_boosters"
    boosters = get_current_data(data, parameter)
    boosters_increment = get_current_data_increment(data, parameter)

    return ("Boosters:\n"
            + get_progress_bar(boosters,
                               boosters_increment)
            + "\n"
            + "\n")


def get_seven_days_string(data, country):
    """Get the string of the normalized 7-day average administered doses."""
    parameter = "total_vaccinations"
    average_week = get_rolling_average_week(data, parameter)
    average_week_increment = get_rolling_average_week_increment(
        data, parameter)

    if math.isnan(average_week_increment) or country in NO_7_DAYS:
        return ""
    else:
        return ("7 days avg.: "
                + "\u3000"
                + f"{average_week:04.2f}"
                + " ["
                + f"{average_week_increment:+04.2f}"
                + "]"
                + "\n")


def get_total_administered(data, country):
    """Get total administered section of the tweet."""
    total = get_current_data(data, "total_vaccinations")
    increment = get_current_data_increment(data, "total_vaccinations")

    if math.isnan(increment):
        return ""
    elif country in COUNTRIES_BOOSTERS:
        boosters = get_current_data(data, "total_boosters")
        boosters_increment = get_current_data_increment(data, "total_boosters")
        return (  # "\nAdministered:\n"
            # emoji.emojize(":syringe:")
            "Total:"
            + "\u3000"
            + f"{total:,.0f}"
            + " ["
            + f"{increment:+,.0f}"
            + "]"
            + "\n"
            + "Boosters: "
            + f"{boosters:,.0f}"
            + " ["
            + f"{boosters_increment:+,.0f}"
            + "]"
            + "\n"
        )
    else:
        return ("Total:"
                + "\u3000"
                + f"{total:,.0f}"
                + " ["
                + f"{increment:+,.0f}"
                + "]"
                + "\n"
                )


def get_days_reported_string(country, data):
    days = get_days_reported(data)

    if days <= datetime.timedelta(days=1):
        return ""
    else:
        return ("\n*"
                + "Aggregated data of "
                + str(days.days)
                + " days")


def get_tweet(country, data, data_normalized):
    """Get the tweet to publish in Twitter for a particular country."""
    if country in COUNTRIES_BOOSTERS:
        return (get_tweet_header(country, data)
                + get_progress_section(data_normalized)
                + get_boosters_section(data_normalized)
                + get_total_administered(data, country)
                + get_seven_days_string(data_normalized, country)
                + get_days_reported_string(country, data))
    else:
        return (get_tweet_header(country, data)
                + get_progress_section(data_normalized)
                + get_total_administered(data, country)
                + get_seven_days_string(data_normalized, country)
                + get_days_reported_string(country, data))
