# Standard
import argparse
import os
import sys
import glob

import plotly.graph_objs as go
import pandas as pd
import base64
# =============================================================================
# Constants
# =============================================================================

# Map the country name to the country flag
FLAGS = {
    "European Union": "EU",
    "Austria": "AT",
    "Belgium": "BE",
    "Bulgaria": "BG",
    "Croatia": "HR",
    "Cyprus": "CY",
    "Czechia": "CZ",
    "Denmark": "DK",
    "Estonia": "EE",
    "Finland": "FI",
    "France": "FR",
    "Germany": "DE",
    "Greece": "GR",
    "Hungary": "HU",
    "Ireland": "IE",
    "Italy": "IT",
    "Latvia": "LV",
    "Lithuania": "LT",
    "Luxembourg": "LU",
    "Malta": "MT",
    "Netherlands": "NL",
    "Poland": "PL",
    "Portugal": "PT",
    "Romania": "RO",
    "Slovakia": "SK",
    "Slovenia": "SI",
    "Spain": "ES",
    "Sweden": "SE"}

# =============================================================================
# Functions
# =============================================================================

def read_data(path):
    return pd.read_csv(path).sort_values(by="people_vaccinated")

def get_flag(code, flags):
    """Gets flag icon"""
    path = os.path.join(flags + code + ".png")
    img = plt.imread(path)
    img = OffsetImage(img, zoom=0.2)

    return img
    

def get_graph(data):
    fig = go.Figure(data = [
        go.Bar(name="Fully vaccinated", 
               y=data["location"], 
               x=data["people_fully_vaccinated"], 
               text=data["people_fully_vaccinated"], 
               marker_color="#3C4E66", 
               orientation="h",
               textposition='inside',
               textfont=dict(color='#FFFFFF')
        ), 
        go.Bar(name="Partly vaccinated", 
               y=data["location"], 
               x=(data["people_vaccinated"] - data["people_fully_vaccinated"]), 
               text=round((data["people_vaccinated"] - data["people_fully_vaccinated"]), 2), 
               marker_color="#1f77b4", 
               orientation="h",
               textposition='inside',
               textfont=dict(color='#FFFFFF')
        ),
    ])

    fig.update_layout(barmode='stack', plot_bgcolor="#FFFFFF", xaxis = dict(fixedrange=True, showgrid = True, gridcolor = "#293133", zeroline = True))
    return fig
    

def add_flags(fig, data):
    #Country flags
    for country, i in zip(data["location"], range(len(data["location"]))):
        flag = base64.b64encode(open('../../flags/' + FLAGS[country] + '.png', 'rb').read())
        fig.add_layout_image(
            source='data:image/png;base64,{}'.format(flag.decode()),
            xref="paper",
            yref="paper",
            x=-0.025,
            y=(i/len(data["location"])),
            xanchor="center",
            yanchor="bottom",
            sizex=0.035,
            sizey=0.035,
        )
    return fig
    
def add_labels(fig, data):
    #Country flags
    for country, i in zip(data["location"], range(len(data["location"]))):
        flag = base64.b64encode(open('../../flags/' + FLAGS[country] + '.png', 'rb').read())
        fig.add_layout_image(
            source='data:image/png;base64,{}'.format(flag.decode()),
            xref="paper",
            yref="paper",
            x=-0.025,
            y=(i/len(data["location"])),
            xanchor="center",
            yanchor="bottom",
            sizex=0.04,
            sizey=0.04,
        )
    return fig

def format_graph(fig, data):
    #Remove old labels
    l = [""] * 100
    fig.update_yaxes(tickvals=l)

    #Country flags
    add_flags(fig, data)

    # % labels

    fig.show()

# =============================================================================
# Arguments
# =============================================================================
description = "Publish vaccination data for a country."
parser = argparse.ArgumentParser(description=description)

arg = "--data"
default = os.environ.get("DATA")
parser.add_argument(arg, default=default)

# arg = "--output"
# default = os.environ.get("OUTPUT")
# parser.add_argument(arg, default=default)

# arg = "--csv"
# default = os.environ.get("CSV")
# parser.add_argument(arg, default=default)

# arg = "--population"
# default = os.environ.get("POPULATION")
# parser.add_argument(arg, default=default)

args = sys.argv[1:]
args = parser.parse_args(args)

# Rename the command line arguments for easier reference
data = args.data
# output = args.output
# csv = args.csv
# population = args.population

# =============================================================================
# Main
# =============================================================================

data = read_data(data)
print(data)
fig = get_graph(data)
fig = format_graph(fig, data)