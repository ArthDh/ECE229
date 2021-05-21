from datetime import datetime as dt

import pandas_datareader as pdr
from dash.dependencies import Input
from dash.dependencies import Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler


import spotipy
import os
from flask import session
from ..util.data_callbacks import *


caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)
scaler = MinMaxScaler() # normalizer instance


def session_cache_path():
    return caches_folder + session.get('uuid')

def get_me(val):
    auth_manager, cache_handler = get_auth_manager(session_cache_path())
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return html.H1(spotify.me()[val])

def register_callbacks(dashapp):

    @dashapp.callback(Output('radar-graph', 'figure'), [Input('radar-dropdown', 'value')])
    def update_graph(playlists):
        if isinstance(playlists, str):
            playlists = [playlists]
        df = pd.read_csv('.csv_caches/audio_feature_kmean.csv').drop(['Unnamed: 0'], axis=1)
        fig = go.Figure()
        for playlist in playlists:
            playlist_df = df[df['playlist_name']==playlist]
            categories = [ 'danceability', 'energy', 'key', 'loudness', 'mode',
                           'speechiness', 'acousticness', 'instrumentalness', 'liveness',
                           'valence', 'tempo']
            for col in playlist_df.columns:
                if col  in categories:
                    scaler.fit(playlist_df[[col]])
                    playlist_df[col] = scaler.transform(playlist_df[col].values.reshape(-1,1)).ravel()
            feature_val_playlist= playlist_df[categories].mean(0)


            fig.add_trace(go.Scatterpolar(
                r=feature_val_playlist,
                theta=categories,
                fill='toself',
                name=f'{playlist}'
            ))
        return fig


    @dashapp.callback(Output('my-h1',  component_property='children'), [Input('spotify_me', 'value')])
    def update_spotify(ip_value):
        me = get_me(ip_value)
        return me

