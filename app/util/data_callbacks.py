import spotipy
import pandas as pd
import numpy as np
import os
from os.path import join
import dash_html_components as html
from PIL import Image
from io import BytesIO
import base64
import requests

from sklearn.preprocessing import MinMaxScaler
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans 
import copy
import datetime
from multiprocessing import Process
import datetime
import plotly.graph_objects as go
from collections import Counter
import itertools
import json
from pandas.tseries.offsets import *

from .recommender import *


caches_folder = './.spotify_caches/'
csv_folder = './.csv_caches'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

if not os.path.exists(csv_folder):
    os.makedirs(csv_folder)

def get_auth_manager(cache_path):
    """Returns authentication manager and Cache Handler for reusing in other functions

    :param cache_path: Directory where cache is stored
    :type cache_path: String
    :return: Authentication Manger, Cache Handler
    :rtype: Tuple
    """    

    scope = ['ugc-image-upload'
            ,'user-read-recently-played'
            ,'user-top-read'
            ,'user-read-playback-position'
            ,'user-read-playback-state'
            ,'user-modify-playback-state'
            ,'user-read-currently-playing'
            ,'app-remote-control'
            ,'streaming'
            ,'playlist-modify-public'
            ,'playlist-modify-private'
            ,'playlist-read-private'
            ,'playlist-read-collaborative'
            ,'user-follow-modify'
            ,'user-follow-read'
            ,'user-library-modify'
            ,'user-library-read'
            ,'user-read-email'
            ,'user-read-private'
            ]
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=cache_path)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope,
                                                cache_handler=cache_handler, 
                                                show_dialog=True)
    return auth_manager, cache_handler    

def add_single_genre(tracks_df):  
    """Adds a single genre to tracks data frame by mapping each arist to the most common genre attribute

    :param tracks_df: Dataframe of Tracks
    :type tracks_df: pd.DataFrame
    :return: dataframe with 'genre' column
    :rtype: pd.DataFrame
    """    
    tmp=tracks_df["genres"]

    merged = list(itertools.chain(*tmp))
    genre_rank=pd.Series(merged).value_counts()

    single_genre_list=[]
    for i in tmp:
        genre_tmp='Unknown'
        if not i: # no listed genres
            single_genre_list.append(genre_tmp)
            continue
        max_tmp=0
        for j in i:
            if genre_rank[j]>max_tmp:
                genre_tmp=j
                max_tmp=genre_rank[j]
        single_genre_list.append(genre_tmp)
    tracks_df['genre']=single_genre_list

    g=genre_rank.index.to_list()
    g.sort(key=len)
    counts=tracks_df['genre'].value_counts()
    tmp=tracks_df['genre'].value_counts().index.to_list()
    tmp.sort(key=len)
    map_dict={}
    # one_split 
    for i in tmp:
        if i in map_dict.keys():
            continue
        split=i.split()
        if i in tmp[:5]:
            continue
        if len(split)==1: # skip single genres
            continue
        for j in split:
            for k in tmp:
                if j in k:
                    if i not in map_dict.keys():
                        map_dict[i]=(k,counts[k])
                        #print("\ngenre",i,"\nkey_word",j,"\nmapped",k)
                    elif map_dict[i][1]<counts[k]:
                        map_dict[i]=(k,counts[k])
                        #print("\ngenre",i,"\nkey_word",j,"\nmapped",k)

    new_genres=[]
    counts_mean=sum(counts.to_list())/len(counts.to_list())
    glist=tracks_df['genre'].to_list()
    for i in glist:
        if i in map_dict.keys() and counts[i]<counts_mean:
            new_genres.append(map_dict[i][0])
        else:
            new_genres.append(i)
    new_genres2=[]
    for g in new_genres:#hardcoding to reduce extra genres
        if counts[g]<7:  
            new_genres2.append('rock')
        else:
            new_genres2.append(g)

    tracks_df['genre']=new_genres2
    return tracks_df


