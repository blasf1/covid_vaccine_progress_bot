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

# Local application
from tweet import get_tweet
from statistics import (read_data,
                        get_last_date,
                        get_population,
                        store_last_date,
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

# Get the vaccination data for the country
data = read_data(data, country)
date = data.index[-1]

if date == last_date:
    print(f"{country} data is up to date.")

    # Exit with a success code
    exit(0)

store_last_date(output, date, country)

# Get population and relative country data
population = get_population(population, country)
data = get_data_hundred_people(data, population)

# Get the tweet string to publish in Twitter
try:
    tweet_string = get_tweet(country, data)
except ValueError:
    print(f"{country} data was not complete.")

    # Exit with a success code
    exit(0)

print(tweet_string)

tweet = api.update_status(tweet_string)
