from datetime import datetime as dt

import pandas_datareader as pdr
from dash.dependencies import Input
from dash.dependencies import Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from io import BytesIO
import base64
from sklearn.preprocessing import MinMaxScaler
from PIL import Image
import requests
import spotipy
import os
from flask import session
from ..util.data_callbacks import *
import math


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
    def update_graph(playlist):
        df = pd.read_csv('.csv_caches/audio_feature_kmean.csv').drop(['Unnamed: 0'], axis=1)
        playlist_df = df[df['playlist_name']==playlist]

        categories = [ 'danceability', 'energy', 'key', 'loudness', 'mode',
                       'speechiness', 'acousticness', 'instrumentalness', 'liveness',
                       'valence', 'tempo']
        for col in playlist_df.columns: 
            if col  in categories:
                scaler.fit(playlist_df[[col]])
                playlist_df[col] = scaler.transform(playlist_df[col].values.reshape(-1,1)).ravel() 
        feature_val_playlist= playlist_df[categories].mean(0)

        fig = go.Figure()

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


    def generate_figure_image(groups, layout):
        data = []

        for idx, val in groups:
            scatter = go.Scatter3d(
                name=idx,
                x=val["x"],
                y=val["y"],
                z=val["z"],
                text=val['name'],
                textposition="top center",
                mode="markers",
                marker=dict(size=5, symbol="circle"),
                
            )
            data.append(scatter)

        figure = go.Figure(data=data, layout=layout, )
        figure.update_layout(template='plotly_dark')

        return figure

    @dashapp.callback(
        Output("graph-3d-plot-tsne", "figure"),
        [
            Input("playlist_drop", "value"),
        ],
    )
    def display_3d_scatter_plot(
        playlist,
    ):
       
        path =  '.csv_caches/audio_feature_kmean.csv'
        try:
            embedding_df = pd.read_csv(path)
        except FileNotFoundError as error:
            print(
                error,
                "\nThe dataset was not found. Please generate it using generate_demo_embeddings.py",
            )
            return go.Figure()

        # Plot layout
        axes = dict(title="", showgrid=True, zeroline=False, showticklabels=False, gridcolor="darkviolet")
        layout = go.Layout(
            margin=dict(l=0, r=0, b=0, t=0),
            scene=dict(xaxis=axes, yaxis=axes, zaxis=axes),
        )

        # For Image datasets
        embedding_df = embedding_df[embedding_df['playlist_name'].isin(playlist)]
        groups = embedding_df.groupby("predicted_genres")
        figure = generate_figure_image(groups, layout)


        return figure


    @dashapp.callback(
        Output("div-plot-click-image", "children"),
        [
            Input("graph-3d-plot-tsne", "clickData"),
            Input("playlist_drop", "value"),
        ],
    )
    def display_click_image(clickData, playlist):
        path =  '.csv_caches/audio_feature_kmean.csv'
        try:
            embedding_df = pd.read_csv(path)
        except FileNotFoundError as error:
            print(
                error,
                "\nThe dataset was not found. Please generate it using generate_demo_embeddings.py",
            )
            return go.Figure()
        # Convert the point clicked into float64 numpy array
        # print(clickData)
        try:
            name = clickData['points'][0]['text']
            row = embedding_df[embedding_df['name']==name ]
        except:
            return None

        if any(row):
            im = Image.open(requests.get(row.album_art.values[0], stream=True).raw)
            def b64(im_pil):
                buff = BytesIO()
                im_pil.save(buff, format="png")
                im_b64 = base64.b64encode(buff.getvalue()).decode("utf-8")
                return im_b64

            im_b64 = b64(im)
            
            ret = html.Div([
                row.artist_names.values[0],
                html.Br(),
                row.name.values[0],
                html.Img(
                    src="data:image/png;base64, " + im_b64,
                    style={"height": "25vh", "display": "block", "margin": "auto"},
                )
            ])
            return ret
        return None


    @dashapp.callback(
        Output("div-era-click", "children"),
        [
            Input("graph-era", "clickData"),
        ],
    )
    def display_era_click(clickData):
        path =  '.csv_caches/playlist_full.csv'
        try:
            embedding_df = pd.read_csv(path)
        except FileNotFoundError as error:
            print(
                error,
                "\nThe dataset was not found. Please generate it using generate_demo_embeddings.py",
            )
            return go.Figure()
        # Convert the point clicked into float64 numpy array
        # print(clickData)
        year = math.floor(int(clickData['points'][0]['x']))
        years = [year, year+1]


        try:
            embedding_df['year'] = embedding_df.apply(lambda x:x.album_release_date.split('-')[0], axis=1)
            df_year = embedding_df.groupby('year')

            artist_era =[]
            for y in years:
                artist_era.extend(list(df_year.get_group(str(y)).artist_names))
            t = []    
            _ = [ t.extend(a.split(',')) for a in  artist_era]
            artists = [a.strip(' ') for a in t]
            artist_counter = Counter(artists)
            sorted_artists = sorted(artist_counter, key=artist_counter.get, reverse=True)

            auth_manager, cache_handler = get_auth_manager(session_cache_path())
            if not auth_manager.validate_token(cache_handler.get_cached_token()):
                return redirect('/')
            spotify = spotipy.Spotify(auth_manager=auth_manager)
            artist_dict = [(artist, spotify.search(artist, type='artist', limit=1)['artists']['items'][0]['images'][0]['url']) for artist in sorted_artists[:3]]

            print(artist_dict)
        except:
            return None


        def b64(im_pil):
            buff = BytesIO()
            im_pil.save(buff, format="png")
            im_b64 = base64.b64encode(buff.getvalue()).decode("utf-8")
            return im_b64

        final_ret = []
        for i in artist_dict:
            im = Image.open(requests.get(i[1], stream=True).raw)
            im_b64 = b64(im)
            final_ret.append(
                html.Div([
                i[0],
                html.Br(),
                html.Img(
                    src="data:image/png;base64, " + im_b64,
                    style={"height": "25vh", "display": "block", "margin": "auto"},
                )])
                )

        
        ret = html.Div(final_ret)
        return ret