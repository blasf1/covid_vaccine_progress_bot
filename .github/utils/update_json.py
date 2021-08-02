# =============================================================================
# Imports
# =============================================================================
# Standard
import argparse
import os
import sys
import glob

import math
import pandas as pd
import json
import numpy as np
import datetime

# =============================================================================
# Constants
# =============================================================================
COUNTRIES = [
    "European Union",
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
    "Sweden",
    "Norway",
    "Iceland",
    "Switzerland",
    "United Kingdom",
    "United States",
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

def get_data_hundred_adults(data, path):
    """Get the vaccination data per hundred people."""
    # Filter the numerical data to avoid errors
    population = get_population(path, data["location"])
    numeric_columns = data.select_dtypes("number").columns.tolist()

    data[numeric_columns] = data[numeric_columns] * 100 / population

    return data

def get_days_to_70(data, parameter):
    """Get the rolling average of the vaccination data."""
    # Use one period for the rolling average
    periods = 1
    days = 7
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

    seven_days_average = difference.sum() / days

    return seven_days_average


def get_week_on_week(data, parameter):
    """Get the rolling average of the vaccination data."""
    # Use one period for the rolling average
    periods = 1
    days = 7
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
    difference = data_for_average.iloc[-1] - data_for_average.iloc[0]

    return difference


def read_data(path, path_population, path_adults):
    """Read the last vaccination data for all countries."""
    files = glob.glob(path + "*.csv")

    def read_csv(file):
        data = pd.read_csv(file)
        data_adults = data.copy()
        data["days_to_70"] = get_days_to_70(data, "people_fully_vaccinated")
        data["week_on_week"] = get_week_on_week(data, "people_fully_vaccinated")
        data = data.iloc[[-1]]
        data_adults = data_adults.iloc[[-1]]
        data = get_data_hundred_people(data, path_population)
        data_adults = get_data_hundred_adults(data_adults, path_adults)
        
        data["days_to_70"] = round(
            (70 - data["people_fully_vaccinated"]) / data["days_to_70"], 0)
        
        data["adults_fully_vaccinated"] = data_adults["people_fully_vaccinated"]
        data["adults_vaccinated"] = data_adults["people_vaccinated"]
        return data

    data = pd.concat(map(read_csv, files))
    columns = ["date", "location", "people_vaccinated",
               "people_fully_vaccinated", "total_vaccinations", "adults_fully_vaccinated", "adults_vaccinated", "days_to_70", "week_on_week"]
    data = data[columns]
    return data.set_index("location").round(2)


def sort_values_dict(dict, sort_by="people_fully_vaccinated"):
    countries = [country for country in dict]
    values = [dict[country][sort_by] for country in dict]
    index_sorted = np.argsort(-np.array(values))
    return list(np.array(countries)[index_sorted])


def get_dict_vaccination_per_country(df):
    dict_people_vaccinated = {"data": {}}
    for country in COUNTRIES:
        people_vaccinated = df["people_vaccinated"][country]
        people_fully_vaccinated = df["people_fully_vaccinated"][country]
        days_to_70 = df["days_to_70"][country]
        date = df["date"][country]
        week_on_week = df["week_on_week"][country]
        adults_vaccinated = df["adults_vaccinated"][country]
        adults_fully_vaccinated = df["adults_fully_vaccinated"][country]
        dict_people_vaccinated["data"][country] = {"people_vaccinated": people_vaccinated,
                                                   "people_fully_vaccinated": people_fully_vaccinated,
                                                   "days_to_70": days_to_70,
                                                   "date":date,
                                                   "week_on_week":week_on_week,
                                                   "adults_vaccinated":adults_vaccinated,
                                                   "adults_fully_vaccinated":adults_fully_vaccinated}
    dict_people_vaccinated["countries_sorted"] = sort_values_dict(
        dict_people_vaccinated["data"])
    dict_people_vaccinated["max_date"] = df.date.max()
    return dict_people_vaccinated


def export_dict_people_vaccinated(data, path):
    file = open(path, "w")
    file.write(json.dumps(data))


def export_csv(data, path):
    data.to_csv(path)


# =============================================================================
# Arguments
# =============================================================================
description = "Publish vaccination data for a country."
parser = argparse.ArgumentParser(description=description)

arg = "--data"
default = os.environ.get("DATA")
parser.add_argument(arg, default=default)

arg = "--noeudata"
default = os.environ.get("NOEUDATA")
parser.add_argument(arg, default=default)

arg = "--output"
default = os.environ.get("OUTPUT")
parser.add_argument(arg, default=default)

arg = "--csv"
default = os.environ.get("CSV")
parser.add_argument(arg, default=default)

arg = "--population"
default = os.environ.get("POPULATION")
parser.add_argument(arg, default=default)

arg = "--adults"
default = os.environ.get("ADULTS")
parser.add_argument(arg, default=default)

args = sys.argv[1:]
args = parser.parse_args(args)

# Rename the command line arguments for easier reference
data = args.data
noeudata = args.noeudata
output = args.output
csv = args.csv
population = args.population
adults = args.adults


# =============================================================================
# Main
# =============================================================================

data = read_data(data, population, adults)
data_ext = read_data(noeudata, population, adults)
print(data_ext)
dataframes = [data, data_ext]
data = pd.concat(dataframes)
print(data)
data.replace([np.inf, -np.inf], 0, inplace=True)
export_csv(data, csv)
data = get_dict_vaccination_per_country(data)
export_dict_people_vaccinated(data, output)
