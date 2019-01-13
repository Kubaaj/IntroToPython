import sqlite3
import pandas as pd
from scipy.sparse import coo_matrix
import numpy as np
conn = sqlite3.connect("jjmovie.db")
c = conn.cursor()
c.execute("PRAGMA table_info(Movies)")
c.fetchall()


tbl = pd.read_sql_query("SELECT UserId, MovieId, Rating FROM Ratings ", conn)

data = tbl['Rating'].values
row = tbl['UserId'].values - 1
col = tbl['MovieId'].values - 1


sparse_matrix = coo_matrix((data,(row,col)), shape = (max(row)+1,max(col)+1))
print(repr(sparse_matrix))


import numpy as np
from lightfm.datasets import fetch_movielens
from lightfm import LightFM
model = LightFM(loss='warp')
model.fit(sparse_matrix, epochs=30, num_threads=2)
n_users, n_items = sparse_matrix.shape


scores = model.predict(1,np.arange(n_items))
top_items = np.argsort(-scores)
top_items


tbl = pd.read_sql_query("SELECT Title FROM Movies WHERE  ", conn)
