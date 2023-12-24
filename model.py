import sqlite3, random
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Integer, Column, ForeignKey, String
from datetime import datetime
# Initializing an instance of the SQLAlchemy class
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    username = db.Column(db.String(50), unique=True)    
    gender = db.Column(db.String(50))
    privacy_enabled = db.Column(db.Boolean, default=False)
    notification_enabled = db.Column(db.Boolean, default=False)
    profile_image = db.Column(db.String(255), nullable=True)
    account_type = db.Column(db.String(10))
    account = db.Column(db.Integer, unique=True, default=lambda: random.randint(10000000000, 99999999999))
    password = db.Column(db.String(64))

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255))
    amount = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    account_number = db.Column(db.Integer, db.ForeignKey('user.account'), nullable=False)
    amount = db.Column(db.Float)
    status = db.Column(db.String(20))  # e.g., 'approved', 'pending', 'rejected'

class Receipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    amount = db.Column(db.Float)
    description = db.Column(db.String(255))
    destination_country = db.Column(db.String(50))
    currency = db.Column(db.String(10))
