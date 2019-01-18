import pickle
from lightfm import LightFM
import pandas as pd
from scipy.sparse import coo_matrix
import numpy as np
import sqlite3

class Engine:
    conn = sqlite3.connect("jjmovie.db")
    c = conn.cursor()
    model = pickle.load(open("lightfm.pkl","rb"))
    tbl = pd.read_sql_query("SELECT UserId, MovieId, Rating FROM Ratings WHERE Rating IS NOT NULL", conn)
    df = pd.read_sql_query("SELECT DISTINCT(MovieId) as MovieId FROM Ratings WHERE Rating IS NOT NULL ORDER BY MovieId ", conn)
    df['index1'] = df.index
    tbl = df.merge(tbl, left_on= "MovieId", right_on ="MovieId")
    links = pd.read_sql_query("SELECT * FROM MovieIdLink", conn)
    n_items = model.item_embeddings.shape[0]
    conn.close()
    def __init__(self):
        self.top_items = None

    def generate_recommendations(self, user):
        reviewed = self.tbl.index1[self.tbl['UserId'] == user+1].values
        movies_to_pick =  np.arange(self.n_items)[np.logical_not(np.isin(np.arange(self.n_items), reviewed))]
        scores = self.model.predict(user ,movies_to_pick)
        self.top_items = np.arange(self.n_items)[np.argsort(-scores)]
        return(True)

    def get_top_n(self,n):
        recommendations = np.array(self.df.loc[self.df.index1.isin(self.top_items[0:n])].merge(self.links, left_on = 'MovieId', right_on = 'MovieId' ).TmdbId)
        return(tuple(recommendations))
