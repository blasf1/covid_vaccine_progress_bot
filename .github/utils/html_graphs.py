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
    "Sweden": "SE",
    "Norway": "NO",
    "Iceland": "IS",
    "Switzerland": "CH",
    "United Kingdom": "UK",
    "United States": "US"}

NON_EU = {
    "Norway": "NO",
    "Iceland": "IS",
    "Switzerland": "CH",
    "United Kingdom": "UK",
    "United States": "US"
}
# =============================================================================
# Functions
# =============================================================================

def read_data(path):
    return pd.read_csv(path).sort_values(by="people_vaccinated")
    
def get_color(country, parameter):
    if country in NON_EU:
        if parameter is "people_fully_vaccinated":
            return "#9B9B9B"
        else:
            return "#BCBCBD"
    else:
        if parameter is "people_fully_vaccinated":
            return "#3C4E66"
        else:
            return "#1f77b4"

def get_graph(data):
    data["color1"] = [get_color(x,"people_fully_vaccinated") for x in data["location"]]
    data["color2"] = [get_color(x,"people_vaccinated") for x in data["location"]]
    fig = go.Figure(data = [
        go.Bar(name="Fully vaccinated", 
               y=data["location"], 
               x=data["people_fully_vaccinated"], 
               text=data["people_fully_vaccinated"], 
               marker_color=data["color1"], 
               orientation="h",
               textposition='inside',
               textfont=dict(color='#FFFFFF')
        ), 
        go.Bar(name="Partly vaccinated", 
               y=data["location"], 
               x=(data["people_vaccinated"] - data["people_fully_vaccinated"]), 
               text=round((data["people_vaccinated"] - data["people_fully_vaccinated"]), 2), 
               marker_color=data["color2"], 
               orientation="h",
               textposition='auto',
               textfont=dict(color='#FFFFFF')
        ),
    ])

    fig.update_layout(barmode='stack', 
                      plot_bgcolor="#FFFFFF", 
                      xaxis = dict(
                          range=[0,100],
                          fixedrange=True, 
                          showgrid = True, 
                          showline=True,
                          gridcolor = "#293133", 
                          zeroline = True
                      ),
                      yaxis=dict(
                          linecolor='#293133',
                          mirror=True,
                          fixedrange=True
                      ),
                      legend=dict(
                          yanchor="bottom",
                          xanchor="right",
                          y=0,
                      ),
                      #width=700,
                      height=700,
                      margin=dict(l=50, r=0, t=0, b=0),
                      )

    return fig
    

def add_flags(fig, data, flags):
    #Country flags
    for country, i in zip(data["location"], range(len(data["location"]))):
        path = os.path.join(flags, FLAGS[country] + '.png')
        flag = base64.b64encode(open(path, 'rb').read())
        fig.add_layout_image(
            source='data:image/png;base64,{}'.format(flag.decode()),
            xref="x domain",
            yref="y domain",
            x= - 0.002,
            y=(i/len(data["location"]) - 0.0015),
            xanchor="right",
            yanchor="bottom",
            sizex=0.035,
            sizey=0.035,
            layer="above"
        )
    return fig
    
def add_labels(fig, data):
    #Country flags
    for i, text in zip(range(len(data["location"])), data["people_vaccinated"]):
        fig.add_annotation(
            xref="x",
            yref="y domain",
            # The arrow head will be 25% along the x axis, starting from the left
            y=(i/len(data["location"]) + 0.015),
            ay=(i/len(data["location"])),
            # The arrow head will be 40% along the y axis, starting from the bottom
            x=(text+1.5),
            xanchor="left",
            yanchor="middle",
            text=text,
            font=dict(family="Arial", size=12, color="#000000")
        )
    return fig

def format_graph(fig, data, flags):
    #Remove old labels
    l = [""] * 100
    fig.update_yaxes(tickvals=l)

    #Country flags
    add_flags(fig, data, flags)

    # % labels
    add_labels(fig,data)

    return fig

def save_graph(fig,output):
    fig.write_html(output, config=dict(displayModeBar=False))

# =============================================================================
# Arguments
# =============================================================================
description = "Publish vaccination data for a country."
parser = argparse.ArgumentParser(description=description)

arg = "--data"
default = os.environ.get("DATA")
parser.add_argument(arg, default=default)

arg = "--output"
default = os.environ.get("OUTPUT")
parser.add_argument(arg, default=default)

arg = "--flags"
default = os.environ.get("FLAGS")
parser.add_argument(arg, default=default)

# arg = "--population"
# default = os.environ.get("POPULATION")
# parser.add_argument(arg, default=default)

args = sys.argv[1:]
args = parser.parse_args(args)

# Rename the command line arguments for easier reference
data = args.data
output = args.output
flags = args.flags
# population = args.population

# =============================================================================
# Main
# =============================================================================

data = read_data(data)
print(data)
data["people_vaccinated"].fillna(data["people_fully_vaccinated"], inplace=True)
fig = get_graph(data)
fig = format_graph(fig, data, flags)
save_graph(fig, output)