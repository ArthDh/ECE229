"""
Prerequisites
    pip3 install spotipy Flask Flask-Session
    // from your [app settings](https://developer.spotify.com/dashboard/applications)
    export SPOTIPY_CLIENT_ID=client_id_here
    export SPOTIPY_CLIENT_SECRET=client_secret_here
    export SPOTIPY_REDIRECT_URI='http://127.0.0.1:8080' // must contain a port
    // SPOTIPY_REDIRECT_URI must be added to your [app settings](https://developer.spotify.com/dashboard/applications)
    OPTIONAL
    // in development environment for debug output
    export FLASK_ENV=development
    // so that you can invoke the app outside of the file's directory include
    export FLASK_APP=/path/to/spotipy/examples/app.py
 
    // on Windows, use `SET` instead of `export`
Run app.py
    python3 app.py OR python3 -m flask run
    NOTE: If receiving "port already in use" error, try other ports: 5000, 8090, 8888, etc...
        (will need to be updated in your Spotify app and SPOTIPY_REDIRECT_URI variable)
"""

import os
from flask import Flask, session, request, redirect, render_template, url_for, Blueprint
from flask_session import Session
import spotipy
import uuid
from dotenv import load_dotenv
import sys
# sys.path.append('..')
from .util.data_callbacks import *
import json
import plotly
import plotly.express as px


load_dotenv()
app = Flask(__name__)
Session(app)

server_bp = Blueprint('main', __name__)



caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + session.get('uuid')

@server_bp.route('/')
def index():
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())
    auth_manager, cache_handler = get_auth_manager(session_cache_path())

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return render_template('signin.html', auth_url = auth_url)

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    # # Creating a daemon to save the users CSV file
    # save_tse_csv = Process( target=get_tsne_csv, args=([spotify]), \
    #                                             kwargs={'min_songs_per_playlist':5,'max_songs_per_playlist':30, 'k':10},  daemon=True)
    # save_tse_csv.start()

    # #for saved song history csv file

    # save_hist_csv = Process(target=get_saved_track_history_csv, args=([spotify]), \
    #                                             kwargs={'ntracks':1000},  daemon=True)
    # save_hist_csv.start()

    # save_top_artist_csv = Process(target=get_top_artist_csv, args=([spotify]), daemon=True)
    # save_top_artist_csv.start()


    # save_hist_csv = Process(target=get_saved_track_history_csv, args=([spotify]), \
    #                                             kwargs={'ntracks':1000},  daemon=True)

    # save_hist_csv.start()
    

    # save_top_artist_csv = Process(target=get_top_artist_csv, args=([spotify]), daemon=True)
    # save_top_artist_csv.start()

    print("\n Done creating CSVs \n")
    # return render_template('dashboard.html', spotify = spotify, graphJSON=graphJSON)
    return redirect('/dashboard')


@server_bp.route('/dashboard')
def dashboard():
    return redirect('/dashboard')


@server_bp.route('/sign_out')
def sign_out():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
        session.clear()
        # -- TODO -- 
        # Remove the cache csv dir with files
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')



@server_bp.route('/update')
def update():
    return redirect(url_for('index'))


@server_bp.route('/playlists')
def playlists():
    auth_manager, cache_handler = get_auth_manager(session_cache_path())
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    print(spotify.current_user_playlists() )
    return spotify.current_user_playlists()


@server_bp.route('/currently_playing')
def currently_playing():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    track = spotify.current_user_playing_track()
    if not track is None:
        return track
    return "No track currently playing."


@server_bp.route('/current_user')
def current_user():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user()


@server_bp.route('/details')
def details():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    return spotify.devices()

@server_bp.route('/recent')
def recent():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)


    # return     spotify.current_user_top_artists( limit=20, offset=0, time_range="long_term")
    return spotify.current_user_recently_played(limit=50, after=None, before=None)


    # if __name__ == '__main__':
    #     app.run(threaded=True, port=int(os.environ.get("PORT",
    #                                                    os.environ.get("SPOTIPY_REDIRECT_URI", 8080).split(":")[-1])))
