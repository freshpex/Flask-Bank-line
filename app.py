from flask import Flask, render_template, request, g, session, jsonify, url_for, redirect, flash, send_from_directory
import sqlite3, requests, hashlib, os, warnings, requests, datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(16)
DATABASE_FILE = 'database.db'

# Function handling the hash password
def hash_password(password):
    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac(
        'sha256', password.encode('utf-8'), salt, 100000)
    return salt + password_hash

# Function handling the password checker for correctness and tallying
def check_password(password, password_hash):
    salt = password_hash[:16]
    stored_password_hash = password_hash[16:]
    new_password_hash = hashlib.pbkdf2_hmac(
        'sha256', password.encode('utf-8'), salt, 100000)
    return new_password_hash == stored_password_hash


def get_user(user_id):
    query = "SELECT id, email, first_name, last_name, username, gender, account, password_hash, notification_enabled, privacy_enabled FROM users WHERE id = ?"
    args = (user_id,)
    row = db_query(query, args)

    if not row:
        return None

    return {
        'id': row[0][0], 'email': row[0][1], 'first_name': row[0][2], 'last_name': row[0][3], 'username': row[0][4], 'gender': row[0][5], 'account': row[0][6], 'password': row[0][7], 'notification_enabled': bool(row[0][8]), 'privacy_enabled': bool(row[0][9])
    }


@app.before_request
def load_user():
    user_id = session.get('user_id')
    if user_id is not None:
        g.user = get_user(user_id)
    else:
        g.user = None

# Get a useable connection to the database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE_FILE)
        db.row_factory = sqlite3.Row
    return db

# Close the database connection when the app shuts down
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# return the results from a database query
def db_query(query, args=None):
    cur = get_db().execute(query, args or ())
    rv = cur.fetchall()
    cur.close()
    return rv

# execute a database query
def db_execute(query, args=()):
    conn = get_db()
    conn.execute(query, args)
    conn.commit()
    return True

def check_user_exists(email, username):
    # Check if user with the given email or username exists
    query = "SELECT id FROM users WHERE email = ? OR username = ?"
    args = (email, username)
    user = db_query(query, args)

    return bool(user)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        email = request.form['email']
        username = secure_filename(request.form['username'])
        account = request.form['account']
        password = request.form['password']
        session['username'] = username

        # Check if user already exists
        if check_user_exists(email, username):
            error_message = 'User with the same email or username already exists.'
            return render_template('signup.html', error=error_message)

        # Hash password
        password_hash = hash_password(password)

        # Insert user into the database
        query = "INSERT INTO users (email, username, account, password_hash) VALUES (?, ?, ?, ?)"
        args = (email, username, account, password_hash)

        db_execute(query, args)

        # Redirect to sign-in page
        return redirect(url_for('login'))

    # Render sign-up page
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']

        # Check if user exists in database
        query = "SELECT id, password_hash FROM users WHERE username = ?"
        args = (username,)
        row = db_query(query, args)

        if not row:  # Check if row is empty
            # User not found
            error = 'Invalid email or password'
            return render_template('login.html', error=error)

        # Check password
        password_hash = row[0][1]
        if check_password(password, password_hash):
            # Password is correct, store user ID in session
            # Access the first row's first element
            session['user_id'] = row[0][0]
            return redirect('/')
        else:
            # Password is incorrect
            error = 'Invalid email or password'
            return render_template('login.html', error=error)

    # Render sign-in page
    return render_template('login.html')


@app.route('/signout')
def signout():
    visited = "Sign out"
    user_id = session['user_id']

    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

   
@app.route('/')
def index():
    return render_template('index.html')




    

if __name__ == '__main__':
    app.run()
