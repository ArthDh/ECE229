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
    df = pd.read_csv('.csv_caches/audio_feature_kmean.csv').drop(['Unnamed: 0'], axis=1)
    playlists = list(df['playlist_name'].unique())
    playlists_kv = [dict([('label', k), ('value', k)]) for k in playlists]


    top_5_artists = pd.read_csv('.csv_caches/top_5_artists.csv')
    artist_images = [json.loads(url.replace("'", '"'))[0]['url'] for url in top_5_artists['images']]

    monthly_mood_df = pd.read_csv('.csv_caches/audio_features_monthly_mean.csv')
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
	children=[html.Section(className="intro", children=[
		html.Header(children=[
			html.H1(className="app_title", children="Mus-X"),
			html.P(children="Let's analyse your music taste."),
			html.A(className="signin", href="#first", children=[
				html.Span(style={'padding-right':'3px'}, children=[
					html.Span(children=["Let's go"], style={'padding-right':'5px'}),
					html.I(className="fas fa-play-circle")
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
			html.H2(children=["Magna sed nullam nisl adipiscing"])
		]),
		html.Div(className="content", children=[
			html.P(children=[
				html.H2(children=["RadarPlot"])]),
			html.Div([
				dcc.Dropdown(
				id='radar-dropdown',
				options=playlists_kv,
				value=playlists[0] if not playlists==None else 0,
				multi=True
			),
			html.Div(
				children=[
					dcc.Graph(id='radar-graph', style={'width': '50%', 'float': 'left'}),
					dcc.Graph(id='playlist-pie-graph', style={'width': '50%', 'float': 'right'}),
				])
		])
	])]),
	html.Section(id="second", children=[
		html.Header(children=[
			html.H2(children=["Your Real Sound Cloud"]),
			html.Div(id="div-plot-click-image"),
		]),
		html.Div(className="content", children=[
			html.P(children=[
				html.Strong(children=["TSNE Plot"])
			]),
			html.Div([
				'Playlist',

				dcc.Dropdown(
					id='playlist_drop',
					options=playlists_kv,
					value=playlists,
					multi=True
				),
				html.Div(id='playlists')
			]),
			html.Div(
				children=[
					dcc.Graph(id="graph-3d-plot-tsne", style={ 'width':'100%', 'float':'left'}),
					
				])
		])
	]),
	html.Section(id="third", children=[
		html.Header(children=[
			html.H2(children=["Magna sed nullam nisl adipiscing"]),
			html.Div(id="div-era-click"),
		]),
		html.Div(className="content", children=[
			html.P(children=[
				html.Strong(children=["Annual Artist Plot"])
			]),
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
			html.H2(children=["Magna sed nullam nisl adipiscing"])
		]),
		html.Div(className="content", children=[
			html.P(children=[
				html.Strong(children=["Era Plot"])
			]),
			html.H1('Your Top 5 Artists'),
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
			html.H2(children=["Saved Song Genre Distribution"])
		]),
		html.Div(className="content", children=[
			html.P(children=[
				html.Strong(children=["Saved Song Genre Distribution"])
			]),
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
			])
		])
	]),
	html.Section(id="six", children=[
		html.Header(children=[
			html.H2(children=["Genres"])
		]),
		html.Div(className="content", children=[
			html.P(children=[
				html.Strong(children=["Saved Song Genre History"])
			]),
			html.Div([
        		dcc.Graph(id='genre-history-chart')
    		])
		])
	]),
	html.Section(id="seven", children=[
		html.Header(children=[
			html.H2(children=["Mood Plots"])
		]),
		html.Div(className="content", children=[
			html.P(children=[
				html.Strong(children=["Mood Plots"])
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
	])
	])])