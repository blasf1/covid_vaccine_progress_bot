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

COUNTRIES_WITHOUT_FULL_DATA = [
    "Luxembourg"
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

    # if(data["location"].iloc[-1] == "Hungary"):
    #    return 0

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

    try:
        difference = data_for_average.iloc[-1] - data_for_average.iloc[0]
    except IndexError:
        print("not available")
        difference = 0

    return difference


def read_data(path, path_population, path_adults):
    """Read the last vaccination data for all countries."""
    files = glob.glob(path + "*.csv")

    def read_csv(file):
        data = pd.read_csv(file)
        print(file)
        print(data)
        data["people_vaccinated"].fillna(
            data["people_fully_vaccinated"], inplace=True)
        data = data.ffill()
        data_adults = data.copy()
        data["days_to_70"] = get_days_to_70(data, "people_fully_vaccinated")
        data["week_on_week"] = get_week_on_week(
            data, "people_fully_vaccinated")

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
               "people_fully_vaccinated", "total_vaccinations",
               "adults_fully_vaccinated", "adults_vaccinated",
               "days_to_70", "week_on_week", "total_boosters"]
    data = data[columns]
    return data.set_index("location").round(1)


def read_data_past(path, path_population, path_adults):
    files = glob.glob(path + "*.csv")

    def read_csv(file):
        data_prev = pd.read_csv(file)
        data_prev = data_prev.drop(index=data_prev.index[-1], axis=0)
        if data["people_vaccinated"].iloc[-1] < data["people_fully_vaccinated"].iloc[-1]:
            data["people_vaccinated"].iloc[-1] = data["people_fully_vaccinated"].iloc[-1]
        data_adults = data_prev.copy()
        data_prev["days_to_70"] = get_days_to_70(
            data_prev, "people_fully_vaccinated")

        data_prev["week_on_week"] = get_week_on_week(
            data_prev, "people_fully_vaccinated")

        data_prev = data_prev.iloc[[-1]]
        data_adults = data_adults.iloc[[-1]]
        data_prev = get_data_hundred_people(data_prev, path_population)
        data_adults = get_data_hundred_adults(data_adults, path_adults)

        data_prev["days_to_70"] = round(
            (70 - data_prev["people_fully_vaccinated"]) / data_prev["days_to_70"], 0)

        data_prev["adults_fully_vaccinated"] = data_adults["people_fully_vaccinated"]
        data_prev["adults_vaccinated"] = data_adults["people_vaccinated"]
        return data_prev

    data_prev = pd.concat(map(read_csv, files))
    columns = ["date", "location", "people_vaccinated",
               "people_fully_vaccinated", "total_vaccinations",
               "adults_fully_vaccinated", "adults_vaccinated",
               "days_to_70", "week_on_week", "total_boosters"]
    data_prev = data_prev[columns]

    return data_prev.set_index("location")


def get_increments(data, data_prev):
    data["people_vaccinated_increment"] = data["people_vaccinated"] - \
        data_prev["people_vaccinated"]
    data["people_fully_vaccinated_increment"] = data["people_fully_vaccinated"] - \
        data_prev["people_fully_vaccinated"]
    data["days_to_70_increment"] = data["days_to_70"] - data_prev["days_to_70"]
    data["week_on_week_increment"] = data["week_on_week"] - \
        data_prev["week_on_week"]
    data["adults_vaccinated_increment"] = data["adults_vaccinated"] - \
        data_prev["adults_vaccinated"]
    data["adults_fully_vaccinated_increment"] = data["adults_fully_vaccinated"] - \
        data_prev["adults_fully_vaccinated"]
    data["total_boosters_increment"] = data["total_boosters"] - \
        data_prev["total_boosters"]
    data = data.fillna(0)
    return data.round(1)


def sort_values_dict(dict, sort_by="people_fully_vaccinated"):
    countries = [country for country in dict]
    values = [dict[country][sort_by] for country in dict]
    index_sorted = np.argsort(-np.array(values))
    return list(np.array(countries)[index_sorted])


def get_dict_vaccination_per_country(df):
    dict_people_vaccinated = {"data": {}}

    for country in COUNTRIES:
        dict_people_vaccinated["data"][country] = {"people_vaccinated": df["people_vaccinated"][country],
                                                   "people_fully_vaccinated": df["people_fully_vaccinated"][country],
                                                   "days_to_70": df["days_to_70"][country],
                                                   "date": df["date"][country],
                                                   "week_on_week": df["week_on_week"][country],
                                                   "adults_vaccinated": df["adults_vaccinated"][country],
                                                   "adults_fully_vaccinated": df["adults_fully_vaccinated"][country],
                                                   "people_vaccinated_increment": df["people_vaccinated_increment"][country],
                                                   "people_fully_vaccinated_increment": df["people_fully_vaccinated_increment"][country],
                                                   "days_to_70_increment": df["days_to_70_increment"][country],
                                                   "week_on_week_increment": df["week_on_week_increment"][country],
                                                   "adults_vaccinated_increment": df["adults_vaccinated_increment"][country],
                                                   "adults_fully_vaccinated_increment": df["adults_fully_vaccinated_increment"][country],
                                                   "total_boosters": df["total_boosters"][country]}
        if country in COUNTRIES_WITHOUT_FULL_DATA:
            dict_people_vaccinated["data"][country]["people_fully_vaccinated"] = 0
            dict_people_vaccinated["data"][country]["adults_fully_vaccinated"] = 0

    dict_people_vaccinated["countries_sorted"] = sort_values_dict(
        dict_people_vaccinated["data"])
    dict_people_vaccinated["lat_update"] = datetime.datetime.now().strftime(
        "%Y-%m-%d")
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
path_data = args.data
path_noeudata = args.noeudata
output = args.output
csv = args.csv
population = args.population
adults = args.adults


# =============================================================================
# Main
# =============================================================================

# read data
data = read_data(path_data, population, adults)
data_ext = read_data(path_noeudata, population, adults)
dataframes = [data, data_ext]
data = pd.concat(dataframes)
#data["people_vaccinated"].apply(lambda x : x if x >= data["people_fully_vaccinated"] else data["people_fully_vaccinated"])
print(data)
# read data of t-1
data_past = read_data_past(path_data, population, adults)
data_ext_past = read_data_past(path_noeudata, population, adults)
dataframes = [data_past, data_ext_past]
data_past = pd.concat(dataframes)
print(data_past)
data = get_increments(data, data_past)
print(data)

data.replace([np.inf, -np.inf], 0, inplace=True)
export_csv(data, csv)
data = get_dict_vaccination_per_country(data)
export_dict_people_vaccinated(data, output)
