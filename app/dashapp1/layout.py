import dash_core_components as dcc
import dash_html_components as html
import spotipy
from ..util.data_callbacks import *
from flask import session
import pandas as pd
import json

df = pd.read_csv('.csv_caches/audio_feature_kmean.csv').drop(['Unnamed: 0'], axis=1)
playlists = list(df['playlist_name'].unique())
playlists_kv = [dict([('label', k), ('value', k)]) for k in playlists]

top_5_artists = pd.read_csv('.csv_caches/top_5_artists.csv')
artist_images = [json.loads(url.replace("'", '"'))[0]['url'] for url in top_5_artists['images']]
def generate_image_column(artist_images, idx):
    return html.Div([
        html.Img(src=artist_images[idx], style={
            'margin-top': '8px',
            'vertical-align': 'middle',
            'width': '100%',
        })
    ], style={
        'flex': '25%',
        'max-width': '25%',
        'padding': '0 4px',
        'margin-top': '8px',
        'vertical-align': 'middle',
        'width': '100%',
    })

layout = html.Div([
    html.H1('Radar Example'),
    dcc.Dropdown(
        id='radar-dropdown',
        options=playlists_kv,
        value=playlists[0],
        multi=True
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
            value='me'
        ),
        html.Div(id='playlists')
    ]),

    html.H1('Your Top 5 Artists'),
    html.Div([
        html.Div([
            generate_image_column(artist_images, 0),
            generate_image_column(artist_images, 1),
            generate_image_column(artist_images, 2),
            generate_image_column(artist_images, 3),
            generate_image_column(artist_images, 4)
        ])

    ], style={
        'display': 'flex',
        'flex-wrap': 'wrap',
        'padding': '0 4px',
    })

], style={'width': '500'})


