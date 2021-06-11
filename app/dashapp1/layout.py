from re import T
import dash_core_components as dcc
import dash_html_components as html
import spotipy
from ..util.data_callbacks import *
from flask import session
import pandas as pd
import json
from pandas.tseries.offsets import *

maxmarks = 13

try:
    df = pd.read_csv(f'.csv_caches/{get_my_id()}/audio_feature_kmean.csv').drop(['Unnamed: 0'], axis=1)
    playlists = list(df['playlist_name'].unique())
    playlists_kv = [dict([('label', k), ('value', k)]) for k in playlists]

    top_5_artists = pd.read_csv(f'.csv_caches/{get_my_id()}/top_5_artists.csv')
    artist_images = [json.loads(url.replace("'", '"'))[0]['url'] for url in top_5_artists['images']]
    artist_names = top_5_artists.name.to_list()
    top_10_tracks = pd.read_csv(f'.csv_caches/{get_my_id()}/top_10_tracks.csv')
    track_images_1 = [url for url in top_10_tracks['image']][:5]
    track_images_2 = [url for url in top_10_tracks['image']][5:]
    track_names_1 = top_10_tracks.name.to_list()[:5]
    track_names_2 = top_10_tracks.name.to_list()[5:]

    monthly_mood_df = pd.read_csv(f'.csv_caches/{get_my_id()}/audio_features_monthly_mean.csv')
    monthly_mood_kv = [dict([('label', feature), ('value', feature)]) for feature in monthly_mood_df.columns[1:]]
    # print(monthly_mood_df.columns)
except:
    pass
# except FileNotFoundError as error:
#     artist_names = None
#     playlists = None
#     artist_images = None
#     track_images_1 = None
#     track_images_2 = None
#     track_names_1 = None
#     track_names_2 = None
#     monthly_mood_df = None

#     playlists_kv = [dict()]
#     monthly_mood_kv = [dict()]
    # print ("One or more CSV Files not found ")


def generate_image_section(artist_images, titles):
    if not artist_images:
        return ""
    row1 = html.Div([
        html.Div([
            html.Img(src=artist_images[0], className='img_in_row'),
            html.H3(titles[0], style={'margin': 'auto', 'text-align': 'center'}),
        ], className='img_col'),

        html.Div([
            html.Img(src=artist_images[1], className='img_in_row'),
            html.H3(titles[1], style={'margin': 'auto', 'text-align': 'center'}),
        ], className='img_col'),

        html.Div([
            html.Img(src=artist_images[2], className='img_in_row'),
            html.H3(titles[2], style={'margin': 'auto', 'text-align': 'center'}),
        ], className='img_col'),
    ],
        className='img_row',

    )
    row2 = html.Div([
        html.Div(style={'width': '17%'}),

        html.Div([
            html.Img(src=artist_images[3], className='img_in_row'),
            html.H3(titles[3], style={'margin': 'auto', 'text-align': 'center'}),
        ], className='img_col'),

        html.Div([
            html.Img(src=artist_images[4], className='img_in_row'),
            html.H3(titles[4], style={'margin': 'auto', 'text-align': 'center'}),
        ], className='img_col'),

        html.Div(style={'width': '17%'}),
    ],
        className='img_row_half',
    )

    return html.Div([row1, row2])


