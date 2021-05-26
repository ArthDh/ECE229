from re import T
import dash_core_components as dcc
import dash_html_components as html
import spotipy
from ..util.data_callbacks import *
from flask import session
import pandas as pd
import json
<<<<<<< HEAD
=======

############# This NEEDS to be changed super sloppy ##############

dummyvar=True
try: 
    df = pd.read_csv('.csv_caches/audio_feature_kmean.csv').drop(['Unnamed: 0'], axis=1)
    playlists = list(df['playlist_name'].unique())
    playlists_kv = [dict([('label', k), ('value', k)]) for k in playlists]

    top_5_artists = pd.read_csv('.csv_caches/top_5_artists.csv')
    artist_images = [json.loads(url.replace("'", '"'))[0]['url'] for url in top_5_artists['images']]
except FileNotFoundError as error:
        print ("One or more CSV Files not found ")
        

##################################################################






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


>>>>>>> More-Plots

df = pd.read_csv('.csv_caches/audio_feature_kmean.csv').drop(['Unnamed: 0'], axis=1)
playlists = list(df['playlist_name'].unique())
playlists_kv = [dict([('label', k), ('value', k)]) for k in playlists]

top_5_artists = pd.read_csv('.csv_caches/top_5_artists.csv')
artist_images = [json.loads(url.replace("'", '"'))[0]['url'] for url in top_5_artists['images']]

monthly_mood_df = pd.read_csv('.csv_caches/audio_features_monthly_mean.csv')
monthly_mood_kv = [dict([('label', feature), ('value', feature)]) for feature in monthly_mood_df.columns[1:]]
print(monthly_mood_df.columns)
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
            value=playlists,
            multi=True
        ),
        html.Div(id='playlists')
    ]),

    html.Div(
        children=[
            dcc.Graph(id="graph-3d-plot-tsne", style={ 'width':'70%', 'float':'left'}),
            html.Div(id="div-plot-click-image", style={'float':'right'}),
        ],

    ),

    html.Div(
        children=[
            dcc.Graph(figure = display_era_plot(), id='graph-era', style={'width':'70%', 'float':'left'}),
            html.Div(id="div-era-click", style={'float':'right'}),
        ],
        
    ),

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
    }),

    html.H1('Saved Song Genre Distribution'),
    html.Div([
        dcc.Graph(id='genre-pie-chart')
    ]),
    
    html.H1('Mood Plots'),
    dcc.Dropdown(
        id='mood-dropdown',
        options=monthly_mood_kv,
        value=monthly_mood_df.columns[1],
        multi=True
    ),

    dcc.Graph(id='mood-graph'),

], style={'width': '500'})