def clean_top_tracks(spotify, tracks_df):
    """Cleans up Playlist Tracks dataframe to make data usable

    :param spotify: Spotify Class object for a given user
    :type spotify: spotify.Spotify
    :param tracks_df: Unparsed Dataframe for given user spotify tracks
    :type tracks_df: pandas.Dataframe
    :return: Parsed Dataframe
    :rtype: pandas.Dataframe
    """    

    tracks_df['album_name'] = tracks_df['album'].map(lambda x:x['name'])
    tracks_df['album_art'] = tracks_df['album'].map(lambda x:x['images'][0]['url'] if len(x['images'])!=0 else 0)
    tracks_df['album_href'] = tracks_df['album'].map(lambda x:x['href'])
    tracks_df['album_release_date'] = tracks_df['album'].map(lambda x:x['release_date'])
    tracks_df['artist_names'] = tracks_df['artists'].map(lambda x: ', '.join([a['name'] for a in x]))
    drop_cols = ['album', 'available_markets', 'disc_number', 'external_ids', 'is_local', 'external_urls',\
                 'track_number', 'duration_ms', 'episode', 'track', 'uri',\
                     'preview_url', 'type',	'album_name', 'album_href']
    tracks_df = tracks_df.drop(drop_cols, axis=1)

    return tracks_df


def clean_saved_tracks(spotify, tracks_df):
    """Cleans up Saved Tracks dataframe to make data usable

    :param spotify: Spotify Class object for a given user
    :type spotify: spotify.Spotify
    :param tracks_df: Unparsed Dataframe for given user spotify tracks
    :type tracks_df: pandas.Dataframe
    :return: Parsed Dataframe
    :rtype: pandas.Dataframe
    """   

    tracks_df['album_name'] = tracks_df['album'].map(lambda x:x['name'])
    tracks_df['album_art'] = tracks_df['album'].map(lambda x:x['images'][0]['url'] if len(x['images'])!=0 else 0)
    tracks_df['album_href'] = tracks_df['album'].map(lambda x:x['href'])
    tracks_df['album_release_date'] = tracks_df['album'].map(lambda x:x['release_date'])
    tracks_df['artist_names'] = tracks_df['artists'].map(lambda x: ', '.join([a['name'] for a in x]))
    # '''
    # Uncomment Below to add genre attributes Note: took me about 70s to get 750 songs so expect ~10s for every 100 songs  
    # '''
    tracks_df['genres'] =tracks_df['artists'].map(lambda x:spotify.artist(x[0]["external_urls"]["spotify"])["genres"])
    drop_cols = ['artists', 'available_markets', 'disc_number', 'external_ids', 'is_local', 'external_urls',\
                 'track_number', 'duration_ms', 'uri',\
                     'preview_url', 'type','album','album_href']
    tracks_df = tracks_df.drop(drop_cols, axis=1)

    return tracks_df


def clean_playlist(spotify, user_playlists, playlist):
    """Clean a filtered playlist from a given list of playlist for a particular user

    :param spotify: Spotify Class object for a given user
    :type spotify: spotify.Spotify
    :param user_playlists: All user playlists
    :type user_playlists: List
    :param playlist: Playlist of interest
    :type playlist: String
    :return: Parsed Playlist specific to the user
    :rtype: pandas.Dataframe
    """

    filter_playlist = [i for i in spotify.current_user_playlists()['items'] if i['name']==playlist_name][0]
    filter_id = filter_playlist['id']
    playlist_filter_id = spotify.playlist(filter_id)
    playlist_tracks = playlist_filter_id['tracks']
    list_tracks = [playlist_tracks['items'][i]['track'] for i in range(filter_playlist['tracks']['total'])]
    temp = pd.DataFrame.from_dict(list_tracks)
    temp_df = clean_top_tracks(temp)

    return temp_df

def audio_playlist_features(spotify, playlist_df):
    """Queries Spotify API to generate an Audio Features Dataframe of songs in a given Playlist for the user

    :param spotify: Spotify Class object for a given user
    :type spotify: spotify.Spotify
    :param playlist_df: Cleaned DataFrame for that particular playlist 
    :type playlist_df: pandas.Dataframe
    :return: Audio features dataframe for all songs in a given playlist
    :rtype: pandas.Dataframe
    """

    df = pd.DataFrame.from_dict([spotify.audio_features(playlist_df['id'][i])[0] for i in range(len(playlist_df))])
    drop_cols = ['analysis_url', 'duration_ms', 'time_signature', 'uri', 'track_href', 'type']
    audio_df = df.drop(drop_cols, axis=1)
        
    return audio_df