layout = html.Div(className="is-preload", children=[html.Div(id="wrapper",
                                                             children=[
                                                                 html.Section(className="intro", children=[
                                                                     dcc.Location(id='url', refresh=False),
                                                                     html.Header(id='header', children=[
                                                                         html.H1(className="app_title",
                                                                                 children="Mus-X"),
                                                                         html.P(
                                                                             children="Let's analyze your music taste."),
                                                                         html.A(className="signin", href="#first",
                                                                                children=[
                                                                                    html.Span(
                                                                                        style={'padding-right': '3px'},
                                                                                        children=[
                                                                                            html.Div(id='user_info'),
                                                                                            # get_user_info(),

                                                                                        ])
                                                                                ])
                                                                     ]),
                                                                     html.Div(className="content", children=[
                                                                         html.Span(
                                                                             className="image fill data-position-center",
                                                                             style={'text-align': 'center'}, children=[
                                                                                 html.Img(
                                                                                     src="/dashboard/assets/images/pic01.jpg")
                                                                             ])
                                                                     ])
                                                                 ]),
                                                                 html.Section(id="first", children=[
                                                                     html.Header(children=[
                                                                         html.H2(children=[
                                                                             "What does your music look like?"]),
                                                                         html.Div(id="div-plot-click-image"),
                                                                     ]),
                                                                     html.Div(className="content", children=[
                                                                         html.P(children=[
                                                                             html.H2(
                                                                                 "Let your \"Real\" Sound Cloud decide"),
                                                                             html.Span(children=[html.Strong(
                                                                                 "Begin your music exploration journey with a spatial visualization of your Spotify playlists, clustered based on audio features")]),
                                                                             html.Br(),
                                                                             html.Span(children=[
                                                                                 "Hover to check the song and click to know more"])
                                                                         ]),
                                                                         html.Div(
                                                                             children=[
                                                                                 dcc.Graph(id="graph-3d-plot-tsne",
                                                                                           style={'width': '100%',
                                                                                                  'float': 'left'}),

                                                                             ]),
                                                                         html.Div([
                                                                             'Playlists',

                                                                             dcc.Dropdown(
                                                                                 id='playlist_drop',
                                                                                 options=playlists_kv,
                                                                                 value=playlists,
                                                                                 multi=True
                                                                             ),
                                                                             html.Div(id='playlists')
                                                                         ]),
                                                                     ])
                                                                 ]),
                                                                 html.Section(id="second", children=[
                                                                     html.Header(children=[
                                                                         html.H2(
                                                                             children=["What flavours do you like?"])
                                                                     ]),
                                                                     html.Div(className="content", children=[
                                                                         html.H2("Grab a piece of your \"spoti-pie\""),
                                                                         html.Span(children=html.Strong(
                                                                             "Get a closer look at the composition of your playlists. Let's delve into your choice of flavors")),
                                                                         html.Br(),
                                                                         html.Span(
                                                                             "Click the radar plot to show the genre distribution of one playlists"),
                                                                         html.Div([
                                                                             dcc.Dropdown(
                                                                                 id='radar-dropdown',
                                                                                 options=playlists_kv,
                                                                                 value=playlists[
                                                                                     0] if not playlists == None else 0,
                                                                                 multi=True
                                                                             ),
                                                                         ]),
                                                                         html.Div(
                                                                             children=[
                                                                                 dcc.Graph(id='radar-graph',
                                                                                           style={'width': '50%',
                                                                                                  'float': 'left'}),
                                                                                 dcc.Graph(id='playlist-pie-graph',
                                                                                           style={'width': '50%',
                                                                                                  'float': 'right'}),
                                                                             ]),
                                                                         html.Br(),
                                                                         html.A(html.Strong(
                                                                             "Learn more about Audio Features on Spotify!"),
                                                                             href='https://developer.spotify.com/documentation/web-api/reference/#endpoint-get-audio-features')

                                                                     ])]),
                                                                 html.Section(id="third", children=[
                                                                     html.Header(children=[
                                                                         html.H2(children=[
                                                                             "Are you a Boomer or a zoomer?"]),
                                                                         html.Div(id="div-era-click"),
                                                                     ]),
                                                                     html.Div(className="content", children=[
                                                                         html.H2(
                                                                             "Let's travel back in time and find out"),
                                                                         html.Span(children=html.Strong(
                                                                             "Let's take a look at the release dates for your music and explore your favourite artists from each time period")),
                                                                         html.Br(),
                                                                         html.Span(
                                                                             "Select a year to fetch the latest albums from your top artists"),
                                                                         html.P(),
                                                                         html.Div(
                                                                             children=[
                                                                                 dcc.Graph(figure=display_era_plot(),
                                                                                           id='graph-era',
                                                                                           style={'width': '100%',
                                                                                                  'float': 'left'}),
                                                                                 html.H2(
                                                                                     'Latest Songs by Artists of Selected Year!',
                                                                                     style={'display': 'None'},
                                                                                     id='era_title'),
                                                                                 html.Div(id="div-era-results"),
                                                                             ],

                                                                         )
                                                                     ])
                                                                 ]),
                                                                 html.Section(id="four", children=[
                                                                     html.Header(children=[
                                                                         html.H2(children=["What's your jam?"])
                                                                     ]),
                                                                     html.Div(className="content", children=[
                                                                         html.H2("It's favorites time!"),
                                                                         html.Span(children=html.Strong(
                                                                             "This gallery displays the top 5 artists who shine through your music space, followed by your top 10 tracks.")),
                                                                         html.P("Are they who you have in mind? Take a moment to sip your connection with their music :)"),
                                                                         generate_image_section(artist_images,
                                                                                                artist_names),
                                                                         generate_image_section(track_images_1,
                                                                                                track_names_1),
                                                                         generate_image_section(track_images_2,
                                                                                                track_names_2),
                                                                     ])
                                                                 ]),
                                                                 html.Section(id="five", children=[
                                                                     html.Header(children=[
                                                                         html.H2(
                                                                             children=["What's your genre pallette?"])
                                                                     ]),
                                                                     html.Div(className="content", children=[
                                                                         html.H2("It's ever changing"),
                                                                         html.Span(children=html.Strong(
                                                                             "Let's break-down the changes in your musical taste over time. This analysis is based on your saved songs")),
                                                                         html.Br(),
                                                                         html.P(
                                                                             "Slide the filter around to pick the time period"),
                                                                         html.Div([
                                                                             dcc.Graph(id='genre-pie-chart'),
                                                                         ]),
                                                                         html.Div([
                                                                             dcc.RangeSlider(
                                                                                 id='month-slider',
                                                                                 updatemode='mouseup',
                                                                                 count=1,
                                                                                 min=1,
                                                                                 max=maxmarks,
                                                                                 step=1,
                                                                                 value=[maxmarks - 5, maxmarks],
                                                                                 marks=get_slider_info()[0],
                                                                                 pushable=1
                                                                             )
                                                                         ]),
                                                                         html.Hr(),
                                                                         html.Span(
                                                                             "Select one or more genres and hover over the graph for more"),
                                                                         html.Div([
                                                                             dcc.Graph(id='genre-history-chart')
                                                                         ])

                                                                     ])
                                                                 ]),
                                                                 html.Section(id="six", children=[
                                                                     html.Header(children=[
                                                                         html.H2(children=[
                                                                             "What do you learn from this one?"])
                                                                     ]),
                                                                     html.Div(className="content", children=[
                                                                         html.P(children=[
                                                                             html.Strong(children=[
                                                                                 "You decide. Mood plot? Maybe?"])
                                                                         ]),
                                                                         html.Div([
                                                                             dcc.Dropdown(
                                                                                 id='mood-dropdown',
                                                                                 options=monthly_mood_kv,
                                                                                 value=monthly_mood_df.columns[
                                                                                     1] if not playlists == None else 0,
                                                                                 multi=True
                                                                             ),

                                                                             dcc.Graph(id='mood-graph'),
                                                                         ])
                                                                     ])
                                                                 ]),
                                                                 html.Section(id="seven", children=[
                                                                     html.Header(children=[
                                                                         html.H2(children=["Lost in the soundscape?"])
                                                                     ]),
                                                                     html.Div(className="content", children=[
                                                                         html.H2(
                                                                             "Let us guide you through the musical woods"),
                                                                         html.P(
                                                                             "Click to see what we think you will like"),
                                                                         html.Div([
                                                                             html.Button('Surprise me!', id='gen_rec',
                                                                                         n_clicks=0),
                                                                             html.Div(id="rec_results"),
                                                                         ]),
                                                                         html.Button('Export the result to Spotify!',
                                                                                     id='export_playlist', n_clicks=0),
                                                                         html.Div(id="export_result"),
                                                                     ])
                                                                 ]),

                                                                 html.Section(id="nine", children=[
                                                                     html.Header(children=[
                                                                         html.H2(children=["See you again!"]),
                                                                         html.Button('Logout', id='logout', n_clicks=0),
                                                                         html.Div(id='temp', style={'display': 'None'})

                                                                     ]),
                                                                 ]),

                                                                 html.Section(id="ten", children=[
                                                                     html.Header(children=[
                                                                         html.H2(
                                                                             children=["Check out our Documentation!"])
                                                                     ]),
                                                                     html.Div(className="content", children=[
                                                                         html.A(id='docs', className="signin", href="/docs",
                                                                                children=[html.H2("Made with ❤️")], )

                                                                     ])
                                                                 ]),
                                                             ])])
