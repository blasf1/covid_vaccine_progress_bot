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

def read_data(path, country, local_path):
    """Read the vaccination data for a country."""
    # Use the date to identify the vaccination data
    path = os.path.join(path, country.replace(" ", "") + ".csv")
    local_path = os.path.join(local_path, country.replace(" ", "") + ".csv")

    index_col = "date"
    data = pd.read_csv(path, index_col = index_col)  
    data_local = pd.read_csv(local_path, index_col = index_col)
    
    if data_local.index[-1] != data.index[-1]:
        data = data_local.append(data.iloc[-1])

    # Debugging, delete after
    return data


def read_data_unsupported(file, country, path):
    """Read the vaccination data for a non automated country."""
    index_col = "date"
    #Join previous stored data to the last update
    data = pd.read_csv(file, index_col = index_col)    
    data = data[data.location == country]
    data = data[["total_vaccinations", "people_vaccinated", "people_fully_vaccinated", "location"]]

    return data


def get_last_date(path, country):
    """Get the last date when the data was published."""
    path = os.path.join(path, country.replace(" ", "") + ".csv")
    data = pd.read_csv(path)

    return data.date.iloc[-1]


def get_previous_vaccinations(path, country):
    """Get the last date when the data was published."""
    path = os.path.join(path, country.replace(" ", "") + ".csv")
    data = pd.read_csv(path)

    return data.people_vaccinated.iloc[-1]

def clean_first_doses(data):
    """If people_vaccinated not available, """

    if data["people_vaccinated"].iloc[-1] < data["people_fully_vaccinated"].iloc[-1]:
        data["people_vaccinated"].iloc[-1] = data["people_fully_vaccinated"].iloc[-1]

    return data


def store_last_data(path, country, data):
    """Store the last date when the data was published."""
    path = os.path.join(path, country.replace(" ", "") + ".csv")
    #Store only the new line
    #data_to_store = data.iloc[[-1]]

    #Read the file
    index_col = "date"
    data_in_file = pd.read_csv(path, index_col=index_col)

    # Store only if updates available
    if data_in_file.index[-1] != data.index[-1]:#data_to_store.index[-1]:
        #data_to_store = data_in_file.append(data_to_store)
        index = True
        #data_to_store.to_csv(path, index=index)
        data.to_csv(path,index=index)


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

    date_limit = data_for_average.iloc[-1]["date"] - datetime.timedelta(days = days + 1) #data_for_average.iloc[-1]["date"] - data_for_average.iloc[0]["date"]

    data_for_average = data_for_average[data_for_average["date"] > date_limit]  

    data_for_average = data_for_average[parameter]

    data_for_average = data_for_average.dropna() #remove empty rows for diff()
    difference = data_for_average.diff(periods)
    
    return (difference.sum() / days)



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
    print("yesterday ")
    print(shift_average_week)
    print("today ")
    print(average_week)
    return average_week - shift_average_week


def is_record(data, parameter):
    """Returns true if todays data is the highest for the given parameter"""
    data_with_dates = data
    data_with_dates["date"] = data_with_dates.index #Take indexes as column
    data_with_dates = data_with_dates[["date", parameter]]
    data_with_dates["date"] = pd.to_datetime(data_with_dates["date"], format='%Y-%m-%d')
    
    increments = data_with_dates.diff()
    last_interval = increments["date"].iloc[-1]

    #Drop rows where day increment is not 1. Daily record won't count then (it's not daily)
    increments = increments[increments['date'] == datetime.timedelta(days = 1)]

    try:
        today = increments[parameter].iloc[-1]
    except IndexError:
        return False

    maximum = increments[parameter].max()

    return today == maximum and last_interval == datetime.timedelta(days = 1)

def get_days_reported(data):
    """Returns true if todays data is the highest for the given parameter"""
    data_dates = data
    data_dates["date"] = data_dates.index #Take indexes as column
    data_dates = data_dates[["date"]]
    data_dates["date"] = pd.to_datetime(data_dates["date"], format='%Y-%m-%d')
    
    increments = data_dates.diff()

    return increments["date"].iloc[-1]