import dash_core_components as dcc
import dash_html_components as html
import spotipy
from ..util.data_callbacks import *
from flask import session
import pandas as pd





df = pd.read_csv('.csv_caches/audio_feature_kmean.csv').drop(['Unnamed: 0'], axis=1)
playlists = list(df['playlist_name'].unique())
playlists_kv = [dict([('label', k), ('value', k)]) for k in playlists]


layout = html.Div([
    html.H1('Radar Example'),
    dcc.Dropdown(
        id='radar-dropdown',
        options=playlists_kv,
        value=playlists[0]
    ),

    dcc.Graph(id='radar-graph'),

    html.Div([
            'Test Text',

            dcc.Dropdown(
            id='spotify_me',
            options=[
                {'label': 'me', 'value': 'display_name'},
                {'label': 'href', 'value': 'href'},
            ],
            value='me'
        ),
        html.Div(id='my-h1')
    ]),

    html.Div([
            'Playlist',

            dcc.Dropdown(
            id='playlist_drop',
            options=playlists_kv,
            value=playlists,
            multi=True
        ),
        html.Div(id='playlists')
    ]),
    html.Div(
        children=[
            dcc.Graph(figure = display_era_plot(), id='graph-era'),
            html.Div(id="div-era-click", style={'float':'right'}),
        ],
        
    ),




], style={'width': '500'})
