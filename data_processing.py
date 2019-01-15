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



tbl2 = pd.read_sql_query("SELECT MovieId, GenreId, 1 AS IfExists FROM MovieGenres ", conn)
movie_id = np.unique(tbl2['MovieId'].values)
movie_id_index = np.arange(0,len(movie_id))
movies_indexed = pd.DataFrame({'movie_id_index': movie_id_index, 'movie_id': movie_id})
tbl3 = tbl.merge(movies_indexed,  left_on = "MovieId", right_on = "movie_id")


data = tbl3['Rating'].values
row = tbl3['UserId'].values - 1
col = tbl3['movie_id_index'].values


shape = (10000, len(movie_id))

sparse_matrix = coo_matrix((data,(row,col)), shape = shape)
print(repr(sparse_matrix))


#tbl2
#
#data2 = tbl2['IfExists'].values
#row2 = tbl2['MovieId'].values - 1
#col2 = tbl2['GenreId'].values - 1
#
#
#sparse_matrix2 = coo_matrix((data2,(row2,col2)), shape = (max(row2)+1,max(col2)+1))
#print(repr(sparse_matrix2))
#print(str(sparse_matrix2.getrow(1)))

from lightfm.datasets import fetch_movielens
from lightfm import LightFM
model = LightFM(loss='warp')
model.fit(sparse_matrix, epochs=30, num_threads=2)
n_users, n_items = sparse_matrix.shape

scores = model.predict(0,np.arange(n_items))
top_items = np.argsort(-scores)
top_items
