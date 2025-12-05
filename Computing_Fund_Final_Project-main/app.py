from flask import Flask, render_template, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from collections import Counter

# Setting up the Flask app
app = Flask(__name__)
app.secret_key = 'library-secret-key-student-2024'

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)


# --- Database Models ---

class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String(80), primary_key=True)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')
    email = db.Column(db.String(120))
    
    checkouts = db.relationship('Checkout', backref='user', lazy=True)
    fines = db.relationship('Fine', backref='user', lazy=True)


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(20))
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    times_borrowed = db.Column(db.Integer, default=0)
    
    checkouts = db.relationship('Checkout', backref='book', lazy=True)


class Checkout(db.Model):
    __tablename__ = 'checkouts'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    username = db.Column(db.String(80), db.ForeignKey('users.username'), nullable=False)
    checkout_date = db.Column(db.String(10), nullable=False)
    due_date = db.Column(db.String(10), nullable=False)
    returned = db.Column(db.Boolean, default=False)


class Fine(db.Model):
    __tablename__ = 'fines'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), db.ForeignKey('users.username'), nullable=False)
    checkout_id = db.Column(db.Integer)
    fine = db.Column(db.Float, nullable=False)
    date = db.Column(db.String(10), nullable=False)


class PendingRequest(db.Model):
    __tablename__ = 'pending_requests'
    id = db.Column(db.Integer, primary_key=True)
    request_type = db.Column(db.String(20), nullable=False)  # 'checkout' or 'return'
    username = db.Column(db.String(80), db.ForeignKey('users.username'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    request_date = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'denied'
    
    user = db.relationship('User', backref='requests', lazy=True)
    book = db.relationship('Book', backref='requests', lazy=True)


class Settings(db.Model):
    __tablename__ = 'settings'
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(200))


# --- Initialization Functions ---

def initialize_system():
    """Create tables on startup"""
    with app.app_context():
        db.create_all()
        print("Database tables ready!")
        
        # Optional: Check if database is empty and needs default data
        if User.query.count() == 0:
            # Add default users
            admin = User(username='admin', password='admin123', 
                        role='librarian', email='admin@library.com')
            john = User(username='john_doe', password='password123', 
                       role='user', email='john@email.com')
            
            db.session.add(admin)
            db.session.add(john)
            
            # Add default books
            books = [
                Book(id=1, title="Harry Potter", author="J.K. Rowling", 
                     isbn="9780439708180", total_copies=3, available_copies=3),
                Book(id=2, title="1984", author="George Orwell", 
                     isbn="9780451524935", total_copies=2, available_copies=2),
                Book(id=3, title="To Kill a Mockingbird", author="Harper Lee", 
                     isbn="9780060935467", total_copies=2, available_copies=2),
            ]
            
            for book in books:
                db.session.add(book)
            
            # Add default settings
            setting = Settings(key='days_to_borrow', value='30')
            db.session.add(setting)
            
            db.session.commit()
            print("Database initialized with default data!")


def calculate_due_date():
    """Calculate the due date based on settings (default 30 days = 1 month)"""
    setting = Settings.query.filter_by(key='days_to_borrow').first()
    days = int(setting.value) if setting else 30
    return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")


def calculate_fine(due_date_string):
    """Calculate fine for overdue books"""
    due_date = datetime.strptime(due_date_string, "%Y-%m-%d")
    today = datetime.now()
    
    if today > due_date:
        days_late = (today - due_date).days
        fine = round(days_late * 0.50, 2)
        return fine
    return 0.0


# --- Start the system ---
if __name__ == '__main__':
    initialize_system()
    app.run(debug=False, use_reloader=False)
