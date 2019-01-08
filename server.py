from bottle import Bottle, route, run, template, get, post, debug, static_file, request, redirect, response
import time
import random
import string
import logging
import logging.handlers
import datetime
import sqlite3
import cgi


secretKey = "SDMDSIUDSFYODS&TTFS987f9ds7f8sd6DFOUFYWE&FY"
log = logging.getLogger('bottle')
log.setLevel('INFO')
h = logging.handlers.TimedRotatingFileHandler('logs/nlog', when='midnight', backupCount=9999)
f = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
h.setFormatter(f)
log.addHandler(h)

@route('/login')
def login_page(error = None):
    return template('LoginPage.html', error=error)



@route('/login', method='POST')
def login():
    if request.forms.get('signin', default=False):
        error = None
        loginName = request.forms.get('login_name', default=False)
        password = request.forms.get('password', default=False)
        randStr = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(18))
        log.info(str(loginName) + ' ' + request.method + ' ' + request.url + ' ' + request.environ.get('REMOTE_ADDR'))

        conn = sqlite3.connect('jjmovie.db')
        c = conn.cursor()
        c.execute("SELECT CASE WHEN COUNT(*) = 1 THEN  CAST( 1 as BIT ) ELSE CAST( 0 as BIT ) END AS LoginPairExists FROM users WHERE Login = ? AND Password = ? LIMIT 1", (loginName, password))
        credsCorrect = c.fetchone()[0] == 1

        if credsCorrect:
            ts = None
            if request.forms.get('remember'):
                ts = datetime.datetime.now()+datetime.timedelta(days=1)
                response.set_cookie("user", loginName, secret=secretKey, expires = ts )
                response.set_cookie("randStr", randStr, secret=secretKey, expires = ts)
            else:
                response.set_cookie("user", loginName, secret=secretKey)
                response.set_cookie("randStr", randStr, secret=secretKey)

            c.execute("UPDATE Users SET LastSeen = datetime('now') WHERE Login = ?", (loginName,))
            c.execute("UPDATE Users SET LoggedIn = 1 WHERE Login = ?", (loginName,))
            c.execute("UPDATE Users SET RandStr = ? WHERE Login = ?", (randStr,loginName))
            c.execute("SELECT * FROM users WHERE Login = ? LIMIT 1", (loginName, ))

            conn.commit()
            conn.close()
            redirect('/index')
            return True
        else:
            error = 'Invalid Credentials. Please try again.'
        conn.commit()
        conn.close()
        return login_page(error)
    else:
        redirect('/signup')
        return False


@route('/signout')
def signout():
        loginName = checkAuth()
        conn = sqlite3.connect('jjmovie.db')
        c = conn.cursor()
        c.execute("UPDATE Users SET LoggedIn = 0 WHERE Login = ?", (loginName,))
        conn.commit()
        conn.close()
        redirect("/index")

@route('/signup')
def signup_page(error = None):
    return template('SingUpPage.html', error=error)



@route('/signup', method='POST')
def signup():
    error = None
    name = request.forms.get('name', default=False)
    loginName = request.forms.get('login_name', default=False)
    password = request.forms.get('password', default=False)
    repPassword = request.forms.get('rep_password', default=False)

    randStr = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(18))
    log.info(str(loginName) + ' ' + request.method + ' ' + request.url + ' ' + request.environ.get('REMOTE_ADDR'))
    if (loginName in users):
        error = "Account for this email address already exists"
    elif password != repPassword:
        error = "Passwords do not match"
    else:
        user_data = {"name":name, "password":password, "email":loginName, "loggedIn":False,  "randStr":"", "lastSeen":0}
        users[loginName] = user_data

        redirect('/login')
        return True
    return signup_page(error)


