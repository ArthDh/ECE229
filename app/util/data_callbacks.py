import spotipy
import pandas as pd
import numpy as np
import os
from os.path import join
from sklearn.preprocessing import MinMaxScaler
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans 
import copy
import datetime
from multiprocessing import Process
import itertools

caches_folder = './.spotify_caches/'
csv_folder = './.csv_caches'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

if not os.path.exists(csv_folder):
    os.makedirs(csv_folder)

def get_auth_manager(cache_path):

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

def add_single_genre(tracks_df):  # I this is ugly and inefficent but it works and it was basically instant when testing on 750 songs
    '''
    '''
    #tracks_df["genres"] = tracks_df["genres"].apply(eval)
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
    return tracks_df


def clean_top_tracks(spotify, tracks_df):
    '''
        
    '''
    tracks_df['album_name'] = tracks_df['album'].map(lambda x:x['name'])
    tracks_df['album_art'] = tracks_df['album'].map(lambda x:x['images'][0]['url'] if len(x['images'])!=0 else 0)
    tracks_df['album_href'] = tracks_df['album'].map(lambda x:x['href'])
    tracks_df['album_release_date'] = tracks_df['album'].map(lambda x:x['release_date'])

    tracks_df['artist_names'] = tracks_df['artists'].map(lambda x: ', '.join([a['name'] for a in x]))

    drop_cols = ['album', 'artists', 'available_markets', 'disc_number', 'external_ids', 'is_local', 'external_urls',\
                 'track_number', 'duration_ms', 'episode', 'track', 'uri',\
                     'preview_url', 'type',	'album_name', 'album_href','album_release_date' ]
    tracks_df = tracks_df.drop(drop_cols, axis=1)

    return tracks_df


def clean_saved_tracks(spotify, tracks_df):
    '''
        
    '''
    tracks_df['album_name'] = tracks_df['album'].map(lambda x:x['name'])
    #tracks_df['album_art'] = tracks_df['album'].map(lambda x:x['images'][0]['url'])
    tracks_df['album_art'] = tracks_df['album'].map(lambda x:x['images'][0]['url'] if len(x['images'])!=0 else 0)
    tracks_df['album_href'] = tracks_df['album'].map(lambda x:x['href'])
    tracks_df['album_release_date'] = tracks_df['album'].map(lambda x:x['release_date'])

    tracks_df['artist_names'] = tracks_df['artists'].map(lambda x: ', '.join([a['name'] for a in x]))


    '''
    Uncomment Below to add genre attributes Note: took me about 70s to get 750 songs so expect ~10s for every 100 songs  
    '''
    tracks_df['genres'] =tracks_df['artists'].map(lambda x:spotify.artist(x[0]["external_urls"]["spotify"])["genres"])

    drop_cols = ['artists', 'available_markets', 'disc_number', 'external_ids', 'is_local', 'external_urls',\
                 'track_number', 'duration_ms', 'uri',\
                     'preview_url', 'type','album','album_href']
    tracks_df = tracks_df.drop(drop_cols, axis=1)

    return tracks_df


def clean_playlist(spotify, user_playlists, playlist):
    '''

    '''

    filter_playlist = [i for i in spotify.current_user_playlists()['items'] if i['name']==playlist_name][0]
    filter_id = filter_playlist['id']
    playlist_filter_id = spotify.playlist(filter_id)
    playlist_tracks = playlist_filter_id['tracks']
    list_tracks = [playlist_tracks['items'][i]['track'] for i in range(filter_playlist['tracks']['total'])]
    temp = pd.DataFrame.from_dict(list_tracks)
    temp_df = clean_top_tracks(temp)

    return temp_df

def audio_playlist_features(spotify, playlist_df):
    '''

    '''
    df = pd.DataFrame.from_dict([spotify.audio_features(playlist_df['id'][i])[0] for i in range(len(playlist_df))])
    drop_cols = ['analysis_url', 'duration_ms', 'time_signature', 'uri', 'track_href', 'type']
    audio_df = df.drop(drop_cols, axis=1)

    return audio_df

