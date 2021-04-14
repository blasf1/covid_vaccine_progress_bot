from collections import defaultdict
import datetime

import configargparse as cap
import tweepy
from tqdm import tqdm
import pandas as pd
import pycountry_convert as pc
import flag

argparser = cap.ArgParser(default_config_files=['keys.yml'])
argparser.add('-c', is_config_file=True, help='config file path')
argparser.add('--api', env_var='BOT_API')
argparser.add('--api-secret', env_var='BOT_API_SECRET')
argparser.add('--access', env_var='BOT_ACCESS')
argparser.add('--access-secret', env_var='BOT_ACCESS_SECRET')

args = argparser.parse_args()

# Authenticate to Twitter
auth = tweepy.OAuthHandler(args.api, args.api_secret)
auth.set_access_token(args.access, args.access_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")

# get current percentage
data = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv', parse_dates=['date'])

data_filtered = data[data.location == 'European Union']
data_filtered = data_filtered[data_filtered.date == data_filtered.date.max()]

# take last item in case dataset contains multiple items this day:
percentage = data_filtered.iloc[-1].people_vaccinated_per_hundred

def tweet_bar_string_from_percentage(percentage, country, bar_format='|{bar:10}| {percentage:04.1f}% COUNTRY'):
    bar = tqdm(initial=percentage, total=100., bar_format=bar_format, ascii=False)
    bar_string = str(bar)
    bar.close()
    bar_separator_ix = bar_string.rfind('|')
    tweet_string = bar_string[:bar_separator_ix].replace(' ', '\u3000') + bar_string[bar_separator_ix:]
    tweet_string = tweet_string.replace('COUNTRY', flag.flagize(country))
    return tweet_string

tweet_string = "People vaccinated with at least one dose\n" + tweet_bar_string_from_percentage(percentage, ":EU:") + '\n'

total_pop = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/scripts/input/un/population_2020.csv')

supported_countries = {'Germany':":DE::EU:", 'France':":FR::EU:", 'Italy':":IT::EU:", \
                        'Spain':":ES::EU:", 'Poland':":PL::EU:", 'Romania':":RO::EU:", \
                        'Netherlands':":NL::EU:", 'Belgium':":BE::EU:", 'Greece':":GR::EU:", \
                        'Czechia':":CZ::EU:", 'Portugal':":PT::EU:", 'Sweden':":SE::EU:", \
                        'Hungary':":HU::EU:",'Austria':":AT::EU:", 'Bulgaria':":BG::EU:", \
                        'Denmark':":DK::EU:", 'Finland':":FI::EU:", 'Slovakia':":SK::EU:",\
                        'Ireland':":IE::EU:", 'Croatia':":HR::EU:", 'Lithuania':":LT::EU:",\
                        'Slovenia':":SI::EU:", 'Latvia':":LV::EU:", 'Estonia':":EE::EU:", \
                        'Cyprus':":CY::EU:", 'Luxembourg':":LU::EU:", 'Malta':":MT::EU:"}
countries_percentages = {}
strings = {}
previous_tweet = 0
for country, emoji in supported_countries.items():
    data_filtered = data[data.location == country]
    data_filtered = data_filtered[data_filtered.date == data_filtered.date.max()]
    countries_percentages[country] = data_filtered.iloc[-1].people_vaccinated_per_hundred
    tweet_string_add = tweet_bar_string_from_percentage(countries_percentages[country], emoji)
    tweet_string = tweet_string + "\n" + tweet_string_add
    if len(tweet_string) > 180:
        if previous_tweet == 0:
            previous_tweet = api.update_status(tweet_string)
        else:
            previous_tweet= api.update_status(status=tweet_string, in_reply_to_status_id=previous_tweet.id, auto_populate_reply_metadata=True)
        print(tweet_string)
        tweet_string = ""

print(tweet_string)
previous_tweet= api.update_status(status=tweet_string, in_reply_to_status_id=previous_tweet.id, auto_populate_reply_metadata=True)

data_filtered = data[data.location == 'European Union']
data_filtered = data_filtered[data_filtered.date == data_filtered.date.max()]
percentage = data_filtered.iloc[-1].people_fully_vaccinated_per_hundred
tweet_string_2 = "\nPeople fully vaccinated (2 doses)\n" + tweet_bar_string_from_percentage(percentage, ":EU:") + '\n'

countries_percentages = {}
strings = {}
previous_tweet = 0
for country, emoji in supported_countries.items():
    data_filtered = data[data.location == country]
    data_filtered = data_filtered[data_filtered.date == data_filtered.date.max()]
    countries_percentages[country] = data_filtered.iloc[-1].people_fully_vaccinated_per_hundred
    tweet_string_add = tweet_bar_string_from_percentage(countries_percentages[country], emoji)
    tweet_string_2 = tweet_string_2 + "\n" + tweet_string_add
    if len(tweet_string_2) > 180:
        if previous_tweet == 0:
            previous_tweet = api.update_status(tweet_string_2)
        else:
            print("Reply to previous tweet")
            previous_tweet= api.update_status(status=tweet_string_2, in_reply_to_status_id=previous_tweet.id, auto_populate_reply_metadata=True)
        print(tweet_string_2)
        tweet_string_2 = ""

print(tweet_string_2)
previous_tweet= api.update_status(status=tweet_string_2, in_reply_to_status_id=previous_tweet.id, auto_populate_reply_metadata=True)
