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

# --- Database Models (Unchanged) ---
# ... (User, Book, Checkout, Fine, PendingRequest, Settings classes remain the same) ...

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


# --- Initialization Functions (Unchanged) ---

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


# --- Flask Routes ---

@app.route('/')
def home():
    # Assuming 'website.html' is correctly rendered, though HTML part is not included here
    return render_template('website.html')


@app.route('/api/login', methods=['POST'])
def api_login():
    # Logic remains unchanged
    data = request.json or {}
    u = data.get('username')
    p = data.get('password')
    
    if not u or not p:
        return jsonify({'success': False, 'message': 'Missing fields'}), 400

    user = User.query.filter_by(username=u).first()
    
    if user and user.password == p:
        session['username'] = u
        return jsonify({'success': True, 'role': user.role})

    return jsonify({'success': False, 'message': 'Invalid credentials'})


@app.route('/api/register', methods=['POST'])
def api_register():
    """Register a new user with validation checks."""
    data = request.json or {}
    u = data.get('username')
    p = data.get('password')
    e = data.get('email', '')
    
    if not u or not p:
        return jsonify({'success': False, 'message': 'Missing username or password'})
    
    if User.query.filter_by(username=u).first():
        return jsonify({'success': False, 'message': 'Username exists'})

    # 1. Password Complexity Check: Min 8 chars and must contain a capital letter
    if len(p) < 8:
        return jsonify({'success': False, 'message': 'Password must be at least 8 characters long.'})
    if not any(c.isupper() for c in p):
        return jsonify({'success': False, 'message': 'Password must include at least one capital letter.'})

    # 2. Email Format Check (simple)
    if e and '@' not in e:
        return jsonify({'success': False, 'message': 'Invalid email format.'})

    new_user = User(username=u, password=p, role='user', email=e)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'success': True})


@app.route('/api/books')
def api_books():
    # Logic remains unchanged
    books = Book.query.all()
    return jsonify([{
        'id': b.id,
        'title': b.title,
        'author': b.author,
        'isbn': b.isbn,
        'total_copies': b.total_copies,
        'available_copies': b.available_copies,
        'times_borrowed': b.times_borrowed
    } for b in books])


@app.route('/api/request_checkout', methods=['POST'])
def api_request_checkout():
    """User requests to checkout a book - includes 5 book limit check."""
    data = request.json or {}
    book_id = data.get('book_id')
    username = session.get('username')

    if not username:
        return jsonify({'success': False, 'message': 'Not logged in'})

    book = Book.query.get(book_id)
    if not book or book.available_copies <= 0:
        return jsonify({'success': False, 'message': 'Book unavailable'})

    # 3. Checkout Limit Check: Users limited to 5 active books
    MAX_CHECKOUTS = 5
    active_count = Checkout.query.filter_by(username=username, returned=False).count()
    if active_count >= MAX_CHECKOUTS:
        return jsonify({'success': False, 'message': f'You have reached the limit ({MAX_CHECKOUTS} books)'})

    # Check if there's already a pending request for this book by this user
    existing = PendingRequest.query.filter_by(
        username=username, 
        book_id=book_id, 
        request_type='checkout',
        status='pending'
    ).first()
    
    if existing:
        return jsonify({'success': False, 'message': 'You already have a pending request for this book'})

    # Create pending request
    pending = PendingRequest(
        request_type='checkout',
        username=username,
        book_id=book_id,
        request_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        status='pending'
    )
    
    db.session.add(pending)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Checkout request submitted! Waiting for librarian approval.'})


@app.route('/api/request_return', methods=['POST'])
def api_request_return():
    # Logic remains unchanged
    data = request.json or {}
    book_id = data.get('book_id')
    username = session.get('username')

    if not username:
        return jsonify({'success': False, 'message': 'Not logged in'})

    # Check if user has this book checked out
    checkout = Checkout.query.filter_by(
        book_id=book_id, username=username, returned=False
    ).first()
    
    if not checkout:
        return jsonify({'success': False, 'message': 'You do not have this book checked out'})

    # Check if there's already a pending return request
    existing = PendingRequest.query.filter_by(
        username=username, 
        book_id=book_id, 
        request_type='return',
        status='pending'
    ).first()
    
    if existing:
        return jsonify({'success': False, 'message': 'You already have a pending return request for this book'})

    # Create pending request
    pending = PendingRequest(
        request_type='return',
        username=username,
        book_id=book_id,
        request_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        status='pending'
    )
    
    db.session.add(pending)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Return request submitted! Waiting for librarian confirmation.'})


