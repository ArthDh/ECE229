from re import T
import dash_core_components as dcc
import dash_html_components as html
import spotipy
from ..util.data_callbacks import *
from flask import session
import pandas as pd
import json
from pandas.tseries.offsets import *




maxmarks=13


try:
    df = pd.read_csv(f'.csv_caches/{get_my_id()}/audio_feature_kmean.csv').drop(['Unnamed: 0'], axis=1)
    playlists = list(df['playlist_name'].unique())
    playlists_kv = [dict([('label', k), ('value', k)]) for k in playlists]


    top_5_artists = pd.read_csv(f'.csv_caches/{get_my_id()}/top_5_artists.csv')
    artist_images = [json.loads(url.replace("'", '"'))[0]['url'] for url in top_5_artists['images']]

    monthly_mood_df = pd.read_csv(f'.csv_caches/{get_my_id()}/audio_features_monthly_mean.csv')
    monthly_mood_kv = [dict([('label', feature), ('value', feature)]) for feature in monthly_mood_df.columns[1:]]
    # print(monthly_mood_df.columns)
except FileNotFoundError as error:
    playlists = None
    artist_images = None
    monthly_mood_df = None
	
    playlists_kv = [dict()]
    monthly_mood_kv = [dict()]
    print ("One or more CSV Files not found ")

def generate_image_column(artist_images, idx):
	if not artist_images:
		return 0
	if idx == 0:
		res = html.Div([
			html.Img(src=artist_images[0], style={
				'margin-top': '8px',
				'vertical-align': 'middle',
				'width': '25%',
				'height':'240px',
				#'position': 'relative',
				#'left': '100px'
			}),
			html.Img(src=artist_images[1], style={
				'margin-top': '8px',
				'vertical-align': 'middle',
				'width': '25%',
				'height': '240px',
				'margin-left': '50px',
				#'padding-left': '50px'
				# 'position': 'relative',
				# 'left': '100px'
			}),
			html.Img(src=artist_images[2], style={
				'margin-top': '8px',
				'vertical-align': 'middle',
				'width': '25%',
				'height': '240px',
				'margin-left': '50px',
				#'padding-left': '50px'
				# 'position': 'relative',
				# 'left': '100px'
			}),

		], style={
			'display':'inline',
			#'flex': '25%',
			#'max-width': '25%',
			'padding': '0 4px',
			'margin-top': '8px',
			'vertical-align': 'middle',
			'width': '100%',
		},
		)
	else:
		res = html.Div([
			html.Img(src=artist_images[3], style={
				'margin-top': '8px',
				'vertical-align': 'middle',
				'width': '25%',
				'height': '240px',
				'margin-left': '130px',
				# 'position': 'relative',
				# 'left': '100px'
			}),
			html.Img(src=artist_images[4], style={
				'margin-top': '8px',
				'vertical-align': 'middle',
				'width': '25%',
				'height': '240px',
				'margin-left': '50px',
				# 'padding-left': '50px'
				# 'position': 'relative',
				# 'left': '100px'
			})
		], style={
			'display': 'inline',
			# 'flex': '25%',
			# 'max-width': '25%',
			'padding': '0 4px',
			'margin-top': '8px',
			'vertical-align': 'middle',
			'width': '100%',
		},
		)


	return res