def get_genres(spotify, tracks_df):
    tracks_df['genres'] = tracks_df['artists'].map(
        lambda x: spotify.artist(x[0]["external_urls"]["spotify"])["genres"])
    tracks_df = add_single_genre(tracks_df)
    return tracks_df

def perform_tsne():
    """Performs TSNE on saved audio feature dataset appended with Kmeans and saves to CSV
    """    
    dataset = '.csv_caches/audio_feature_kmean.csv'
    data = pd.read_csv( dataset)
    X = copy.deepcopy(data)
    song_features = pd.DataFrame()
    scaler = MinMaxScaler() # normalizer instance
    for col in X.columns: 
        if col not in ['artists','predicted_genres', 'href', 'id', 'name', 'playlist_name',  'album_art', 'artist_names','predicted_genres', 'album_release_date']:
            scaler.fit(X[[col]])
            song_features[col] = scaler.transform(X[col].values.reshape(-1,1)).ravel() 

    nb_col = song_features.shape[1]

    pca = PCA(n_components=nb_col)
    data_pca = pca.fit_transform(song_features.values)

    tsne = TSNE(
        n_components=3,
        n_iter=3000,
        learning_rate=200,
        perplexity=10,
        random_state=1131,
    )
    embedding = tsne.fit_transform(data_pca)

    embedding_df = pd.DataFrame(embedding, columns=["x", "y", "z"],)
    data[['x', 'y', 'z']] = embedding_df
    data.to_csv(csv_folder+'/audio_feature_kmean.csv')




def get_tsne_csv(spotify, min_songs_per_playlist=5, max_songs_per_playlist=10, k=10):
    """Creates base csv to perform TSNE 

    :param spotify: Spotify class object for user
    :type spotify: spotify.Spotify
    :param min_songs_per_playlist: Minimum number of songs a particular playlist must have, defaults to 5
    :type min_songs_per_playlist: int, optional
    :param max_songs_per_playlist: Maximum number of songs a particular playlist must have, defaults to 10
    :type max_songs_per_playlist: int, optional
    :param k: k-value for K-Means will define the number of clusters in the final plot, defaults to 10
    :type k: int, optional
    :return: Saves and Returns the final CSV for plotting of TSNE
    :rtype: pandas.Dataframe
    """
    print(f'---MIN SONGS {min_songs_per_playlist}---')
    print(f'---MAX SONGS {max_songs_per_playlist}---')
    print(f'---K value for K Means {k}---')
    
    user_playlists = [i['name'] for i in spotify.current_user_playlists()['items']]
    final_df = pd.DataFrame()
    final_df_alt = pd.DataFrame()
    for playlist_name in user_playlists:
        print(f'getting tsne for {playlist_name}')
        filter_playlist = [i for i in spotify.current_user_playlists()['items'] if i['name']==playlist_name][0]
        if filter_playlist['tracks']['total'] <min_songs_per_playlist:
            continue
        # print(playlist_name, filter_playlist['tracks']['total'])
        filter_id = filter_playlist['id']
        playlist_filter_id = spotify.playlist(filter_id)
        playlist_tracks = playlist_filter_id['tracks']
        list_tracks = [playlist_tracks['items'][i]['track'] for i in range(min(max_songs_per_playlist, filter_playlist['tracks']['total']))]

        list_tracks_alt = [playlist_tracks['items'][i]['track'] for i in range(min(100, filter_playlist['tracks']['total']))]
        list_tracks = [x for x in list_tracks if x]
        list_tracks_alt = [x for x in list_tracks_alt if x]
        temp = pd.DataFrame.from_dict(list_tracks)
        temp_alt = pd.DataFrame.from_dict(list_tracks_alt)


        c_tracks = clean_top_tracks(spotify, temp)
        c_tracks_alt = clean_top_tracks(spotify, temp_alt)

        audio_features = audio_playlist_features(spotify, c_tracks)
        merged_inner = pd.merge(left=c_tracks, right=audio_features, left_on='id', right_on='id')
        merged_inner['playlist_name'] = playlist_name

        # Stack the DataFrames on top of each other
        final_df_alt = pd.concat([final_df_alt, c_tracks_alt], axis=0)
        final_df = pd.concat([final_df, merged_inner], axis=0)

    # K Means - Predicted Genre feature 
    X = copy.deepcopy(final_df)
    song_features = pd.DataFrame()
    scaler = MinMaxScaler() # normalizer instance
    for col in X.columns: 
        if col not in ['artists','predicted_genres', 'href', 'id', 'name', 'playlist_name',  'album_art', 'artist_names','album_release_date']:
            scaler.fit(X[[col]])
            song_features[col] = scaler.transform(X[col].values.reshape(-1,1)).ravel() 

    nb_col = song_features.shape[1]
    pca = PCA(n_components=nb_col)
    data_pca = pca.fit_transform(song_features.values)
    tsne = TSNE(
        n_components=3,
        n_iter=3000,
        learning_rate=200,
        perplexity=10,
        random_state=1131,
    )
    embedding = tsne.fit_transform(data_pca)
    embedding_df = pd.DataFrame(embedding, columns=["x", "y", "z"])


    km = KMeans(n_clusters=k)
    predicted_genres = km.fit_predict(song_features)
    X['predicted_genres'] = predicted_genres
    X[['x', 'y', 'z']] = embedding_df
    X.to_csv(csv_folder+'/audio_feature_kmean.csv')
    final_df_alt.to_csv(csv_folder+'/playlist_full.csv')
    final_df_genre = get_genres(spotify, final_df)
    final_df_genre.to_csv(join(csv_folder, 'playlist_songs_genre.csv'))
    perform_tsne()
    print('---TSNE FILE SAVED---')
    return X
  