@route('/')
@route('/index')
def main_page():
    loginName = checkAuth()
    
    conn = sqlite3.connect('jjmovie.db')
    c = conn.cursor()
    sql = """
        CREATE VIEW BestFilms AS 
        SELECT m.MovieId, m.Title, m.VoteAverage, m.VoteCount, p.PosterPath 
        FROM Movies m 
        LEFT JOIN Posters p ON m.MovieId = p.MovieId 
        WHERE VoteCount > 1050 AND VoteCount IS NOT NULL 
        ORDER BY VoteAverage DESC, VoteCount DESC 
        LIMIT 6;
    """
    c.execute(str(sql))
    c.execute("SELECT PosterPath FROM BestFilms LIMIT 1;")
    best1=c.fetchone()
    best1_2 = 'https://image.tmdb.org/t/p/w185' + best1[0]
    c.execute("SELECT PosterPath FROM BestFilms LIMIT 1 OFFSET 1;")
    best2=c.fetchone()
    best2_2 = 'https://image.tmdb.org/t/p/w185' + best2[0]
    c.execute("SELECT PosterPath FROM BestFilms LIMIT 1 OFFSET 2;")
    best3=c.fetchone()
    best3_2 = 'https://image.tmdb.org/t/p/w185' + best3[0]
    c.execute("SELECT PosterPath FROM BestFilms LIMIT 1 OFFSET 3;")
    best4=c.fetchone()
    best4_2 = 'https://image.tmdb.org/t/p/w185' + best4[0]
    c.execute("SELECT PosterPath FROM BestFilms LIMIT 1 OFFSET 4;")
    best5=c.fetchone()
    best5_2 = 'https://image.tmdb.org/t/p/w185' + best5[0]
    c.execute("SELECT PosterPath FROM BestFilms LIMIT 1 OFFSET 5;")
    best6=c.fetchone()
    best6_2 = 'https://image.tmdb.org/t/p/w185' + best6[0]
    c.execute("DROP VIEW BestFilms;")
    
    c.execute("SELECT p.PosterPath FROM Movies m LEFT JOIN Posters p ON m.MovieId = p.MovieId LEFT JOIN Rentals r ON m.MovieId = r.MovieId LEFT JOIN Users u ON r.UserId = u.UserId WHERE Login = ? ORDER BY date(RentalDate) DESC LIMIT 1;", (loginName,))
    rent1=c.fetchone()
    if rent1 == None:
        rent1_2 = "http://www.apmusicstudio.com/images/InnerImages/NoVideo.jpg"
    else:
        rent1_2 = 'https://image.tmdb.org/t/p/w185' + rent1[0]
    c.execute("SELECT p.PosterPath FROM Movies m LEFT JOIN Posters p ON m.MovieId = p.MovieId LEFT JOIN Rentals r ON m.MovieId = r.MovieId LEFT JOIN Users u ON r.UserId = u.UserId WHERE Login = ? ORDER BY date(RentalDate) DESC LIMIT 1 OFFSET 1;", (loginName,))
    rent2=c.fetchone()
    if rent2 == None:
        rent2_2 = "http://www.apmusicstudio.com/images/InnerImages/NoVideo.jpg"
    else:
        rent2_2 = 'https://image.tmdb.org/t/p/w185' + rent2[0]
    c.execute("SELECT p.PosterPath FROM Movies m LEFT JOIN Posters p ON m.MovieId = p.MovieId LEFT JOIN Rentals r ON m.MovieId = r.MovieId LEFT JOIN Users u ON r.UserId = u.UserId WHERE Login = ? ORDER BY date(RentalDate) DESC LIMIT 1 OFFSET 2;", (loginName,))
    rent3=c.fetchone()
    if rent3 == None:
        rent3_2 = "http://www.apmusicstudio.com/images/InnerImages/NoVideo.jpg"
    else:
        rent3_2 = 'https://image.tmdb.org/t/p/w185' + rent3[0]
    c.execute("SELECT p.PosterPath FROM Movies m LEFT JOIN Posters p ON m.MovieId = p.MovieId LEFT JOIN Rentals r ON m.MovieId = r.MovieId LEFT JOIN Users u ON r.UserId = u.UserId WHERE Login = ? ORDER BY date(RentalDate) DESC LIMIT 1 OFFSET 3;", (loginName,))
    rent4=c.fetchone()
    if rent4 == None:
        rent4_2 = "http://www.apmusicstudio.com/images/InnerImages/NoVideo.jpg"
    else:
        rent4_2 = 'https://image.tmdb.org/t/p/w185' + rent4[0]
    c.execute("SELECT p.PosterPath FROM Movies m LEFT JOIN Posters p ON m.MovieId = p.MovieId LEFT JOIN Rentals r ON m.MovieId = r.MovieId LEFT JOIN Users u ON r.UserId = u.UserId WHERE Login = ? ORDER BY date(RentalDate) DESC LIMIT 1 OFFSET 4;", (loginName,))
    rent5=c.fetchone()
    if rent5 == None:
        rent5_2 = "http://www.apmusicstudio.com/images/InnerImages/NoVideo.jpg"
    else:
        rent5_2 = 'https://image.tmdb.org/t/p/w185' + rent5[0]
    c.execute("SELECT p.PosterPath FROM Movies m LEFT JOIN Posters p ON m.MovieId = p.MovieId LEFT JOIN Rentals r ON m.MovieId = r.MovieId LEFT JOIN Users u ON r.UserId = u.UserId WHERE Login = ? ORDER BY date(RentalDate) DESC LIMIT 1 OFFSET 5;", (loginName,))
    rent6=c.fetchone()
    if rent6 == None:
        rent6_2 = "http://www.apmusicstudio.com/images/InnerImages/NoVideo.jpg"
    else:
        rent6_2 = 'https://image.tmdb.org/t/p/w185' + rent6[0]
    
        conn = sqlite3.connect('jjmovie.db')
    c = conn.cursor()
    sql = """
        CREATE VIEW PopularFilms AS 
        SELECT m.MovieId, m.Title, cast(m.Popularity as int) as Pop, p.PosterPath 
        FROM Movies m 
        LEFT JOIN Posters p ON m.MovieId = p.MovieId 
        ORDER BY Pop DESC 
        LIMIT 6;    
    """
    c.execute(str(sql))
    c.execute("SELECT PosterPath FROM PopularFilms LIMIT 1;")
    pop1=c.fetchone()
    pop1_2 = 'https://image.tmdb.org/t/p/w185' + pop1[0]
    c.execute("SELECT PosterPath FROM PopularFilms LIMIT 1 OFFSET 1;")
    pop2=c.fetchone()
    pop2_2 = 'https://image.tmdb.org/t/p/w185' + pop2[0]
    c.execute("SELECT PosterPath FROM PopularFilms LIMIT 1 OFFSET 2;")
    pop3=c.fetchone()
    pop3_2 = 'https://image.tmdb.org/t/p/w185' + pop3[0]
    c.execute("SELECT PosterPath FROM PopularFilms LIMIT 1 OFFSET 3;")
    pop4=c.fetchone()
    pop4_2 = 'https://image.tmdb.org/t/p/w185' + pop4[0]
    c.execute("SELECT PosterPath FROM PopularFilms LIMIT 1 OFFSET 4;")
    pop5=c.fetchone()
    pop5_2 = 'https://image.tmdb.org/t/p/w185' + pop5[0]
    c.execute("SELECT PosterPath FROM PopularFilms LIMIT 1 OFFSET 5;")
    pop6=c.fetchone()
    pop6_2 = 'https://image.tmdb.org/t/p/w185' + pop6[0]
    c.execute("DROP VIEW PopularFilms;")
    
    conn.commit()
    conn.close()
    return template('MainPage.html',username = loginName, best1 = best1_2, best2 = best2_2, best3 = best3_2, best4 = best4_2, best5 = best5_2, best6 = best6_2, rent1 = rent1_2, rent2 = rent2_2, rent3 = rent3_2, rent4 = rent4_2, rent5 = rent5_2, rent6 = rent6_2, pop1 = pop1_2, pop2 = pop2_2, pop3 = pop3_2, pop4 = pop4_2, pop5 = pop5_2, pop6 = pop6_2)

    request.forms.get('search_term')

