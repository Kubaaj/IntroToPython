import bcrypt
import sqlite3
conn = sqlite3.connect('jjmovie.db')
c = conn.cursor()
c.execute("SELECT UserId from Users")
UserIds = c.fetchall()
UserIds  = [ID[0] for ID in UserIds]
for ID in UserIds:
    c.execute("SELECT password FROM Users WHERE UserId = ?",(ID,))
    password = c.fetchall()
    password = str.encode(password[0][0])
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password, salt)
    c.execute("UPDATE Users SET Salt = ?, Hash = ? WHERE UserId = ?", (salt,hash,ID))
conn.commit()
conn.close()
