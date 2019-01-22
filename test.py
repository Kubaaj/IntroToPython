# -*- coding: utf-8 -*-
"""
Created on Sun Jan  6 00:57:27 2019

@author: jakub
"""
import sqlite3
conn = sqlite3.connect('jjmovie.db')
c = conn.cursor()
#c.execute("Create View BestFilms AS SELECT m.MovieId, m.Title, m.VoteAverage, m.VoteCount, p.PosterPath FROM Movies m LEFT JOIN Posters p ON m.MovieId = p.MovieId WHERE VoteCount > 1000 AND VoteCount IS NOT NULL AND VoteCount ORDER BY VoteAverage DESC, VoteCount DESC LIMIT 5;")
c.execute("SELECT PosterPath FROM BestFilms LIMIT 1;")
best1=c.fetchone()
print(best1[0])
best1_2 = 'https://image.tmdb.org/t/p/w185' + best1[0]
print(best1_2)