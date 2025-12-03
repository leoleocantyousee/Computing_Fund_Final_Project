from flask import Flask, render_template, jsonify, request, session
import json
from datetime import datetime, timedelta
import os
from collections import Counter

# Setting up the Flask app
app = Flask(__name__)
# We need this secret key for session management (to keep track of who is logged in)
app.secret_key = 'library-secret-key-student-2024' 

# We will save our data here
DATA_FILE = 'library_data_simple.json' 

# This is our main storage dictionary for all library data
library = {"users": {}, "books": [], "checkouts": [], "fines": {}}


# --- Data Management Functions ---

def save_data():
    # Let's save the current state of our library to a file
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(library, f, indent=2)
        return True
    except:
        return False


def load_data():
    # We load the data when the server starts up
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                library.update(data)
            return True
    except:
        # If loading fails, we just ignore it and start fresh
        pass
    return False


def initialize_system():
    # If the data file is empty, we set up default users and books
    if not load_data() or not library.get('users'):
        # IMPORTANT: We are storing passwords as plain strings for simplicity 
        library['users'] = {
            'admin': {'password': 'admin123', 'role': 'librarian', 'email': 'admin@library.com'},
            'john_doe': {'password': 'password123', 'role': 'user', 'email': 'john@email.com'}
        }

        # We'll set a very short borrowing period (1 day) to easily test the fine calculation
        library['settings'] = {'days_to_borrow': 1} 

        library['books'] = [
            {"id": 1, "title": "Harry Potter", "author": "J.K. Rowling", "isbn": "9780439708180", "total_copies": 3, "available_copies": 3, "times_borrowed": 0},
            {"id": 2, "title": "1984", "author": "George Orwell", "isbn": "9780451524935", "total_copies": 2, "available_copies": 2, "times_borrowed": 0},
            {"id": 3, "title": "To Kill a Mockingbird", "author": "Harper Lee", "isbn": "9780060935467", "total_copies": 2, "available_copies": 2, "times_borrowed": 0},
        ]

        library['checkouts'] = []
        library['fines'] = {}
        save_data()


def calculate_due_date():
    # This figures out the due date based on our settings (which is 1 day)
    days = library['settings']['days_to_borrow']
    return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")


def calculate_fine(due_date_string):
    # This is how we check if a book is late and calculate the fine
    due_date = datetime.strptime(due_date_string, "%Y-%m-%d")
    today = datetime.now()
    
    if today > due_date:
        time_difference = today - due_date
        # We only charge for full days late
        days_late = time_difference.days
        # Fine is $0.50 per day
        fine = round(days_late * 0.50, 2)
        return fine
    return 0.0


# --- Flask Routes ---

@app.route('/')
def home():
    # We now serve the HTML from a file called website.html using render_template
    # Flask will look for this file in a 'templates' folder or the root folder.
    return render_template('website.html')


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json or {}
    u = data.get('username')
    p = data.get('password')
    if not u or not p:
        return jsonify({'success': False, 'message': 'Missing fields'}), 400

    user = library['users'].get(u)
    # Simple check: Does the username exist AND does the plain password match?
    if user and user.get('password') == p:
        session['username'] = u
        return jsonify({'success': True, 'role': user.get('role', 'user')})

    return jsonify({'success': False, 'message': 'Invalid credentials'})


@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json or {}
    u = data.get('username')
    p = data.get('password')
    e = data.get('email', '')
    if not u or not p:
        return jsonify({'success': False, 'message': 'Missing fields'})
    if u in library['users']:
        return jsonify({'success': False, 'message': 'Username exists'})

    # We store the new user with their plain password and default role 'user'
    library['users'][u] = {'password': p, 'role': 'user', 'email': e} 
    library['fines'][u] = [] 
    save_data()
    return jsonify({'success': True})


@app.route('/api/books')
def api_books():
    # Simply returns the list of books for the frontend to display
    return jsonify(library.get('books', []))


@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    data = request.json or {}
    book_id = data.get('book_id')
    username = session.get('username')

    if not username:
        return jsonify({'success': False, 'message': 'Not logged in'})

    # Find the book in our list
    book = next((b for b in library['books'] if b['id'] == book_id), None)
    if not book or book['available_copies'] <= 0:
        return jsonify({'success': False, 'message': 'Unavailable'})

    # Check if the user is already borrowing 5 books
    active = [c for c in library['checkouts'] if c['username'] == username and not c.get('returned')]
    if len(active) >= 5:
        return jsonify({'success': False, 'message': 'Limit reached (5 books)'})

    # Create the new checkout record
    checkout = {
        'id': len(library['checkouts']) + 1,
        'book_id': book_id,
        'username': username,
        'checkout_date': datetime.now().strftime("%Y-%m-%d"),
        'due_date': calculate_due_date(), 
        'returned': False
    }

    library['checkouts'].append(checkout)
    # Decrease the available count for the book
    book['available_copies'] -= 1
    book['times_borrowed'] += 1
    save_data()

    return jsonify({'success': True, 'due_date': checkout['due_date']})


