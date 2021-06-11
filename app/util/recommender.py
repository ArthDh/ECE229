import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

from surprise import SVD
from surprise import accuracy
from surprise import dump

import os
import time

import spotipy
from dotenv import load_dotenv


# Package Dependencies:
# numpy==1.20.3
# scikit-surprise==1.1.1
# scipy==1.5.4
# File dependencies:
# songs_pool.csv
# SPF_user_song_score.csv
# recommender_model_final.pkl

def get_user_song_df(saved_songs_csv):
    """
    saved_songs: a list of Spotify song ids for user saved songs
    return: a user song preference pd.DataFrame for find_sim_user
    """
    saved_songs = pd.read_csv(saved_songs_csv).id.to_list()
    user_data = pd.DataFrame.from_dict(
        {'user_id': ['TEMP' for i in range(len(saved_songs))], 'song_id_SPF': saved_songs,
         'score': [10 for i in range(len(saved_songs))]})
    return user_data, saved_songs


def get_new_songs(saved_songs, songs_pool_file=None):
    """
    get a list of tracks the user hasn't liked as the pool of tracks for recommendation
    saved_songs: a list of Spotify song ids for user saved songs
    return: a list of Spotify song ID
    """
    songs_pool = pd.read_csv(songs_pool_file).iloc[:, 0]
    all_songs = set(songs_pool.to_list())
    new_songs = list(all_songs - set(saved_songs))

    return new_songs


def get_sim_user(user_data, song_id_user_csv=None):
    """
    user_data: pd.DataFrame with weighted user saved songs
    song_id_user_csv: filemane for curated user id - song id - rating dataset
    returns: user_id of most similar user in the training set
    """
    num_entries = 500000  # dataset to large to be used in full, has to cap # of entries
    df_song_id_user = pd.read_csv(song_id_user_csv).iloc[:num_entries, :10]
    df_song_id_user.append(user_data)

    song_user = df_song_id_user.pivot(index='user_id', columns='song_id_SPF', values='score').fillna(0)

    # obtain a sparse matrix
    song_user_mat = csr_matrix(song_user.values)
    # calculate pairwise cosine similarity between users based on listening preference
    cos_sim = cosine_similarity(song_user_mat)
    # get most similar user
    sim_score = cos_sim[-1, :-1].max()
    user_index = cos_sim[-1, :-1].argmax()

    return song_user.index[user_index], sim_score


def generate_rec_songs(user_id=None, top=20, pool=None, model=None):
    """
    user_id: MSD user_id in training set
    top: number of songs to recommend
    pool: a list of Spotify song ID to recommend from
    return: (top_songs, top_scores) a list of top song_ids and a list of predicted ratings(preference) to these songs
    """

    # load trained collaborative filtering model
    (predictions, final_algorithm) = dump.load(model)

    top_ten = []
    pred_scores = []
    for song in pool:
        pred = final_algorithm.predict(user_id, song)
        pred_scores.append((pred.iid, pred.est))

    pred_scores.sort(key=lambda tup: tup[1], reverse=True)
    top_songs = [song for song, score in pred_scores[:top]]
    top_scores = [score for song, score in pred_scores[:top]]

    return top_songs, top_scores





