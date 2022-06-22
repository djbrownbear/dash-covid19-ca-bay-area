
from operator import index
import pandas as pd
import numpy as np
import requests
import io

import os,time,re
import shutil
from datetime import datetime as dt, timedelta

# graphing libraries & dependencies
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html

# Fix: downloading the csv file from your GitHub account
# Thanks to source: https://medium.com/towards-entrepreneurship/importing-a-csv-file-from-github-in-a-jupyter-notebook-e2c28e7e74a5
url = 'https://raw.githubusercontent.com/djbrownbear/dash-covid19-ca-bay-area/main/NumberCases.csv'
download = requests.get(url).content

# Reading the downloaded content and turning it into a pandas dataframe
df = pd.read_csv(io.StringIO(download.decode('utf-8')),index_col=0)

# cleanup - convert date to datetime object
df.index = pd.to_datetime(df.index)
df.sort_index(inplace=True)

# normalize date for graphing
df.index = df.index.normalize()

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__)
server = app.server

# create unique list of all counties, used in dropdown menu
all_counties = tuple(df['County'].unique())
all_counties = all_counties + ('All',)

# create unique list of all cities, grouped by county, used in dropdown menu
all_options = {}


def get_county_cities():
    for c in all_counties:
       all_options[c] = tuple(df.loc[df['County'] == c, 'Location'].unique())
    all_options['All'] = tuple(df.loc[:, 'Location'].unique())

get_county_cities()

max_date = df.index.max()
last_30 = max_date-timedelta(days=30)
ytd = dt(max_date.year, 1, 1)

app.layout = html.Div(id='app-container',
    children=[
    html.Header(html.H1('Covid-19 Case Tracker')),

    html.Div(id='dropdown-menu-container',
        className='box-main',
        children=[
            html.Div(id='dropdown-counties',
                children=[
                    html.Label('County'),
                    dcc.Dropdown(
                        options=[
                            dict(label=str(i), value=str(i).strip()) for i in all_counties
                        ],
                        value='All',
                        multi=False,
                        clearable=False,
                        id='county-dropdown-options',
                    )], style={'width': '24%', 'display': 'inline-block'}),

            html.Div(id='dropdown-cities',
                children=[
                    html.Label('Cities'),
                    dcc.Dropdown(
                        multi=True,
                        id='city-dropdown-options',
                    )], style={'width': '72%', 'display': 'inline-block'}),
    ]),

    html.Div(id='radio-buttons-time',
        children=[
            html.Label('Filter by Time Period'),
            dcc.RadioItems(
                ['All', 'Last 30 Days', 'YTD'],
                'All',
                id='date-type',
                inline=True,
            )
    ]),
    html.Div(
        id='graph-container',
        children=[
            dcc.Graph(id='graph-cases', figure=go.Figure()),
        ]),
    html.Footer(
        children=[
            html.P(
                html.A(
                    href='https://github.com/djbrownbear/dash-covid19-ca-bay-area',
                    className='icon brands fa-github',
                    target='_blank')),
            html.P("By Aaron Brown"),
    ]),
])


@app.callback(Output('city-dropdown-options', 'options'),
              [Input('county-dropdown-options', 'value')]
              )
def set_cities_options(selected_county):
    return [{'label': i, 'value': i} for i in all_options[selected_county]]


@app.callback(Output('city-dropdown-options', 'value'),
              [Input('city-dropdown-options', 'options')]
              )
def set_cities_options(available_options):
    return available_options


@app.callback(Output('graph-cases', 'figure'),
              Input('county-dropdown-options', 'value'),
              Input('city-dropdown-options', 'value'),
              Input('date-type', 'value')
              )
def update_figure(county_value, cities_value, date_type):

    # handle default for county selection, show all cities
    if len(list(cities_value)) == 0:
        if county_value == 'All':
            d = df.copy()
        else:
            d = df.loc[(df['County'] == county_value), :]
    else:
        d = df.loc[(df['Location']).isin(list(cities_value)), :]

    # handle filter by time periods
    if date_type == 'Last 30 Days':
        filtered_df = d.loc[(d.index >= last_30) & (d.index <= max_date), :]
    elif date_type == 'YTD':
        filtered_df = d.loc[(d.index >= ytd) & (d.index <= max_date), :]
    else:
        filtered_df = d.copy()

    fig = go.Figure()

    # build graphs based on user input
    for index, location in enumerate(filtered_df['Location'].unique()):

        graph_target = 'Cases Last 14 Days'
        f = filtered_df.loc[filtered_df['Location']== location,
                             [graph_target, 'Location']]

        fig.add_trace(
            go.Scatter(
                x=f.index,
                y=f[graph_target].values,
                name=location
            )
        )

    fig.update_layout(
        paper_bgcolor='#353333',
        plot_bgcolor='#353333',
        font_color='#ffffff',
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=False)