def display_era_plot():
    """Static plot of Artist distribution over years

    :return: Plot of artists belonging to particular years
    :rtype: plotly.graph_objects
    """        
    path =  '.csv_caches/playlist_full.csv'
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

    embedding_df['year'] = embedding_df.apply(lambda x:x.album_release_date.split('-')[0], axis=1)
    df_year = embedding_df.groupby('year')
    years =  list(df_year.groups.keys())
    # print(years)

    colors = [
                "#F4EC15",
                "#DAF017",
                "#BBEC19",
                "#9DE81B",
                "#80E41D",
                "#66E01F",
                "#4CDC20",
                "#34D822",
                "#24D249",
                "#25D042",
                "#26CC58",
                "#28C86D",
                "#29C481",
                "#2AC093",
                "#2BBCA4",
                "#2BB5B8",
                "#2C99B4",
                "#2D7EB0",
                "#2D65AC",
                "#2E4EA4",
                "#2E38A4",
                "#3B2FA0",
                "#4E2F9C",
                "#603099",]
    year_skip10 = [int(i) for i in years[::5]]
    colored = []

    for i in range(len(years)):
        mc = 9999
        c_index = 0
        for j in range(len(year_skip10)):
            if abs(year_skip10[j]-int(years[i])) < mc:
                mc =  abs(year_skip10[j]-int(years[i]))
                c_index = j
        colored.append(colors[c_index])
    layout = go.Layout(
        bargap=0.01,
        bargroupgap=0,
        barmode="group",
        margin=go.layout.Margin(l=15, r=0, t=0, b=50),
        showlegend=False,)   

    figure = go.Figure(data=[
                            go.Histogram(
                                        y=sorted(embedding_df['year']),
                                        marker=dict(
                                            color= colored
                                        ),
                                        hovertemplate="<b>Year:</b> %{y} <br><b>Count:</b> %{x}<br>"
                                        )
                            ],
                        layout=layout,
                        
                            )
    figure.update_xaxes(showspikes=True)
    figure.update_yaxes(showspikes=True)
    figure.update_layout(
        xaxis_title="Counts",
        yaxis_title="Years",
    )
    return figure

