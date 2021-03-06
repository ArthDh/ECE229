# Mus-X: A Music Taste Analysis & Exploration Web Dashboard for Spotify Users

By ECE 229 Group 4: Arth D., Chin L., John O., Moira F., Tawaana H., Zizhan C.

![Home Page](readme_images/welcome_page.png?raw=true)

## About

This dashboard is developed by a group of music-lover graduate students as the final project for ECE 229: Computational Data Science & Product Development at UCSD. 

If you're interested in learning more about your music listening preferences, this dashboard is for you. By signing in with your Spotify Credentials, you'll be able to see analysis and visualization of your music tastes, such as TSNE spatial clustering of all tracks, genre breakdown, top artists & top tracks, recommended tracks for you and more. 

We hope Mus-X brings our users a pleasant visual & interactive experience, and help understand one's music preferences better.

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
## Spotify Setup
-Create a spotify developer account (its free) https://developer.spotify.com/dashboard/login

From https://developer.spotify.com/dashboard/applications :
- Select "create an app"
- Choose an app name and description,  eg. "test", "test" 
- Select "edit settings"
- Set redirct url, eg. http://127.0.0.1:5000
- From the application page select show "client secret" either (1)  create a .env file ad save in under the 'app', 'util' and 'test' folders. 
- .env will appear as follows: 
```
SPOTIPY_CLIENT_ID='YOUR_CLIENT_ID'
SPOTIPY_CLIENT_SECRET='YOUR_CLIENT_SECRET'
SPOTIPY_REDIRECT_URI='YOUR_REDIRECT_URL'
```

or (2) in the python environment (linux only):
```
export SPOTIPY_CLIENT_ID='YOUR_CLIENT_ID'
```
```
export SPOTIPY_CLIENT_SECRET='YOUR_CLIENT_SECRET'
```
```
export SPOTIPY_REDIRECT_URI='YOUR_REDIRECT_URL'
```
## Usage

To run this webapp on your machine, go to the directory where this repository sits, and type in your terminal:
```python
python dashapp.py
```
This will launch a server locally on your machine. Clicking on the url shown will bring you to Mus-X home page in your web browser. Then you can sign in with your Spotify credentials to start the jorney of understanding your music tastes!

Note: We have also deployed this web app on AWS for the period of this course, but the site will be down when our credits run out.

Note 2: Initial run of the app may not show the graphs as the CSVs are being built in the background. You should see the progress in the console. You should have 8 CSVs under .csv_caches/'YOUR_USER_ID' when the process is completed. You may have to restart the app and sign-in again to view the graphs.

Note 3: The recommendation system model are a couple of big file which can be downloaded from here: [Model Link](https://drive.google.com/file/d/1F0i5-YRZ8ZgEGaADKYXz95X9hWPk3yfO/view?usp=sharing) and need to be placed under app/assets/rec-files for the recommendation engine to work.

## OKR Summary

There are a several main milestones that defined this project.

![app architetcure](readme_images/OKRs.png?raw=true)

## Application Architecture

We used Flask as the web framework, and integrated Dash by Plotly to create interactive data visualization plots that ties to modern UI elements. The web application is deployed on AWS EC2 Scaling Group, with S3 used for large files storage and Dynamo DB for session cache. Data analysis, processing and integration are coded in Python. The Spotify Python API and OAuth Security handles the Spotify user log-in credentials. 

![app architetcure](readme_images/app_architetcure1.png?raw=true)

## Data Visualization

The plots in this dashcoard are coded using Plotly. We wrote callback functions to allow a more interactive data exploration experience for the user.

### All Tracks TSNE

We used TSNE(T-Distributed Stochastic Neighbor Embedding) to cluster and visualize tracks in a users playlists based on the 13 audio features of each track. The user can select playlists of interest in the dropdown list to visualize the similarity of songs.

![TSNE plot](readme_images/TSNE.png?raw=true)

### Genre Breakdown Over Time

![data visual plot](readme_images/genre_time.png?raw=true)

### Top Artists & Tracks

![top artists & tracks](readme_images/top_artists.png?raw=true)

### Songs Recommender Model

We built a user-item collaborative filtering recommender to generate personalized song recommendations for users. The model applies SVD (Probablistic Matrix Factorization) algorithm to learn user preferences of songs from external training dataset, and predicts scores of songs during inference. The user can export the recommended tracks playlist to Spotify by a simple button-click.

![recommender](readme_images/recommender.png?raw=true)

### To View Doumentation 
Documentation is created via Sphinx. From  the section of the dashboard titled "check out our documentation" select the made "made with" to be redirected  to our documentation page

![Docs Page](readme_images/Documentation.png?raw=true)
## To run code coverage tests:
Coverage report is generated from the coverage python package

chromedriver needs to be in the path variable, it can be added using:

```
export PATH=$PATH:/path/to/chromedriver
```

From the ECE229 (root) directory, run the following commands: 
```
coverage run --source=app -m pytest
```
```
coverage report -m
```
