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
from statistics import read_data, get_population, get_data_hundred_people
from tweet import get_tweet


# =============================================================================
# Arguments
# =============================================================================

description = "Publish vaccination data for a country."
parser = argparse.ArgumentParser(description=description)

arg = "--country"
parser.add_argument(arg)

arg = "--data"
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
dest = "access"
default = os.environ.get("BOT_ACCESS")
parser.add_argument(arg, default=default)

arg = "--access-secret"
dest = "access_secret"
default = os.environ.get("BOT_ACCESS_SECRET")
parser.add_argument(arg, default=default)

args = sys.argv[1:]
args = parser.parse_args(args)

# Rename the command line arguments for easier reference
country = args.country
data = args.data
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

# message = "The user credentials are "
# message = message + ("valid" if user else "invalid") + "."
# print(message)

# Get the vaccination data for the corresponding country
data = read_data(data, country)
population = get_population(population, country)
data = get_data_hundred_people(data, population)

# Get the tweet string to publish in Twitter
tweet_string = get_tweet(country, data)

print(tweet_string)

try:
    tweet = api.update_status(tweet_string)
except tweepy.TweepyException: 
    print(f"Tweet {tweet_string} already published.")
