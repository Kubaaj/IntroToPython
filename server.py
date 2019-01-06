from bottle import Bottle, route, run, template, get, post, debug, static_file, request, redirect, response
import time
import random
import string
import logging
import logging.handlers
import datetime
import sqlite3


from users import users
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
        if (loginName in users) and users[loginName]["password"] == password:
            ts = None
            if request.forms.get('remember'):
                ts = datetime.datetime.now()+datetime.timedelta(days=1)
            else:
                response.set_cookie("user", loginName, secret=secretKey)
                response.set_cookie("randStr", randStr, secret=secretKey)
                conn = sqlite3.connect('jjmovie.db')
                c = conn.cursor()
                c.execute("UPDATE Users SET LastSeen = datetime('now') WHERE Login = ?", (loginName,))

                conn.commit()
                conn.close()
            users[loginName]["loggedIn"] = True
            users[loginName]["randStr"] = randStr
            users[loginName]["lastSeen"] = time.time()

            redirect('/index')
            return True
        else:
            error = 'Invalid Credentials. Please try again.'
        return login_page(error)
    else:
        redirect('/signup')
        return False


@route('/signout')
def signout():
        loginName = checkAuth()
        users[loginName]["loggedIn"] = False
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
        print(users[loginName])
        redirect('/login')
        return True
    return signup_page(error)


@route('/')
@route('/index')
def main_page():
    conn = sqlite3.connect('jjmovie.db')
    c = conn.cursor()
    c.execute("Create View BestFilms AS SELECT m.MovieId, m.Title, m.VoteAverage, m.VoteCount, p.PosterPath FROM Movies m LEFT JOIN Posters p ON m.MovieId = p.MovieId WHERE VoteCount > 1050 AND VoteCount IS NOT NULL ORDER BY VoteAverage DESC, VoteCount DESC LIMIT 6;")
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
    conn.commit()
    conn.close()
    loginName = checkAuth()
    userName = users[loginName]["name"]
    return template('MainPage.html',username = userName, best1 = best1_2, best2 = best2_2, best3 = best3_2, best4 = best4_2, best5 = best5_2, best6 = best6_2)


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
            print(random_password)
            redirect("/index")
        else:
            error =  "Account for this email does not exists"
        return forgot_page(error)



def checkAuth():
    loginName = request.get_cookie("user", secret=secretKey)
    randStr = request.get_cookie("randStr", secret=secretKey)
    log.info(str(loginName) + ' ' + request.method + ' ' +
             request.url + ' ' + request.environ.get('REMOTE_ADDR'))
    if (loginName in users) and (users[loginName].get("randStr", "") == randStr) and (users[loginName]["loggedIn"] == True) and (time.time() - users[loginName]["lastSeen"] < 3600):
        users[loginName]["lastSeen"] = time.time()
        return loginName
    return redirect('/login')



run(host='localhost', port=8080, debug=True)
