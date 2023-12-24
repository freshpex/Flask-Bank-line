# import sqlite3
# from flask_sqlalchemy import SQLAlchemy
# # from sqlalchemy import Boolean, Integer, Column, ForeignKey, String


# # Initializing an instance of the SQLAlchemy class
# db = SQLAlchemy()

# conn = sqlite3.connect('database.db')
# c = conn.cursor()

# c.execute('''CREATE TABLE users
#              (id INTEGER PRIMARY KEY AUTOINCREMENT,
#               email TEXT UNIQUE,
#               first_name TEXT,
#               last_name TEXT,
#               username TEXT UNIQUE,
#               gender TEXT,
#               account INTEGER,
#               notification_enabled INTEGER,
#               privacy_enabled INTEGER,
#               password_hash TEXT,
#               profile_image TEXT )''')

# conn.commit()
# conn.close()


# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50))
#     email = db.Column(db.String(50), unique=True)