@app.route('/api/pending_requests')
def api_pending_requests():
    # Logic remains unchanged
    username = session.get('username')
    user = User.query.filter_by(username=username).first()

    if not user or user.role != 'librarian':
        return jsonify([])

    requests = PendingRequest.query.filter_by(status='pending').all()
    
    result = []
    for req in requests:
        result.append({
            'id': req.id,
            'request_type': req.request_type,
            'username': req.username,
            'book_id': req.book_id,
            'book_title': req.book.title,
            'book_author': req.book.author,
            'request_date': req.request_date,
            'status': req.status
        })
    
    return jsonify(result)


@app.route('/api/approve_checkout', methods=['POST'])
def api_approve_checkout():
    # Logic remains unchanged
    data = request.json or {}
    request_id = data.get('request_id')
    username = session.get('username')
    user = User.query.filter_by(username=username).first()

    if not user or user.role != 'librarian':
        return jsonify({'success': False, 'message': 'Librarian access only'})

    pending = PendingRequest.query.get(request_id)
    if not pending or pending.status != 'pending':
        return jsonify({'success': False, 'message': 'Request not found or already processed'})

    book = Book.query.get(pending.book_id)
    if not book or book.available_copies <= 0:
        pending.status = 'denied'
        db.session.commit()
        return jsonify({'success': False, 'message': 'Book no longer available'})

    # Create the actual checkout
    checkout = Checkout(
        book_id=pending.book_id,
        username=pending.username,
        checkout_date=datetime.now().strftime("%Y-%m-%d"),
        due_date=calculate_due_date(),
        returned=False
    )
    
    db.session.add(checkout)
    book.available_copies -= 1
    book.times_borrowed += 1
    pending.status = 'approved'
    
    db.session.commit()

    return jsonify({'success': True, 'due_date': checkout.due_date})


@app.route('/api/approve_return', methods=['POST'])
def api_approve_return():
    # Logic remains unchanged
    data = request.json or {}
    request_id = data.get('request_id')
    username = session.get('username')
    user = User.query.filter_by(username=username).first()

    if not user or user.role != 'librarian':
        return jsonify({'success': False, 'message': 'Librarian access only'})

    pending = PendingRequest.query.get(request_id)
    if not pending or pending.status != 'pending':
        return jsonify({'success': False, 'message': 'Request not found or already processed'})

    # Find the checkout record
    checkout = Checkout.query.filter_by(
        book_id=pending.book_id, 
        username=pending.username, 
        returned=False
    ).first()
    
    if not checkout:
        pending.status = 'denied'
        db.session.commit()
        return jsonify({'success': False, 'message': 'No active checkout found'})

    fine = calculate_fine(checkout.due_date)
    
    checkout.returned = True
    
    book = Book.query.get(pending.book_id)
    if book:
        book.available_copies += 1

    if fine > 0:
        fine_record = Fine(
            username=pending.username,
            checkout_id=checkout.id,
            fine=fine,
            date=datetime.now().strftime("%Y-%m-%d")
        )
        db.session.add(fine_record)

    pending.status = 'approved'
    db.session.commit()
    
    return jsonify({'success': True, 'fine': fine})


@app.route('/api/deny_request', methods=['POST'])
def api_deny_request():
    # Logic remains unchanged
    data = request.json or {}
    request_id = data.get('request_id')
    username = session.get('username')
    user = User.query.filter_by(username=username).first()

    if not user or user.role != 'librarian':
        return jsonify({'success': False, 'message': 'Librarian access only'})

    pending = PendingRequest.query.get(request_id)
    if not pending or pending.status != 'pending':
        return jsonify({'success': False, 'message': 'Request not found or already processed'})

    pending.status = 'denied'
    db.session.commit()
    
    return jsonify({'success': True})


@app.route('/api/my_checkouts')
def api_my_checkouts():
    # Logic remains unchanged
    username = session.get('username')
    if not username:
        return jsonify([])

    checkouts = Checkout.query.filter_by(
        username=username, returned=False
    ).all()
    
    result = []
    for c in checkouts:
        due_date = datetime.strptime(c.due_date, "%Y-%m-%d")
        result.append({
            'id': c.id,
            'book_id': c.book_id,
            'username': c.username,
            'checkout_date': c.checkout_date,
            'due_date': c.due_date,
            'returned': c.returned,
            'book': {
                'id': c.book.id,
                'title': c.book.title,
                'author': c.book.author
            },
            'is_overdue': datetime.now().date() >= due_date.date()
        })
    
    return jsonify(result)