def perform_tsne():
    dataset = '.csv_caches/audio_feature_kmean.csv'
    data = pd.read_csv( dataset)
    X = copy.deepcopy(data)
    song_features = pd.DataFrame()
    scaler = MinMaxScaler() # normalizer instance
    for col in X.columns: 
        if col not in ['artists','predicted_genres', 'href', 'id', 'name', 'playlist_name',  'album_art', 'artist_names','predicted_genres']:
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
    '''
    '''
    print(f'---MIN SONGS {min_songs_per_playlist}---')
    print(f'---MAX SONGS {max_songs_per_playlist}---')
    print(f'---K value for K Means {k}---')
    
    user_playlists = [i['name'] for i in spotify.current_user_playlists()['items']]
    final_df = pd.DataFrame()
    for playlist_name in user_playlists:
        
        filter_playlist = [i for i in spotify.current_user_playlists()['items'] if i['name']==playlist_name][0]
        if filter_playlist['tracks']['total'] <min_songs_per_playlist:
            continue
        # print(playlist_name, filter_playlist['tracks']['total'])
        filter_id = filter_playlist['id']
        playlist_filter_id = spotify.playlist(filter_id)
        playlist_tracks = playlist_filter_id['tracks']
        list_tracks = [playlist_tracks['items'][i]['track'] for i in range(min(max_songs_per_playlist, filter_playlist['tracks']['total']))]
        temp = pd.DataFrame.from_dict(list_tracks)

        c_tracks = clean_top_tracks(spotify, temp)
        audio_features = audio_playlist_features(spotify, c_tracks)
        merged_inner = pd.merge(left=c_tracks, right=audio_features, left_on='id', right_on='id')
        merged_inner['playlist_name'] = playlist_name

        # Stack the DataFrames on top of each other
        final_df = pd.concat([final_df, merged_inner], axis=0)

    # K Means - Predicted Genre feature 
    X = copy.deepcopy(final_df)
    song_features = pd.DataFrame()
    scaler = MinMaxScaler() # normalizer instance
    for col in X.columns: 
        if col not in ['artists','predicted_genres', 'href', 'id', 'name', 'playlist_name',  'album_art', 'artist_names',]:
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
    perform_tsne()


    print('--- TSNE FILE SAVED---')
    return X


def get_saved_track_history_csv(spotify, ntracks=1000):
    '''
    param: max_songs_per_month: max number of songs to get for each month
    '''
    assert isinstance(ntracks,int) and ntracks%20==0  #number of songs 

    df_saved_tracks=pd.DataFrame() # empty df to append to
    for i in range(1,int(ntracks/20)): # use 50 to limit to 1000 songs for now 
        saved_tracks_snip=spotify.current_user_saved_tracks(limit=20, offset=i*20)['items']
        num_snip= len(saved_tracks_snip) # number of tracks grabbed
        if num_snip<1: # end of saved tracks
            break
        list_tracks=[saved_tracks_snip[i]['track']for i in range(num_snip)]
        list_add_date=[saved_tracks_snip[i]['added_at']for i in range(num_snip)] # format is a bit different for saved tracks
        temp = pd.DataFrame.from_dict(list_tracks)
        temp['date_added']=list_add_date
        df_saved_tracks=df_saved_tracks.append(clean_saved_tracks(spotify,temp))
    df_saved_tracks=add_single_genre(df_saved_tracks)          # add a single genre
    df_saved_tracks.to_csv(csv_folder+'/saved_track_history.csv')
    print('--- HIST FILE SAVED---')
    return(df_saved_tracks)


def get_top_artist_csv(spotify):
    print(f'--- Generating top artist csv ---')
    data = spotify.current_user_top_artists(limit=5, time_range='long_term')['items']
    df = pd.DataFrame.from_dict(data)
    df.to_csv(join(csv_folder, 'top_5_artists.csv'))

    print(f'--- TOP_ARTISTS FILE SAVED ---')


    