@route('/index', method='POST')
def mainPageSearch():
    search_term = request.forms.get('search_term')
    redirect('/search/' + search_term)
    
    
    
@route('/search/<search_term>')
def search(search_term):
    loginName = checkAuth()
    
    #form = cgi.FieldStorage()
    #searchString =  form.getvalue('searchbox')
    searchString = search_term.upper()
    conn = sqlite3.connect('jjmovie.db')
    c = conn.cursor()
    sql = """
        SELECT DISTINCT m.MovieId, m.Title, m.Popularity, m.VoteAverage, p.PosterPath,
        CASE 
        WHEN INSTR(UPPER(m.Title), ?) THEN 5 
        ELSE (CASE WHEN INSTR(UPPER(k.Keyword), ?) THEN 4 
              ELSE 3 END) 
        END AS SearchValue 

        FROM Movies m
        LEFT JOIN MoviesKeywords mk ON m.MovieId = mk.MovieId
        LEFT JOIN Keywords k ON mk.KeywordId = k.KeywordId
        LEFT JOIN MovieGenres mg ON m.MovieId = mg.MovieId
        LEFT JOIN Genres g ON mg.GenreId = g.GenreId
        LEFT JOIN Posters p ON m.MovieId = p.MovieId
        WHERE INSTR(UPPER(m.Title), ?) OR INSTR(UPPER(k.Keyword), ?) OR INSTR(UPPER(g.GenreName), ?)
        ORDER BY SearchValue DESC, CAST(m.Popularity AS INT) DESC, CAST(m.VoteAverage AS INT)  DESC LIMIT 20;
    """
    sql2 = """
    SELECT COUNT(DISTINCT m.MovieId)
        FROM Movies m
        LEFT JOIN MoviesKeywords mk ON m.MovieId = mk.MovieId
        LEFT JOIN Keywords k ON mk.KeywordId = k.KeywordId
        LEFT JOIN MovieGenres mg ON m.MovieId = mg.MovieId
        LEFT JOIN Genres g ON mg.GenreId = g.GenreId
        LEFT JOIN Posters p ON m.MovieId = p.MovieId
        WHERE INSTR(UPPER(m.Title), ?) OR INSTR(UPPER(k.Keyword), ?) OR INSTR(UPPER(g.GenreName), ?);
    """
    c.execute(str(sql2), (searchString, searchString, searchString,))
    num = c.fetchall()
    c.execute(str(sql), (searchString, searchString, searchString, searchString, searchString,))
    s1=c.fetchall()
    num = num[0][0]
    print('NUM: ' + str(num))
    s2 = [None] * 20
    for i in range(20):
        if i < int(num):
            s2[i] = 'https://image.tmdb.org/t/p/w185' + str(s1[i][4])
        else:
            s2[i] = "http://www.apmusicstudio.com/images/InnerImages/NoVideo.jpg"

    s1 = "http://www.apmusicstudio.com/images/InnerImages/NoVideo.jpg"
    conn.commit()
    conn.close()
    return template('Search.html', s1 = s1, s2 = s2) #, s2 = s1_2, s3 = s1_3, s4 = s1_4, s5 = s1_5, s6 = s1_6, s7 = s1_7, s8 = s1_8, s9 = s1_9, s10 = s1_10)

