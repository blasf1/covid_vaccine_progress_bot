"""Statistics for a particular vaccination data parameter of a country."""


# =============================================================================
# Imports
# =============================================================================

# Standard
import os
import sys

# Third party
import numpy as np
import pandas as pd
import datetime

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
    
    data = data[parameter]

    # Use one period for the rolling average
    periods = 1

    # Substract one day to count the last day
    days = -days - 1

    difference = data.iloc[days:].diff(periods)

    return np.mean(difference)


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