@app.route('/api/return', methods=['POST'])
def api_return():
    data = request.json or {}
    book_id = data.get('book_id')
    username = session.get('username')

    # Find the specific active checkout record
    checkout = next((c for c in library['checkouts'] if c['book_id'] == book_id and c['username'] == username and not c.get('returned')), None)
    if not checkout:
        return jsonify({'success': False, 'message': 'No active checkout found'})

    fine = calculate_fine(checkout['due_date'])
    
    # Mark it as returned
    checkout['returned'] = True

    # Increase the available copies again
    book = next((b for b in library['books'] if b['id'] == book_id), None)
    if book:
        book['available_copies'] += 1

    # Record the fine if there is one
    if fine > 0:
        if username not in library['fines']:
            library['fines'][username] = []
        library['fines'][username].append({'checkout_id': checkout['id'], 'fine': fine, 'date': datetime.now().strftime("%Y-%m-%d")})

    save_data()
    return jsonify({'success': True, 'fine': fine})


@app.route('/api/my_checkouts')
def api_my_checkouts():
    username = session.get('username')
    if not username:
        return jsonify([])

    # Filter for the user's active (not returned) checkouts
    checkouts = [c for c in library['checkouts'] if c['username'] == username and not c['returned']]
    for c in checkouts:
        # Attach the book title/author to the checkout record
        b = next((bb for bb in library['books'] if bb['id'] == c['book_id']), None)
        c['book'] = b if b else {'title': 'Unknown'} 
        
        # Simple check: is today >= the due date?
        due_date = datetime.strptime(c['due_date'], "%Y-%m-%d")
        c['is_overdue'] = datetime.now().date() >= due_date.date()

    return jsonify(checkouts)


@app.route('/api/add_book', methods=['POST'])
def api_add_book():
    username = session.get('username')
    user = library['users'].get(username)

    # Only librarians can add books
    if not user or user.get('role') != 'librarian':
        return jsonify({'success': False, 'message': 'Librarian access only'})

    data = request.json or {}
    
    # We find the next available ID for the new book
    new_id = max([b['id'] for b in library['books']], default=0) + 1 

    new_book = {
        'id': new_id,
        'title': data.get('title', 'Unknown Title'),
        'author': data.get('author', 'Unknown Author'),
        'isbn': data.get('isbn', 'N/A'),
        'total_copies': int(data.get('copies', 1)),
        # Available copies start at the total count
        'available_copies': int(data.get('copies', 1)),
        'times_borrowed': 0
    }

    library['books'].append(new_book)
    save_data()

    return jsonify({'success': True})


@app.route('/api/stats')
def api_stats():
    username = session.get('username')
    user = library['users'].get(username)

    # Only librarians can see these stats
    if not user or user.get('role') != 'librarian':
        return jsonify({}) 

    active = [c for c in library['checkouts'] if not c['returned']]
    
    overdue_count = 0
    for c in active:
        due_date = datetime.strptime(c['due_date'], "%Y-%m-%d")
        if datetime.now().date() > due_date.date():
             overdue_count += 1

    return jsonify({
        'total_books': len(library['books']),
        'active_checkouts': len(active),
        'overdue': overdue_count,
        'total_users': len(library['users'])
    })


@app.route('/api/analytics')
def api_analytics():
    username = session.get('username')
    user = library['users'].get(username)

    # Only librarians can run analytics
    if not user or user.get('role') != 'librarian':
        return jsonify({})

    # 1. Finding the top 5 most borrowed books
    borrow_counts = Counter(c['book_id'] for c in library['checkouts'])
    most_borrowed_ids = borrow_counts.most_common(5) 
    most_borrowed = []
    
    for book_id, count in most_borrowed_ids:
        book = next((b for b in library['books'] if b['id'] == book_id), None)
        if book:
            most_borrowed.append({
                'title': book['title'],
                'author': book['author'],
                'times': count
            })

    # 2. Counting how many unique users currently have books
    active_users = list(set(c['username'] for c in library['checkouts'] if not c['returned']))

    # 3. Summing up all the fines ever recorded
    total_fines = sum(fine_data['fine'] for user_fines in library['fines'].values() for fine_data in user_fines)

    return jsonify({
        'most_borrowed': most_borrowed,
        'active_user_count': len(active_users),
        'total_fines': round(total_fines, 2)
    })


# Start the system when the script runs
if __name__ == '__main__':
    initialize_system()
    # TEMPORARY FIX: Set debug=False and use_reloader=False to stop Spyder crashes
    app.run(debug=False, use_reloader=False)