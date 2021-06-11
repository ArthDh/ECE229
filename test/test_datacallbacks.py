from unittest import TestCase
import numpy as np
import pandas as pd
import os
import spotipy
import plotly.graph_objects as go
import dash_html_components as html

# coverage run --source=app -m pytest

class TestDataCallbackMethods(TestCase):
    
    def __init__(self, *args, **kwargs):
        print('TestDataCallbackMethods.__init__')
        super(TestDataCallbackMethods, self).__init__(*args, **kwargs)

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


        auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope,
                                                    show_dialog=True)

        # auth_manager.get_access_token(request.args.get("code"))
        auth_url = auth_manager.get_authorize_url()
        self.spotify = spotipy.Spotify(auth_manager=auth_manager)

    def test_get_my_id(self):
        from app.util.data_callbacks import get_my_id
        res = get_my_id()
        assert isinstance(res, str)


    def test_get_top_artist_csv(self):
        from app.util.data_callbacks import get_top_artist_csv

        res = get_top_artist_csv(self.spotify)
        assert isinstance(res, type(None))

    def test_get_top_tracks_csv(self):
        from app.util.data_callbacks import get_top_tracks_csv

        res = get_top_tracks_csv(self.spotify)
        assert isinstance(res, type(None))

    def test_get_tsne_csv(self):
        from app.util.data_callbacks import get_tsne_csv

        res = get_tsne_csv(self.spotify, min_songs_per_playlist=1,max_songs_per_playlist=1,k=1)
        assert isinstance(res, pd.DataFrame)

    def test_get_saved_track_history_csv(self):
        from app.util.data_callbacks import get_saved_track_history_csv

        res = get_saved_track_history_csv(self.spotify, ntracks=20)
        assert isinstance(res, pd.DataFrame)

    def test_display_era_plot(self):
        from app.util.data_callbacks import display_era_plot

        res = display_era_plot()
        assert isinstance(res, go.Figure)

    def test_get_user_info(self):
        from app.util.data_callbacks import get_user_info

        res = get_user_info()
        assert isinstance(res, (type(None), type(html.Div())))
    
   
    def test_get_saved_track_audio_features(self):
        from app.util.data_callbacks import  get_saved_track_audio_features

        res = get_saved_track_audio_features(self.spotify)
        assert isinstance(res, type(None))

    def test_get_slider_info(self):
        from app.util.data_callbacks import get_slider_info

        res = get_slider_info()
        assert isinstance(res, tuple)

if __name__ == '__main__':
    unittest.main()
