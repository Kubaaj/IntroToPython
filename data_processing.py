import sqlite3
import pandas as pd
from scipy.sparse import coo_matrix
import numpy as np
conn = sqlite3.connect("jjmovie.db")
c = conn.cursor()
c.execute("PRAGMA table_info(Movies)")
c.fetchall()


tbl = pd.read_sql_query("SELECT UserId, MovieId, Rating FROM Ratings ", conn)
tbl

data = tbl['Rating'].values
row = tbl['UserId'].values - 1
col = tbl['MovieId'].values - 1


sparse_matrix = coo_matrix((data,(row,col)), shape = (max(row)+1,max(col)+1))
print(repr(sparse_matrix))

tbl2 = pd.read_sql_query("SELECT MovieId, GenreId, 1 AS IfExists FROM MovieGenres ", conn)
tbl2

data2 = tbl2['IfExists'].values
row2 = tbl2['MovieId'].values - 1
col2 = tbl2['GenreId'].values - 1


sparse_matrix2 = coo_matrix((data2,(row2,col2)), shape = (max(row2)+1,max(col2)+1))
print(repr(sparse_matrix2))


from lightfm.datasets import fetch_movielens
from lightfm import LightFM
model = LightFM(loss='warp')
model.fit(sparse_matrix, epochs=30, num_threads=2)
n_users, n_items = sparse_matrix.shape

scores = model.predict(1,np.arange(n_items))
top_items = np.argsort(-scores)
top_items