from flask import Flask, render_template, request, g, session, url_for, redirect, flash, send_from_directory
import sqlite3, hashlib, os, requests
from werkzeug.utils import secure_filename
from model import db, User, Transaction, Receipt, Loan, Account

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
DATABASE_FILE = 'instance/database.db'

db.init_app(app)

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
    query = "SELECT id, email, firstname, lastname, username, gender, password, notification_enabled, privacy_enabled, profile_image, account_type FROM user WHERE id = ?"
    args = (user_id,)
    row = db_query(query, args)

    if not row:
        return None

    return {
        'id': row[0][0], 'email': row[0][1], 'firstname': row[0][2], 'lastname': row[0][3], 'username': row[0][4], 'gender': row[0][5], 'password': row[0][10], 'notification_enabled': bool(row[0][7]), 'privacy_enabled': bool(row[0][6]), 'account_type': row[0][9]
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
    query = "SELECT id FROM user WHERE email = ? OR username = ?"
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
        query = "INSERT INTO user (email, username, password) VALUES (?, ?, ?)"
        args = (email, username, password_hash)

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
        query = "SELECT id, password FROM user WHERE username = ?"
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
    # Fetch the current user's accounts
    user_accounts = Account.query.filter_by(user_id=g.user['id']).all()
    return render_template('dashboard.html', user_accounts=user_accounts)

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

@app.route('/createaccount', methods=['GET', 'POST'])
def createaccount():
    if g.user is None:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        gender = request.form['gender']
        username = request.form['username']
        account_type = request.form['account_type']

        # Fetch the current user instance
        current_user = User.query.get(g.user['id'])

        # Update the user details
        current_user.username = username
        current_user.firstname = fname
        current_user.lastname = lname
        current_user.gender = gender
        current_user.account_type = account_type

        # Check if an account already exists for the user
        existing_account = Account.query.filter_by(user_id=g.user['id']).first()
        if existing_account:
            # If an account exists, update it
            existing_account.account_type = account_type
        else:
            # If no account exists, create a new one
            new_account = Account(user_id=g.user['id'], account_type=account_type)
            db.session.add(new_account)

        # Commit the changes to the database
        db.session.commit()

        # Redirect to account page
        return redirect(url_for('accounts'))

    # Render the createaccount page
    return render_template('createaccount.html')



@app.route('/accounts')
def accounts():
    if g.user is None:
        return redirect(url_for('login'))
    
    # Fetch the current user's accounts
    user_accounts = Account.query.filter_by(user_id=g.user['id']).all()
    return render_template('accounts.html', user_accounts=user_accounts)  # Pass user_accounts to the template


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

    user_transactions = Transaction.query.filter_by(user_id=g.user['id']).all()
    return render_template('history.html', user_transactions=user_transactions)

# Route for viewing receipt
@app.route('/view_receipt/<int:transaction_id>')
def view_receipt(transaction_id):
    if g.user is None:
        return redirect(url_for('login'))

    # Fetch the specific transaction
    transaction = Transaction.query.get(transaction_id)
    return render_template('view_receipt.html', transaction=transaction)

def process_transaction_logic(source_account, amount, description, transaction_type, destination_country=None, currency=None):
    # Assuming you have a User model and a Transaction model in your application
    user = User.query.filter_by(account_number=source_account).first()

    if not user:
        return render_template('error.html', error_message='Invalid source account.')

    # Assuming your User model has a balance field
    if user.balance < amount:
        return render_template('error.html', error_message='Insufficient funds.')

    # Update the user's balance
    user.balance -= amount

    # Create a new transaction record
    new_transaction = Transaction(
        description=description,
        amount=-amount,  # Deduct amount for debiting the account
        user_id=user.id
    )

    db.session.add(new_transaction)
    db.session.commit()

    # Additional logic for international transfer
    if transaction_type == 'international':
        # Handle additional international transfer logic
        # This might include exchange rate calculations, fees, etc.
        # For simplicity, let's assume a fixed fee for international transfers
        international_fee = 10.0  # Replace with your actual fee
        amount -= international_fee

    # Update the user's balance after deducting the international fee
    user.balance -= international_fee if transaction_type == 'international' else 0

    # Assuming you have a Receipt model
    new_receipt = Receipt(
        transaction_id=new_transaction.id,
        amount=amount,
        description=description,
        destination_country=destination_country,
        currency=currency
    )

    db.session.add(new_receipt)
    db.session.commit()

    # Redirect to the transaction history page or generate receipt
    return render_template('confirmation.html', confirmation_message=f"Transaction successfully processed. Receipt ID: {new_receipt.id}")


# Route for processing transactions
@app.route('/process_transaction', methods=['POST'])
def process_transaction():
    if g.user is None:
        return redirect(url_for('login'))

    transaction_type = request.form.get('transaction_type')
    source_account = request.form.get('source_account')
    amount = float(request.form.get('amount'))
    description = request.form.get('description')

    destination_country = None
    currency = None

    if transaction_type == 'international':
        destination_country = request.form.get('destination_country')
        currency = request.form.get('currency')

        # Add logic for international transfer fields handling
        # Example: You may want to check exchange rates, apply fees, etc.
        # For simplicity, let's assume a fixed fee for international transfers
        international_fee = 10.0  # Replace with your actual fee

        # Deduct the international fee from the transfer amount
        amount -= international_fee

    # Check if the user has multiple accounts
    user_accounts = User.query.filter_by(id=g.user['id']).all()

    if len(user_accounts) > 1:
        # If the user has multiple accounts, ask which account to use
        return render_template('process_transaction.html', user_accounts=user_accounts, amount=amount, description=description, transaction_type=transaction_type, source_account=source_account, destination_country=destination_country, currency=currency)
    
    # If the user has only one account, proceed to process the transaction
    return process_transaction_logic(source_account, amount, description, transaction_type, destination_country, currency)

@app.route('/loan_history/<int:account_number>')
def loan_history(account_number):
    if g.user is None:
        return redirect(url_for('login'))

    # Placeholder logic: Fetch loan history based on the account number
    loan_history = Loan.query.filter_by(account_number=account_number).all()

    return render_template('loan_history.html', account_number=account_number, loan_history=loan_history)
    
@app.errorhandler(400)
def handle_bad_request(e):
    return 'Bad Request: {0}'.format(e.description), 400

if __name__ == '__main__':
    app.run()
