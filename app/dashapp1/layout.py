import dash_core_components as dcc
import dash_html_components as html
import spotipy
from ..util.data_callbacks import *
from flask import session
# from cre


# caches_folder = './.spotify_caches/'
# if not os.path.exists(caches_folder):
#     os.makedirs(caches_folder)

# def session_cache_path():
#     return caches_folder + session.get('uuid')


# auth_manager, cache_handler = get_auth_manager(session_cache_path())
# spotify = spotipy.Spotify(auth_manager)

# print(user_playlists = [i['name'] for i in spotify.current_user_playlists()['items']])

layout = html.Div([
    # html.H1('Stock Tickers'),
    # dcc.Dropdown(
    #     id='my-dropdown',
    #     options=[
    #         {'label': 'Coke', 'value': 'COKE'},
    #         {'label': 'Tesla', 'value': 'TSLA'},
    #         {'label': 'Apple', 'value': 'AAPL'}
    #     ],
    #     value='COKE'
    # ),

    # dcc.Graph(id='my-graph'),

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
            options=[   {'label': '229Jams', 'value': '229Jams'},
                        {'label': 'Lorem', 'value': 'Lorem'},
                        {'label': 'RapCaviar', 'value': 'RapCaviar'},
                        {'label': 'Discover Weekly', 'value': 'Discover Weekly'},
                        {'label': 'Hindi Songs - Mega Hit Mix - Bollywood songs - All time top 1000 songs',
                        'value': 'Hindi Songs - Mega Hit Mix - Bollywood songs - All time top 1000 songs'},
                        {'label': 'Coffee Table Jazz', 'value': 'Coffee Table Jazz'},
                        {'label': 'Body Radio', 'value': 'Body Radio'},
                        {'label': 'Classical Upbeat Piano', 'value': 'Classical Upbeat Piano'},
                        {'label': 'Best of the Decade For You',
                        'value': 'Best of the Decade For You'},
                        {'label': 'Your Top Songs 2019', 'value': 'Your Top Songs 2019'},
                        {'label': 'Hot Rhythmic', 'value': 'Hot Rhythmic'},
                        {'label': 'lofi hip hop music - beats to relax/study to',
                        'value': 'lofi hip hop music - beats to relax/study to'},
                        {'label': 'Late Night Jazz', 'value': 'Late Night Jazz'},
                        {'label': 'Liked from Radio', 'value': 'Liked from Radio'},
                        {'label': 'Kimi No Nawa (Your Name) OST | RADWIMPS 💫 ',
                        'value': 'Kimi No Nawa (Your Name) OST | RADWIMPS 💫 '},
                        {'label': 'Moood🤙', 'value': 'Moood🤙'},
                        {'label': 'All Out 10s', 'value': 'All Out 10s'},
                        {'label': 'Hamilton!', 'value': 'Hamilton!'}],
            value='me'
        ),
        html.Div(id='playlists')
    ]),



], style={'width': '500'})