@route('/search/<search_term>', method='POST')
def searchNextSearch(search_term):
    search_term = request.forms.get('search_term')
    redirect('/search/' + search_term)


@route("/forgot")
def forgot_page(error = None):
    return template('ForgotPassword.html', error=error)

@route('/forgot', method='POST')
def reset():
        error = None
        loginName = request.forms.get('login_name', default=False)
        if (loginName in users):
            random_password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            users[loginName]["password"] =  random_password

            redirect("/index")
        else:
            error =  "Account for this email does not exists"
        return forgot_page(error)



def checkAuth():
    loginName = request.get_cookie("user", secret=secretKey)
    randStr = request.get_cookie("randStr", secret=secretKey)
    log.info(str(loginName) + ' ' + request.method + ' ' + request.url + ' ' + request.environ.get('REMOTE_ADDR'))

    conn = sqlite3.connect('jjmovie.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE Login = ? LIMIT 1", (loginName, ))

    c.execute("SELECT CASE WHEN COUNT(*) = 1 THEN  CAST( 1 as BIT ) ELSE CAST( 0 as BIT ) END AS IsAuth FROM users WHERE Login = ? AND RandStr = ? AND LoggedIn == 1 AND LastSeen > ?  LIMIT 1", (loginName, randStr, time.time() - 3600 ))
    IsAuth = c.fetchone()[0] == 1


    # (loginName in users) and (users[loginName].get("randStr", "") == randStr) and (users[loginName]["loggedIn"] == True) and (time.time() - users[loginName]["lastSeen"] < 3600)
    if IsAuth:
        c.execute("UPDATE Users SET LastSeen = datetime('now') WHERE Login = ?", (loginName,))
        conn.commit()
        conn.close()
        return loginName
    return redirect('/login')



run(host='localhost', port=8080, debug=True)


#clean up