layout=html.Div(className="is-preload", children=[html.Div(id="wrapper",
	children=[
		html.Section(className="intro", children=[
		html.Header(children=[
			html.H1(className="app_title", children="Mus-X"),
			html.P(children="Let's analyze your music taste."),
			html.A(className="signin", href="#first", children=[
				html.Span(style={'padding-right':'3px'}, children=[
					html.Span(
						children=[
							"Let's go",
					], style={'padding-right':'5px'}),
					html.I(className="fas fa-play-circle"),
					get_user_info(),

				])
			])
		]),
		html.Div(className="content", children=[
			html.Span(className="image fill data-position-center", style={'text-align':'center'},children=[
				html.Img(src="/dashboard/assets/images/pic01.jpg")
			])
		])
	]),
	html.Section(id="first", children=[
		html.Header(children=[
			html.H2(children=["What does your music look like?"]),
			html.Div(id="div-plot-click-image"),
		]),
		html.Div(className="content", children=[
			html.P(children=[
				html.H2("Let your \"Real\" Sound Cloud decide"),
				html.Span(children=[html.Strong("Begin your music exploration journey with a spatial visualization of your Spotify playlists, clustered based on audio features")]),
				html.Br(),
				html.Span(children=["Hover to check the song and click to know more"])
			]),
			html.Div(
				children=[
					dcc.Graph(id="graph-3d-plot-tsne", style={ 'width':'100%', 'float':'left'}),
					
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
			html.H2(children=["What flavours do you like?"])
		]),
		html.Div(className="content", children=[
			html.H2("Grab a piece of your \"spoti-pie\""),
			html.Span(children=html.Strong("Get a closer look at the composition of your playlists. Let's delve into your choice of flavors")),
			html.Br(),
			html.Span("Click the radar plot to show the genre distribution of one playlists"),
			html.Div([
				dcc.Dropdown(
					id='radar-dropdown',
					options=playlists_kv,
					value=playlists[0] if not playlists == None else 0,
					multi=True
				),
			]),
			html.Div(
				children=[
					dcc.Graph(id='radar-graph', style={'width': '50%', 'float': 'left'}),
					dcc.Graph(id='playlist-pie-graph', style={'width': '50%', 'float': 'right'}),
				]),
			html.Br(),
			html.A(html.Strong("Learn more about Audio Features on Spotify!"),
				   href='https://developer.spotify.com/documentation/web-api/reference/#endpoint-get-audio-features')


	])]),
	html.Section(id="third", children=[
		html.Header(children=[
			html.H2(children=["Are you a Boomer or a zoomer?"]),
			html.Div(id="div-era-click"),
		]),
		html.Div(className="content", children=[
			html.H2("Let's travel back in time and find out"),
			html.Span(children=html.Strong("Let's take a look at the release dates for your music and explore your favourite artists from each time period")),
			html.Br(),
			html.Span("Select a year to fetch the latest albums from your top artists"),
			html.P(),
			html.Div(
        children=[
            dcc.Graph(figure = display_era_plot(), id='graph-era', style={'width':'100%', 'float':'left'}),
			html.H2('Latest Songs by Artists of Selected Year!', style={'display':'None'}, id='era_title'),
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
			html.Span(children=html.Strong("")),
			html.Br(),
			html.Div([
				html.Div([
					generate_image_column(artist_images, 0),
					generate_image_column(artist_images, 1),
				])



			], style={
				'display': 'flex',
				'flex-wrap': 'wrap',
				'padding': '0 4px',
			})
		])
	]),
	html.Section(id="five", children=[
		html.Header(children=[
			html.H2(children=["What's your genre pallette?"])
		]),
		html.Div(className="content", children=[
			html.H2("It's ever changing"),
			html.Span(children=html.Strong("Let's break-down the changes in your musical taste over time. This analysis is based on your saved songs")),
			html.Br(),
			html.P("Slide the filter around to pick the time period"),
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
					value=[maxmarks-5,maxmarks],
					marks=get_slider_info()[0],
					pushable=1
				)
			]),
			html.Hr(),
			html.Span("Select one or more genres and hover over the graph for more"),
			html.Div([
        		dcc.Graph(id='genre-history-chart')
    		])

		])
	]),
	html.Section(id="six", children=[
		html.Header(children=[
			html.H2(children=["What do you learn from this one?"])
		]),
		html.Div(className="content", children=[
			html.P(children=[
				html.Strong(children=["You decide. Mood plot? Maybe?"])
			]),
			html.Div([
        		dcc.Dropdown(
					id='mood-dropdown',
					options=monthly_mood_kv,
					value=monthly_mood_df.columns[1] if not playlists==None else 0,
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
			html.H2("Let us guide you through the musical woods"),
			html.P("Click to see what we think you will like"),
			html.Div([
				html.Button('Surprise me!', id='gen_rec', n_clicks=0),
				html.Div(id="rec_results"),

    		])
		])
	]),

	html.Section(id="nine", children=[
		html.Header(children=[
			html.H2(children=["See you again!"]),
			html.Button('Logout', id='logout', n_clicks=0),

		]),
		# html.Div(className="content", children=[
		# 	html.P(children=[
		# 		html.H1('We got you!')
		# 	]),
		# 	html.Div([
		# 		html.Button('Surprise me!', id='gen_rec', n_clicks=0),
		# 		html.Div(id="rec_results"),

    	# 	])
		# ])
	]),


	])])