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
from statistics import (read_data,
                        read_data_unsupported,
                        get_last_date,
                        get_population,
                        store_last_data,
                        get_data_hundred_people)


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

arg = "--telegram"
default = os.environ.get("TELEGRAM")
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

# Get last date when the country data was published
last_date = get_last_date(output, country)

if country == "EuropeanUnion":
        country = "European Union"

unsupported_countries = ["Austria", "Croatia", "European Union", "Hungary"]

if country not in unsupported_countries:
    # Get the vaccination data for the country
    data = read_data(data, country, output)
else:
    # Get the vaccination data for the country when not supported by owid
    data = read_data_unsupported(data, country, output)
    
store_last_data(output, country, data) 
date = data.index[-1]
vaccinations = data["total_vaccinations"].iloc[-1]
previous_vaccinations = data["total_vaccinations"].iloc[-2]
if (date == last_date) or (vaccinations <= previous_vaccinations):
    print(f"{country} data is up to date.")

    # Exit with a success code
    exit(0)

# Get population and relative country data
population = get_population(population, country)
data_normalized = get_data_hundred_people(data, population)

# Get the tweet string to publish in Twitter
try:
    tweet_string = get_tweet(country, data, data_normalized)
except ValueError:
    print(f"{country} data was not complete.")

    # Exit with a success code
    exit(0)

print(tweet_string)

try:
    tweet = api.update_status(tweet_string)
    #publish in telegram
    bot = telegram.Bot(token=telegram_api)
    status = bot.send_message(chat_id="@euCovidVaccination", text=tweet_string)
except tweepy.TweepError:
    print(f"Tweet already published.")