def get_saved_track_history_csv(spotify, ntracks=1000):
    """Generates csv for users saved spotify tracks

    :param spotify: Spotify class object for user
    :type spotify: spotify.Spotify
    :param ntracks: max num of songs to grab, defaults to 1000
    :type ntracks: int, optional
    :return: None
    :rtype: None
    """    
    assert isinstance(ntracks,int) and ntracks%20==0  #number of songs 
    print('----- Generating Saved Track History ---- ')

    df_saved_tracks=pd.DataFrame() # empty df to append to
    df_audio_feature = pd.DataFrame() # empty df for audio features
    for i in range(0,int(ntracks/20)): # use 50 to limit to 1000 songs for now 
        saved_tracks_snip=spotify.current_user_saved_tracks(limit=20, offset=i*20)['items']
        num_snip= len(saved_tracks_snip) # number of tracks grabbed
        if num_snip<1: # end of saved tracks
            break
        list_tracks=[saved_tracks_snip[i]['track']for i in range(num_snip)]
        list_add_date=[saved_tracks_snip[i]['added_at']for i in range(num_snip)] # format is a bit different for saved song
        temp = pd.DataFrame.from_dict(list_tracks)
        temp['date_added']=list_add_date
        df_saved_tracks=df_saved_tracks.append(clean_saved_tracks(spotify,temp))

        list_add_date=[saved_tracks_snip[i]['added_at']for i in range(num_snip)] # format is a bit different for saved tracks
        temp = pd.DataFrame.from_dict(list_tracks)
        temp['date_added']=list_add_date
        cleaned_temp = clean_saved_tracks(spotify, temp)
        df_saved_tracks = df_saved_tracks.append(cleaned_temp)

        track_ids = cleaned_temp['id'].tolist()
        audio_df = pd.DataFrame.from_dict(spotify.audio_features(track_ids))
        merged_inner = pd.merge(left=cleaned_temp, right=audio_df, left_on='id', right_on='id')
        drop_cols = ['analysis_url', 'duration_ms', 'time_signature', 'uri', 'track_href', 'type', 'explicit',
                     'popularity']
        merged_inner = merged_inner.drop(drop_cols, axis=1)
        df_audio_feature = pd.concat([df_audio_feature, merged_inner], axis=0)

    df_saved_tracks=add_single_genre(df_saved_tracks)          # add a single genre
    df_saved_tracks.to_csv(csv_folder+'/saved_track_history.csv')

    # save audio feature df
    df_audio_feature['month_year'] = pd.to_datetime(df_audio_feature['date_added']).dt.to_period('M')
    df_audio_feature.to_csv(join(csv_folder, 'saved_track_audio_features.csv'))

    monthly_mean = df_audio_feature.groupby(["month_year"]).mean()
    x = monthly_mean.values
    min_max_scaler = MinMaxScaler()
    monthly_mean = pd.DataFrame(min_max_scaler.fit_transform(x), index=monthly_mean.index, columns=monthly_mean.columns)
    monthly_mean.to_csv(join(csv_folder, 'audio_features_monthly_mean.csv'))

    print('--- HIST FILE SAVED---')
    return(df_saved_tracks)



