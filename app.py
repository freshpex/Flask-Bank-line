from flask import Flask, render_template, request, g, session, jsonify, url_for, redirect, flash, send_from_directory
import sqlite3, requests, hashlib, os, warnings, requests, datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(16)
<<<<<<< HEAD
DATABASE_FILE = 'database.db'
=======
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
DATABASE_FILE = 'instance/database.db'

db.init_app(app)
>>>>>>> 9b64c7a (work flow)

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
        password = request.form['password']
        session['username'] = username

        # Check if user already exists
        if check_user_exists(email, username):
            error_message = 'User with the same email or username already exists.'
            return render_template('signup.html', error=error_message)

        # Hash password
        password_hash = hash_password(password)

        # Insert user into the database
<<<<<<< HEAD
        query = "INSERT INTO users (email, username, account, password_hash) VALUES (?, ?, ?, ?)"
        args = (email, username, account, password_hash)
=======
        query = "INSERT INTO user (email, username, password) VALUES (?, ?, ?)"
        args = (email, username, password_hash)
>>>>>>> 9b64c7a (work flow)

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
            return redirect('/dashboard')
        else:
            # Password is incorrect
            error = 'Invalid email or password'
            return render_template('login.html', error=error)

    # Render sign-in page
    return render_template('login.html')


@app.route('/signout')
def signout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

   
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if g.user is None:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/transaction')
def transaction():
    if g.user is None:
        return redirect(url_for('login'))
    user_accounts = User.query.filter_by(id=g.user['id']).all()
    return render_template('transaction.html', user_accounts=user_accounts)

@app.route('/products')
def products():
    if g.user is None:
        return redirect(url_for('login'))
    return render_template('products.html')

@app.route('/createaccount')
def createaccount():
    if g.user is None:
        return redirect(url_for('login'))
<<<<<<< HEAD
=======
    if request.method == 'POST':
        try:
            fname = request.form['fname']
            lname = request.form['lname']
            gender = request.form['gender']
            username = request.form['username']

            # Fetch the current user instance
            current_user = User.query.get(g.user['id'])

            # Update the user details
            current_user.username = username
            current_user.firstname = fname
            current_user.lastname = lname
            current_user.gender = gender

            # Commit the changes to the database
            db.session.commit()

            # Redirect to account page
            return redirect(url_for('accounts'))
        except Exception as e:
            print(f"Error updating user details: {e}")
            db.session.rollback()

    # Render the createaccount page
>>>>>>> 9b64c7a (work flow)
    return render_template('createaccount.html')

@app.route('/accounts')
def accounts():
    if g.user is None:
        return redirect(url_for('login'))
    return render_template('accounts.html')

@app.route('/cardpayment')
def cardpayment():
    if g.user is None:
        return redirect(url_for('login'))
    return render_template('cardpayment.html')

@app.route('/feedbacks')
def feedbacks():
    if g.user is None:
        return redirect(url_for('login'))
    return render_template('feedbacks.html')

@app.route('/history')
def history():
    if g.user is None:
        return redirect(url_for('login'))
    return render_template('history.html')

    
@app.errorhandler(400)
def handle_bad_request(e):
    return 'Bad Request: {0}'.format(e.description), 400

if __name__ == '__main__':
    app.run()
