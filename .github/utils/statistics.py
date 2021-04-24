"""Statistics for a particular vaccination data parameter of a country."""


# =============================================================================
# Imports
# =============================================================================

# Standard
import datetime
import os
import sys

# Third party
import numpy as np
import pandas as pd


# =============================================================================
# Functions
# =============================================================================

def read_data(path, country):
    """Read the vaccination data for a country."""
    # Use the date to identify the vaccination data
    path = os.path.join(path, country + ".csv")

    index_col = "date"
    data = pd.read_csv(path, index_col=index_col)

    return data


def read_data_unsupported(country, file):
    """Read the vaccination data for a non automated country."""
    index_col = "date"
    data = pd.read_csv(file, index_col=index_col)

    data = data[data.location == country]
    data = data[["total_vaccinations", "people_vaccinated", "people_fully_vaccinated"]]
    return data


def get_last_date(path, country):
    """Get the last date when the data was published."""
    path = os.path.join(path, country.replace(" ", "") + ".csv")
    data = pd.read_csv(path)

    return data.date.iloc[-1]


def store_last_date(path, date, country):
    """Store the last date when the data was published."""
    path = os.path.join(path, country.replace(" ", "") + ".csv")
    data = pd.read_csv(path)

    data.date.iloc[-1] = date

    index = False
    data.to_csv(path, index=index)


def get_population(path, country):
    """Get the population for a country."""
    # Use the country to identify the population data
    index_col = "entity"
    data = pd.read_csv(path, index_col=index_col)

    return data.loc[country].population


def get_data_hundred_people(data, population):
    """Get the vaccination data per hundred people."""
    # Filter the numerical data to avoid errors
    data = data.select_dtypes("number")

    return data * 100 / population


def get_current_data(data, parameter):
    """Get the current vaccination data."""
    return data[parameter].iloc[-1]


def get_current_data_increment(data, parameter):
    """Get the current vaccination data increment."""
    # Shift the data one day to compute the vaccination data increment
    periods = 1
    shift_data = data.shift(periods)

    current_data = get_current_data(data, parameter)
    shift_current_data = get_current_data(shift_data, parameter)

    return current_data - shift_current_data


def get_rolling_average(data, parameter, days):
    """Get the rolling average of the vaccination data."""
    # Use one period for the rolling average
    periods = 1
    data_for_average = data.tail(days + 1) #keep days + 1 so that diff can cçompare with the last day out of the average
    data_for_average.reset_index(inplace=True)
    data_for_average["date"] = pd.to_datetime(data_for_average["date"], format='%Y-%m-%d')

    interval = data_for_average.iloc[-1]["date"] - data_for_average.iloc[0]["date"]
    print("Interval is " + str(interval))

    if interval.days > (days):
        new_last_date = data_for_average.iloc[0]["date"] - interval
        print(new_last_date)
        data_for_average = data_for_average[data_for_average["date"] > new_last_date]  

    # Substract one day to count the last day
    print("Data for average")
    print(data_for_average)
    data_for_average = data_for_average[parameter]
    difference = data_for_average.diff(periods)
    
    print(difference)
    return (difference.sum() / days)


def get_rolling_average_day(data, parameter):
    """Get the rolling average of the vaccination data for one day."""
    days = 1

    return get_rolling_average(data, parameter, days)


def get_rolling_average_day_increment(data, parameter):
    """Get the rolling average increment of the vaccination data for one day."""
    # Shift the data one day to compute the increment for one day
    periods = 1
    shift_data = data.shift(periods)

    average_day = get_rolling_average_day(data, parameter)
    shift_average_day = get_rolling_average_day(shift_data, parameter)

    return average_day - shift_average_day


def get_rolling_average_week(data, parameter):
    """Get the rolling average of the vaccination data for one week."""
    days = 7

    return get_rolling_average(data, parameter, days)


def get_rolling_average_week_increment(data, parameter):
    """Get the rolling average increment of the vaccination data for one week."""
    # Shift the data one day to compute the increment for one week
    periods = 1
    shift_data = data.shift(periods)

    average_week = get_rolling_average_week(data, parameter)
    shift_average_week = get_rolling_average_week(shift_data, parameter)

    return average_week - shift_average_week
