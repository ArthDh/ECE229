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
import plotly.express as px
from plotly.subplots import make_subplots
import textwrap


caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)
scaler = MinMaxScaler()

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
        """
        callback function for radar graph for playlists
        :param playlists: list of playlists
        :type playlists: String or List of Strings
        :return: Figure containing radar graph for audio features in playlists
        :rtype: plotly.graph_objs
        """
        if isinstance(playlists, str):
            playlists = [playlists]
        df = pd.read_csv(f'.csv_caches/{get_my_id()}/audio_feature_kmean.csv').drop(['Unnamed: 0'], axis=1)
        fig = go.Figure()
        for playlist in playlists:
            playlist_df = df[df['playlist_name'] == playlist]
            categories = ['danceability', 'energy', 'key', 'loudness', 'mode',
                          'speechiness', 'acousticness', 'instrumentalness', 'liveness',
                          'valence', 'tempo']
            for col in playlist_df.columns:
                if col in categories:
                    scaler.fit(playlist_df[[col]])
                    playlist_df[col] = scaler.transform(playlist_df[col].values.reshape(-1, 1)).ravel()
            feature_val_playlist = playlist_df[categories].mean(0)

            legend_str = '<br>'.join(textwrap.wrap(playlist, width=12))
            fig.add_trace(go.Scatterpolar(
                r=feature_val_playlist,
                theta=categories,
                fill='toself',
                name=f'{legend_str}'
            ))
        return fig

    @dashapp.callback(
        Output("playlist-pie-graph", "figure"),
        [
            Input("radar-graph", "clickData"),
            Input("radar-dropdown", "value"),
        ],
    )
    def generate_playlist_pie_chart(clickData, playlists):
        """
        generate pie chart based on the selected playlist
        :param clickData: Dictionary of the clicked datapoint
        :type clickData: Dict
        :param playlists: Selected playlists from the dropdown menu
        :type playlists: List
        :return:Figure containing pie chart for the genres in the playlist
        :rtype: plotly.graph_objs
        """
        if isinstance(playlists, str):
            playlists = [playlists]
        # print(clickData)
        # print(playlists)
        # print('----------------------yoooo---------------')
        if not clickData:
            idx = 0
        else:
            idx = clickData['points'][0]['curveNumber']
        fig = go.Figure()
        df = pd.read_csv(f'.csv_caches/{get_my_id()}/playlist_songs_genre.csv')
        df = df[df['playlist_name'] == playlists[idx]]['genre'].value_counts()
        # print(df)
        new = pd.DataFrame()
        new['genre'] = df.index
        new['counts'] = df.values
        # clipped = new[new['counts'] > 5]
        a = df.index.tolist()
        b = df.values.tolist()
        trace = go.Pie(labels=a, values=b)
        fig.add_trace(trace)
        return fig


    @dashapp.callback(Output('my-h1',  component_property='children'), [Input('spotify_me', 'value')])
    def update_spotify(ip_value):
        me = get_me(ip_value)
        return me


    @dashapp.callback(Output('mood-graph', 'figure'), [Input('mood-dropdown', 'value')])
    def update_mood_graph(features):
        """
        callback function for mood graph
        :param features: list of audio features
        :type features: String or List of Strings
        :return: line graph for mood over time
        :rtype: plotly.graph_objs
        """
        # print('features: ', features)
        if isinstance(features, str):
            features = [features]
        monthly_mood_df = pd.read_csv(f'.csv_caches/{get_my_id()}/audio_features_monthly_mean.csv')
        fig = go.Figure()
        for feature in features:
            fig.add_trace(go.Scatter(x=monthly_mood_df['month_year'], y=monthly_mood_df[feature],
                                     mode='lines',
                                     name=f'{feature}'))
        fig.update_layout(xaxis_title="Time", yaxis_title="Normalized Index")
        return fig

    def generate_figure_image(groups, layout):
        """Generates figure for TSNE points given a specific layout

        :param groups: K-Mean generated groups
        :type groups: List
        :param layout: Figure layout for groups in TSNE visualization
        :type layout: plotly.graph_object.Layout
        :return: Figure containing the plotted scatter points
        :rtype: plotly.graph_object
        """
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
                hovertemplate = "Song:<br><b>%{text}<b> "
            )
            data.append(scatter)

        figure = go.Figure(data=data, layout=layout, )
        figure.update_layout(template='plotly_white')

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
        """Creates a 3d Scatter Plot for TSNE visualization colored using K-Means clustering

        :param playlist: Playlists for which the plot is to be shown
        :type playlist: List
        :return: Scatter Plot   
        :rtype: plotly.graph_object
        """

        path =  f'.csv_caches/{get_my_id()}/audio_feature_kmean.csv'
        try:
            embedding_df = pd.read_csv(path)
        except FileNotFoundError as error:
            # print(
            #     error,
            #     "\nThe dataset was not found. Please generate it using generate_demo_embeddings.py",
            # )
            return go.Figure()

        # Plot layout
        axes = dict(title="", showgrid=True, zeroline=False, showticklabels=False, gridcolor="#2ee4bb")
        layout = go.Layout(
            margin=dict(l=0, r=0, b=0, t=0),
            scene=dict(xaxis=axes, yaxis=axes, zaxis=axes),
        )

        # For Image datasets
        embedding_df = embedding_df[embedding_df['playlist_name'].isin(playlist)]
        groups = embedding_df.groupby("predicted_genres")
        figure = generate_figure_image(groups, layout)
        figure.update_layout(showlegend=False)


        return figure


    @dashapp.callback(
        Output("div-plot-click-image", "children"),
        [
            Input("graph-3d-plot-tsne", "clickData"),
            Input("playlist_drop", "value"),
        ],
    )
    def display_click_image(clickData, playlist):
        """Display Focused view of points in 3D ScatterPlot for TSNE 

        :param clickData: Content information of clicked point 
        :type clickData: Dict   
        :param playlist: Playlists for which the plot is to be shown
        :type playlist: List
        :return: Extended information of the clicked point
        :rtype: plotly.graph_object
        """
        path =  f'.csv_caches/{get_my_id()}/audio_feature_kmean.csv'
        try:
            embedding_df = pd.read_csv(path)
        except FileNotFoundError as error:
            # print(
            #     error,
            #     "\nThe dataset was not found. Please generate it using generate_demo_embeddings.py",
            # )
            return go.Figure()

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
                ),
                
            ],style={'float':'left', 'padding':'5vw', 'font-weight': '600'})
            return ret
        return None

    @dashapp.callback(
        Output("div-era-click", "children"),
        [
            Input("graph-era", "clickData"),
        ],
    )
    def display_era_click(clickData):
        """Extended view of Era histogram that shows top-3 artists from that particular year 

        :param clickData: More information on the Histogram that was clicked
        :type clickData: Dict
        :return: Extended view of Histogram that was clicked on 
        :rtype: plotly.graph_object
        """

        
        try:
            path =  f'.csv_caches/{get_my_id()}/playlist_full.csv'
            embedding_df = pd.read_csv(path)
        except FileNotFoundError as error:
            # print(
            #     error,
            #     "\nThe dataset was not found. Please generate it using generate_demo_embeddings.py",
            # )
            return go.Figure()

        try:
            year = math.floor(int(clickData['points'][0]['y']))
            years = [year, year+1]
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

            # print(artist_dict)
        except:
            return None


        def b64(im_pil):
            """Conversion to Base64 

            :param im_pil: Pillow Image to be converted
            :type im_pil: Pillow Image
            :return: base64 encoded image
            :rtype: base64 Image
            """
            buff = BytesIO()
            im_pil.save(buff, format="png")
            im_b64 = base64.b64encode(buff.getvalue()).decode("utf-8")
            return im_b64

        final_ret = []
        for ii, i in enumerate(artist_dict):
            im = Image.open(requests.get(i[1], stream=True).raw)
            im_b64 = b64(im)
            final_ret.append(
                html.Div([
                f'{years[0]} - {years[1]}' if ii==0 else None,
                html.Br() if ii==0 else None,
                i[0],
                html.Br(),
                html.Img(
                    src="data:image/png;base64, " + im_b64,
                    style={"height": "20vh", "display": "block", "margin": "auto"},
                )
                ],
                 style={'font-weight':'600', 'text-align':'center'})
                )


        ret = html.Div(final_ret)
        return ret


    @dashapp.callback(
        Output("div-era-results", "children"),
        [
            Input("graph-era", "clickData"),
        ],
    )
    def display_era_res(clickData):
        """Extended view of Era histogram that shows top-3 artists from that particular year 

        :param clickData: More information on the Histogram that was clicked
        :type clickData: Dict
        :return: Extended view of Histogram that was clicked on 
        :rtype: plotly.graph_object
        """

        
        try:
            path =  f'.csv_caches/{get_my_id()}/playlist_full.csv'
            embedding_df = pd.read_csv(path)
        except FileNotFoundError as error:
            # print(
            #     error,
            #     "\nThe dataset was not found. Please generate it using generate_demo_embeddings.py",
            # )
            return go.Figure()

        try:
            year = math.floor(int(clickData['points'][0]['y']))
            years = [year, year+1]
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

            # Getting latest songs by the artists
        except:
            return None


        def b64(im_pil):
            """Conversion to Base64 

            :param im_pil: Pillow Image to be converted
            :type im_pil: Pillow Image
            :return: base64 encoded image
            :rtype: base64 Image
            """
            buff = BytesIO()
            im_pil.save(buff, format="png")
            im_b64 = base64.b64encode(buff.getvalue()).decode("utf-8")
            return im_b64
        # print(artist_dict)
        final_ret = []

        for artist in sorted_artists[:3]:
            res           = spotify.search(artist, type='artist', limit=1)
            artist_id     = res['artists']['items'][0]['id']
            rec           = spotify.artist_top_tracks(artist_id)
            latest_album  = rec['tracks'][0]['album']['name']
            album_cover   = rec['tracks'][0]['album']['images'][1]['url']
            audio_preview = rec['tracks'][0]['preview_url']

            im = Image.open(requests.get(album_cover, stream=True).raw)
            # print(im)
            im_b64 = b64(im)
            final_ret.append(
                html.Div([
                    html.H4(latest_album),
                    html.Img(
                    src="data:image/png;base64, " + im_b64,
                    style={"height": "15vh", "display": "block", "margin": "auto"},
                    ),
                    html.Audio(src=audio_preview,controls=True, style={'margin-top':'1em', 'width':'80%'}),                  
                ], style={'text-align':'center', 'width':'33%', 'float':'left'})
            )

        ret = html.Div(final_ret, style={'margin-top':'2em'})
        return ret

    @dashapp.callback(Output('era_title', 'style'), [Input("graph-era", "clickData")])
    def update_style(val):
        if val==None: 
            return  {'display': 'None'}
        else:
            return {'display': 'inline'}

    @dashapp.callback(
        Output("genre-pie-chart", "figure"),
        Input("month-slider", "value"))
    def generate_pie_chart(date_range):
        """Genrates pie chart displaying genre distribution of users saved tracks

        :param date_range: date range shown on slider to filter dataframe by
        :type range: list
        :return: pie chart figure
        :rtype: plotly.graph_object
        """
        dates_dict=get_slider_info()[1]
        before=dates_dict[date_range[1]].tz_localize(None)
        after=dates_dict[date_range[0]].tz_localize(None)
        df = pd.read_csv(f'.csv_caches/{get_my_id()}/saved_track_history.csv')
        df['date_added'] = pd.to_datetime(df['date_added']).apply(lambda x: x.replace(tzinfo=None)) 
        df=df[df['date_added']<before]
        df=df[df['date_added']>after]
        df=df['genre'].value_counts()
        new=pd.DataFrame()
        new['genre']=df.index
        new['counts']=df.values
        #clipped=new[new['counts']>5]# removing infrequent genres distribution
        clipped=new
        a=clipped['genre'].tolist()
        b=clipped['counts'].tolist()
        trace =go.Pie(labels=a, values=b )
        data=[trace]
        fig=go.Figure(data=data)
        return fig

    @dashapp.callback(
        Output("genre-history-chart", "figure"),
        Input("graph-3d-plot-tsne", "clickData"))
    def generate_genre_history_chart(test):
        """Generates genre history chart of user saved saved tracks

        :param test: test var
        :type test: none
        :return: genre history chart
        :rtype:  plotly.express.graph_object
        """
        number_of_stacked_genres=5
        num_months=11
        #need to make this a try block
        df=pd.read_csv(f'.csv_caches/{get_my_id()}/saved_track_history.csv')
        top10genres=df["genre"].value_counts()
        counts=top10genres.index.to_list()[:10]
        df=df[df["genre"].isin(counts)]

        df['date_added']=pd.to_datetime(df['date_added'])
        df['month_yr']=df['date_added'].dt.to_period('M')
        count_series=df.groupby(['month_yr','genre']).size()
        new_df = count_series.to_frame(name = 'count')
        new_df = new_df.reset_index() \
            .sort_values(['month_yr','count'],ascending=False) \
            .set_index(['month_yr','genre']) \
            .rename_axis([None, 'genre'])

        new_df=new_df.groupby(level=0).head(number_of_stacked_genres)

        new_df=new_df.reset_index(level=[0,1])
        new_df=new_df.rename(columns={'level_0':'month_yr'})
        new_df=new_df[:4*num_months ]
        new_df['month_yr']=new_df['month_yr'].astype(str)
        print(new_df.head())
        fig=px.bar(new_df, x="month_yr", y="count", color="genre", hover_data={"genre":True,"count":True, "month_yr":False})
        fig.update_layout(xaxis_title='Month', yaxis_title='Number of Songs Added')
        return fig



    @dashapp.callback(
        Output('rec_results', 'children'),
        [Input('gen_rec', 'n_clicks')])
    def update_output(n_clicks):
        if n_clicks==0: 
            return  None
        else:
            if os.path.exists(os.path.join(f'{csv_folder}/{get_my_id()}','rec.json')):
                data = json.load( open( os.path.join(f'{csv_folder}/{get_my_id()}','rec.json')) )
                
                def b64(im_pil):
                    """Conversion to Base64 

                    :param im_pil: Pillow Image to be converted
                    :type im_pil: Pillow Image
                    :return: base64 encoded image
                    :rtype: base64 Image
                    """
                    buff = BytesIO()
                    im_pil.save(buff, format="png")
                    im_b64 = base64.b64encode(buff.getvalue()).decode("utf-8")
                    return im_b64
                temp = []

                for k,v in data.items():
                    im = Image.open(requests.get(v['img_href'], stream=True).raw)
                    im_b64 = b64(im)

                    temp.append(html.Div([
                                html.H2(v['artist'], style={'text-align':'center', 'margin':'0'}),
                                html.H3(v['track'], style={'text-align':'center', 'margin':'0'}),
                                html.Img(
                                src="data:image/png;base64, " + im_b64,
                                style={"height": "25vh", "display": "block", "margin": "auto", 'border-radius':'15em'},
                                ),
                                
                                html.Div([

                                    html.Audio(src=v['preview_href'],controls=True, style={'margin-top':'1em'}),                  

                                ], style={'text-align':'center'})

                            ],style={'margin-top':'2em'}))

                return html.Div(temp, style={'height':'1000px', 'overflow-y':'scroll'})

    @dashapp.callback(
        Output('export_result', 'children'),
        [Input('export_playlist', 'n_clicks')])
    def export_playlist(n_clicks):
        if n_clicks==0:
            return  None
        auth_manager, cache_handler = get_auth_manager(session_cache_path())
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            return redirect('/')
        spotify = spotipy.Spotify(auth_manager=auth_manager)
        user_id = spotify.current_user()['id']
        playlist = spotify.user_playlist_create(user_id, 'Mus-X Recommendations')


        data = json.load(open("me.json"))
        rec = json.load(open(f".csv_caches/{data['id']}/rec.json", 'r'))
        rec_ids = [v['id'] for x, v in rec.items()]
        spotify.playlist_add_items(playlist['id'], rec_ids)
        print('---created---')

        return "done"

    @dashapp.callback(
    Output('user_info', 'children'),
        [Input('url', 'pathname')])
    def get_user_info(pathname):
        if os.path.exists('me.json'):
            data = json.load( open( "me.json" ) )
            im = Image.open(requests.get(data['img_url'], stream=True).raw)
            def b64(im_pil):
                """Conversion to Base64 

                :param im_pil: Pillow Image to be converted
                :type im_pil: Pillow Image
                :return: base64 encoded image
                :rtype: base64 Image
                """
                buff = BytesIO()
                im_pil.save(buff, format="png")
                im_b64 = base64.b64encode(buff.getvalue()).decode("utf-8")
                return im_b64
            im_b64 = b64(im)
 
            return html.Div(className='user-info',children=[
                    html.Img(
                    src="data:image/png;base64, " + im_b64,
                    className='user-image',
                    ),
                    html.P(children=[
                    html.H3(children=["Hi ", data['name']], className='user-name')])
                ],style={'margin-top':'1em'})
        else:
            return None