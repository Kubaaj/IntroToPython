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
    tbl = tbl.merge(df, left_on= "MovieId", right_on ="MovieId")
    tbl[tbl.UserId == 1]
    links = pd.read_sql_query("SELECT * FROM MovieIdLink WHERE TmdbId IN (SELECT MovieId FROM Movies)", conn)
    n_items = model.item_embeddings.shape[0]
    conn.close()
    def __init__(self):
        self.top_items = None
        self.user = None
    def generate_recommendations(self, user):
        self.user = user
        scores = self.model.predict(user-1 ,np.arange(self.n_items))
        self.top_items = np.arange(self.n_items)[np.argsort(-scores)]
        return(True)

    def get_top_n(self,n):
        df2 = self.df.merge(self.links, how ='inner', left_on = 'MovieId', right_on = 'MovieId' )
        recommendations = np.array(df2.loc[df2.index1.isin(self.top_items[0:n])].TmdbId)
        return(tuple(recommendations))
