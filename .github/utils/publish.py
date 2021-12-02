"""Publish the vaccination data for a country in Twitter."""


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
import telegram

# Local application
from tweet import get_tweet
from tweet_boosters import get_tweet_boosters
from statistics import (read_data,
                        read_data_unsupported,
                        get_last_date,
                        get_population,
                        store_last_data,
                        get_data_hundred_people,
                        get_previous_vaccinations)

# =============================================================================
# Constants
# =============================================================================

COUNTRIES = [
    "Austria",
    "Belgium",
    "Bulgaria",
    "Croatia",
    "Cyprus",
    "Czechia",
    "Denmark",
    "Estonia",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Hungary",
    "Ireland",
    "Italy",
    "Latvia",
    "Lithuania",
    "Luxembourg",
    "Malta",
    "Netherlands",
    "Poland",
    "Portugal",
    "Romania",
    "Slovakia",
    "Slovenia",
    "Spain",
    "Sweden"]

COUNTRIES_BOOSTERS = [
    "Malta",
    "Germany",
    "Denmark",
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
    "Portugal",
    "Sweden"
]

UNSUPPORTED_COUNTRIES = []
# Countries whose stats must be posted with 24 hours delay
DELAYED_COUNTRIES = ["Italy", "Slovenia", "Slovakia", "Estonia"]
ONLY_FULL_COUNTRIES = ["Bulgaria"]  # Countries reporting only full vaccination

# =============================================================================
# Functions
# =============================================================================


def publish_tweet(country, api, data, data_unsupported, input, population):
    # Get last date when the country data was published
    print("Updating " + country + "...")
    last_date = get_last_date(output, country)
    previous_vaccinations = get_previous_vaccinations(output, country)
    if country not in UNSUPPORTED_COUNTRIES:
        # Get the vaccination data for the country
        data = read_data(data, country, input)
    else:
        # Get the vaccination data for the country when not supported by owid
        data = read_data_unsupported(data_unsupported, country, output)
        store_last_data(output, country, data)
    data = data.sort_values(by='date')
    date = data.index[-1]
    vaccinations = data["people_vaccinated"].iloc[-1]

    if country in ONLY_FULL_COUNTRIES:
        data["people_vaccinated"].fillna(
            data["people_fully_vaccinated"], inplace=True)

    print(date)
    print(last_date)

    if (date == last_date or vaccinations <= (previous_vaccinations + 100)):
        print(f"{country} data is up to date.")
        # Exit with a success code
        return

    # For delayed countries ignore the last row
    if country in DELAYED_COUNTRIES:
        data.drop(index=data.index[-1], axis=0, inplace=True)

    # Get population and relative country data
    population = get_population(population, country)
    data_normalized = get_data_hundred_people(data, population)

    # Get the tweet string to publish in Twitter
    try:
        tweet_string = get_tweet(country, data, data_normalized)
    except ValueError:
        print(f"{country} data was not complete.")

        # Exit with a success code
        return

    print(tweet_string)

    try:
        tweet = api.update_status(tweet_string)
        #publish in telegram
        bot = telegram.Bot(token=telegram_api)
        status = bot.send_message(
            chat_id="@euCovidVaccination", text=tweet_string)
    except tweepy.TweepError:
        print(f"Tweet already published.")

    # try:
    #     if country in COUNTRIES_BOOSTERS:
    #         tweet_string = get_tweet_boosters(country, data, data_normalized)
    #         tweet = api.update_status(
    #             tweet_string, in_reply_to_status_id=tweet.id)
    # except UnboundLocalError:
    #     print(f"Tweet already published. No boosters to publish")


# =============================================================================
# Arguments
# =============================================================================

description = "Publish vaccination data for a country."
parser = argparse.ArgumentParser(description=description)

arg = "--data"
parser.add_argument(arg)

arg = "--data-unsupported"
parser.add_argument(arg)

arg = "--input"
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

arg = "--telegram"
default = os.environ.get("TELEGRAM")
parser.add_argument(arg, default=default)

args = sys.argv[1:]
args = parser.parse_args(args)

# Rename the command line arguments for easier reference
data = args.data
data_unsupported = args.data_unsupported
input = args.input
output = args.output
population = args.population
api = args.api
api_secret = args.api_secret
access = args.access
access_secret = args.access_secret
telegram_api = args.telegram

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

for country in COUNTRIES:
    publish_tweet(country, api, data, data_unsupported, input, population)