@app.route('/api/my_requests')
def api_my_requests():
    # Logic remains unchanged
    username = session.get('username')
    if not username:
        return jsonify([])

    requests = PendingRequest.query.filter_by(username=username, status='pending').all()
    
    result = []
    for req in requests:
        result.append({
            'id': req.id,
            'request_type': req.request_type,
            'book_title': req.book.title,
            'book_author': req.book.author,
            'request_date': req.request_date
        })
    
    return jsonify(result)


@app.route('/api/add_book', methods=['POST'])
def api_add_book():
    # Logic remains unchanged
    username = session.get('username')
    user = User.query.filter_by(username=username).first()

    if not user or user.role != 'librarian':
        return jsonify({'success': False, 'message': 'Librarian access only'})

    data = request.json or {}
    
    new_book = Book(
        title=data.get('title', 'Unknown Title'),
        author=data.get('author', 'Unknown Author'),
        isbn=data.get('isbn', 'N/A'),
        total_copies=int(data.get('copies', 1)),
        available_copies=int(data.get('copies', 1)),
        times_borrowed=0
    )

    db.session.add(new_book)
    db.session.commit()

    return jsonify({'success': True})


@app.route('/api/stats')
def api_stats():
    # Logic remains unchanged
    username = session.get('username')
    user = User.query.filter_by(username=username).first()

    if not user or user.role != 'librarian':
        return jsonify({})

    active_checkouts = Checkout.query.filter_by(returned=False).all()
    
    overdue_count = 0
    for c in active_checkouts:
        due_date = datetime.strptime(c.due_date, "%Y-%m-%d")
        if datetime.now().date() > due_date.date():
            overdue_count += 1

    pending_count = PendingRequest.query.filter_by(status='pending').count()

    return jsonify({
        'total_books': Book.query.count(),
        'active_checkouts': len(active_checkouts),
        'overdue': overdue_count,
        'total_users': User.query.count(),
        'pending_requests': pending_count
    })


@app.route('/api/analytics')
def api_analytics():
    # Logic remains unchanged
    username = session.get('username')
    user = User.query.filter_by(username=username).first()

    if not user or user.role != 'librarian':
        return jsonify({})

    all_checkouts = Checkout.query.all()
    borrow_counts = Counter(c.book_id for c in all_checkouts)
    most_borrowed_ids = borrow_counts.most_common(5)
    
    most_borrowed = []
    for book_id, count in most_borrowed_ids:
        book = Book.query.get(book_id)
        if book:
            most_borrowed.append({
                'title': book.title,
                'author': book.author,
                'times': count
            })

    active_checkouts = Checkout.query.filter_by(returned=False).all()
    active_users = list(set(c.username for c in active_checkouts))

    all_fines = Fine.query.all()
    total_fines = sum(f.fine for f in all_fines)

    # Get all currently borrowed books
    borrowed_books = []
    for checkout in active_checkouts:
        borrowed_books.append({
            'username': checkout.username,
            'book_title': checkout.book.title,
            'book_author': checkout.book.author,
            'checkout_date': checkout.checkout_date,
            'due_date': checkout.due_date
        })

    # Get all overdue books
    overdue_books = []
    today = datetime.now().date()
    for checkout in active_checkouts:
        due_date = datetime.strptime(checkout.due_date, "%Y-%m-%d").date()
        if today > due_date:
            days_overdue = (today - due_date).days
            overdue_books.append({
                'username': checkout.username,
                'book_title': checkout.book.title,
                'book_author': checkout.book.author,
                'due_date': checkout.due_date,
                'days_overdue': days_overdue,
                'fine': round(days_overdue * 0.50, 2)
            })

    return jsonify({
        'most_borrowed': most_borrowed,
        'active_user_count': len(active_users),
        'total_fines': round(total_fines, 2),
        'borrowed_books': borrowed_books,
        'overdue_books': overdue_books
    })


# Start the system
if __name__ == '__main__':
    initialize_system()
    app.run(debug=False, use_reloader=False)
