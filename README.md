# Mus-X: A Music Taste Analysis & Exploration Web Dashboard for Spotify Users

By ECE 229 Group 4: Arth D., Chin L., John O., Moira F., Tawaana H., Zizhan C.

(insert main page screenshot)

## About

This dashboard is developed by a group of music-lover graduate students as the final project for ECE 229: Computational Data Science & Product Development at UCSD. If you're interested in learning more about your music listening preferences, this dashboard is for you. By signing in with your Spotify Credentials, you'll be able to see analysis and visualization of your music tastes, such as TSNE spatial clustering of all tracks, genre breakdown, top artists & top tracks, recommended tracks for you and more. We hope Mus-X brings our users a pleasant visual & interactive experience, and help understand one's music preferences better.

## Installation

Requires python 3.7+

Some main third-party modules:
- dash 1.20.0
- Flask 1.1.2
- pandas 1.1.4
- scikit-learn 0.23.2
- scikit-surprise 1.1.1
- plotly 4.13.0
- spotipy 2.18.0

Clone the repository using
```
git clone https://github.com/ArthDh/ECE229.git
```

Create a python virtual environment
```python
python -m venv env
```
Activate the environment
```
source  env/bin/activate
```

Install dependencies
```
pip install requirements.txt
```

Deactivate when done making changes
```
deactivate
```

## Usage

To run this webapp on your machine, go to the directory where this repository sits, and type in your terminal:
```python
python dashapp.py
```
This will launch a server locally on your machine. Clicking on the url shown will bring you to Mus-X home page in your web browser. Then you can sign in with your Spotify credentials to start the jorney of understanding your music tastes!

Note: We have also deployed this web app on AWS for the period of this course, but the site will be down when our credits run out.

## Application Architecture

We used Flask as the web framework, and integrated Dash by Plotly to create interactive data visualization plots that ties to modern UI elements. The web application is deployed on AWS EC2 Scaling Group, with S3 used for large files storage and Dynamo DB for session cache. Data analysis, processing and integration are coded in Python. The Spotify Python API and OAuth Security handles the Spotify user log-in credentials. 

## Data Visualization

The plots in this dashcoard are coded using Plotly. We wrote callback functions to allow a more interactive data exploration experience for the user.

### All Tracks TSNE

We used K-mean for clustering and all visualizations regarding K-mean are also showed in final notebook. The original data used for hyper dimensional visualization are stoed in [data](https://github.com/ArthDh/ECE-143/tree/main/data) folder, named df_cleaned.tsv and df_cleaned_genre_10.tsv.

### Genre Radar Plot & Pie Charts for Playlists

PCA

![PCA](https://github.com/ArthDh/ECE-143/blob/main/images/PCA.gif)

UMAP

![UMAP](https://github.com/ArthDh/ECE-143/blob/main/images/UMAP.gif)

In order to see the 3D visualization of the dataset with predicted genres and artist names as index, use the following link:<br>
[Embedding Visualizer](https://projector.tensorflow.org/?config=https://gist.githubusercontent.com/ArthDh/804b7297af76e5d0e626c8c01af2d158/raw/0d0c110e2ca731df7a63dcc7e8e0370d9dd29dd0/projector_config.json)

### Songs Recommender Model

We built a user-item collaborative filtering recommender to generate personalized song recommendations for users. The model applies SVD (Probablistic Matrix Factorization) algorithm to learn user preferences of songs from external training dataset, and predicts scores of songs during inference.
