from bottle import Bottle, route, run, template, get, post, debug, static_file, request, redirect, response
import time
import random
import string
import logging
import logging.handlers
import datetime

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
            if request.forms.get('remember'): ts = datetime.datetime.now()+datetime.timedelta(days=1)
            response.set_cookie("user", loginName, secret=secretKey, expires = ts)
            response.set_cookie("randStr", randStr, secret=secretKey, expires = ts)
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
    userName = users[loginName]["name"]
    return template('MainPage.html',username = userName)


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