def get_saved_track_audio_features(spotify):
    """
    generate csv for audio features from saved tracks

    :param spotify: Spotify class object for user
    :type spotify: spotify.Spotify
    :return: None
    :rtype: None
    """
    print('-------- creating get_saved_track_audio_features.csv --------')
    history = pd.read_csv(join(csv_folder, 'saved_track_history.csv'))
    final_df = pd.DataFrame()

    for i in range(len(history) // 20 + 1):
        track_ids = history['id'].iloc[i * 20: (i + 1) * 20].tolist()
        tmp_df = history.iloc[i * 20: (i + 1) * 20, :]

        audio_df = pd.DataFrame.from_dict(spotify.audio_features(track_ids))
        merged_inner = pd.merge(left=tmp_df, right=audio_df, left_on='id', right_on='id')
        drop_cols = ['Unnamed: 0', 'analysis_url', 'duration_ms', 'time_signature', 'uri', 'track_href', 'type', 'explicit', 'popularity']
        merged_inner = merged_inner.drop(drop_cols, axis=1)
        final_df = pd.concat([final_df, merged_inner], axis=0)

    final_df['month_year'] = pd.to_datetime(final_df['date_added']).dt.to_period('M')
    final_df.to_csv(join(csv_folder, 'saved_track_audio_features.csv'))

    # get normalized monthly mean for features
    monthly_mean = final_df.groupby(["month_year"]).mean()

    x = monthly_mean.values
    min_max_scaler = MinMaxScaler()
    monthly_mean = pd.DataFrame(min_max_scaler.fit_transform(x), index=monthly_mean.index, columns=monthly_mean.columns)

    monthly_mean.to_csv(join(csv_folder, 'audio_features_monthly_mean.csv'))
    print('--- get_saved_track_audio_features.csv SAVED ---')

def get_top_artist_csv(spotify):
    """
    Generate csv containing current user's top artists
    :param spotify: Spotify class object for user
    :type spotify: spotify.Spotify
    :return: None
    :rtype: None
    """
    print(f'--- Generating top artist csv ---')
    data = spotify.current_user_top_artists(limit=5, time_range='long_term')['items']
    df = pd.DataFrame.from_dict(data)
    df.to_csv(join(csv_folder, 'top_5_artists.csv'))

    print(f'--- TOP_ARTISTS FILE SAVED ---')



def get_slider_info():
    maxmarks=13
    tday=pd.Timestamp.today() #gets timestamp of today
    m1date=tday+DateOffset(months=-maxmarks+1) #first month on slider
    datelist=pd.date_range(m1date, periods=maxmarks, freq='M') # list of months as dates

    dlist=pd.DatetimeIndex(datelist).normalize()
    tags={} #dictionary relating marks on slider to tags. tags are shown as "Apr', "May', etc
    datevalues={} #dictionary relating mark to date value
    x=1
    for i in dlist:
        tags[x]=(i+DateOffset(months=1)).strftime('%b-%Y') #gets the string representation of next month ex:'Apr'
        datevalues[x]=i
        x=x+1
    return (tags,datevalues)


def recommend(spotify):
    """
    saved_songs_csv: csv file with saved track history
    spotify: Spotify auth token
    """
    saved_songs_csv = os.path.join(csv_folder, 'saved_track_history.csv')

    model_folder = 'app/assets/rec-files/'
    model = os.path.join(model_folder, 'recommender_model_final.pkl')
    user_song_csv = os.path.join(model_folder, 'SPF_user_song_score.csv')
    songs_pool_csv = os.path.join(model_folder, 'songs_pool.csv')

    print('\nloaded_csvs\n')

    user_data, saved_songs = get_user_song_df(saved_songs_csv)
    print('user_data loaded')
    sim_user_id = get_sim_user(user_data, song_id_user_csv=user_song_csv)
    print('sim user loaded')
    
    new_songs = get_new_songs(saved_songs, songs_pool_file=songs_pool_csv)
    print('SAved songs loaded')
    
    top_songs, _ = generate_rec_songs(user_id=sim_user_id, top=20, pool=new_songs, model=model)
    print('TOP songs loaded')

    tracks = spotify.tracks(top_songs)
    print(tracks['tracks'])

    d = dict()
    for i, t in enumerate(tracks['tracks']):
        d[i] = {'track':t['name'], 'artist':t['artists'][0]['name'], \
                'img_href': t['album']['images'][0]['url'],  'preview_href': t['preview_url'], \
                'id':t['id']}

    json.dump(d, open( "rec.json", 'w' ) )
    return tracks


def get_user_info():
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

        return html.Div([
                        html.H2(data['name'], style={'text-align':'center', 'margin':'0'}),
                        html.Img(
                        src="data:image/png;base64, " + im_b64,
                        style={"height": "25vh", "display": "block", "margin": "auto", 'border-radius':'15em'},
                        ),
                        
                    ],style={'margin-top':'5em'})
    else:
        return None