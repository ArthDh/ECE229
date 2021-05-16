import spotipy
import pandas as pd
import numpy as np
import os


caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)


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



# def clean_top_artists(items_df):
#     '''
        
#     '''

#     items_df['external_urls'] = temp['external_urls'].map(lambda x: x['spotify'])
#     items_df['images'] = temp['images'].map(lambda x: x[0]['url'])
#     items_df['followers'] = temp['followers'].map(lambda x: x['total'])

#     return items_df


# def clean_playlist(user_playlists, playlist):
#     '''

#     '''

#     filter_playlist = [i for i in spotify.current_user_playlists()['items'] if i['name']==playlist_name][0]
#     filter_id = filter_playlist['id']
#     playlist_filter_id = spotify.playlist(filter_id)
#     playlist_tracks = playlist_filter_id['tracks']
#     list_tracks = [playlist_tracks['items'][i]['track'] for i in range(filter_playlist['tracks']['total'])]
#     temp = pd.DataFrame.from_dict(list_tracks)
#     temp_df = clean_top_tracks(temp)

#     return temp_df


# def audio_playlist_features(playlist_df):
#     '''

#     '''
#     return pd.DataFrame.from_dict([spotify.audio_features(playlist_df['id'][i])[0] for i in range(len(playlist_df))])
     