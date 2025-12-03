# -*- coding: utf-8 -*-
"""
Created on Tue Nov  4 17:48:58 2025

@author: ajohn
"""

# ==================== DATA STORAGE ====================

users = {}
books = []
checked_out_books = {}
current_user = None

# ==================== FILE OPERATIONS ====================

def save_users():
    try:
        file = open("users.txt", "w")
        for username, password in users.items():
            file.write(username + "|" + password + "\n")
        file.close()
        return True
    except:
        return False

def load_users():
    global users
    try:
        file = open("users.txt", "r")
        users = {}
        for line in file:
            line = line.strip()
            if line:
                parts = line.split("|")
                if len(parts) == 2:
                    users[parts[0]] = parts[1]
        file.close()
        return True
    except:
        return False

def save_books():
    try:
        file = open("books.txt", "w")
        for book in books:
            line = str(book["id"]) + "|" + book["title"] + "|" + book["author"] + "|"
            line += str(book["available"]) + "|" + str(book["checked_out_by"]) + "|"
            line += str(book["due_date"]) + "\n"
            file.write(line)
        file.close()
        return True
    except:
        return False

def load_books():
    global books
    try:
        file = open("books.txt", "r")
        books = []
        for line in file:
            line = line.strip()
            if line:
                parts = line.split("|")
                if len(parts) == 6:
                    book = {
                        "id": int(parts[0]),
                        "title": parts[1],
                        "author": parts[2],
                        "available": parts[3] == "True",
                        "checked_out_by": None if parts[4] == "None" else parts[4],
                        "due_date": None if parts[5] == "None" else parts[5]
                    }
                    books.append(book)
        file.close()
        return True
    except:
        return False

def save_checkouts():
    try:
        file = open("checkouts.txt", "w")
        for username, book_ids in checked_out_books.items():
            line = username + "|" + ",".join([str(bid) for bid in book_ids]) + "\n"
            file.write(line)
        file.close()
        return True
    except:
        return False

def load_checkouts():
    global checked_out_books
    try:
        file = open("checkouts.txt", "r")
        checked_out_books = {}
        for line in file:
            line = line.strip()
            if line:
                parts = line.split("|")
                if len(parts) == 2:
                    username = parts[0]
                    book_ids = [int(bid) for bid in parts[1].split(",") if bid]
                    checked_out_books[username] = book_ids
        file.close()
        return True
    except:
        return False

# ==================== USER AUTHENTICATION ====================

def register_user(username, password):
    if not username or not password:
        return False, "Username and password cannot be empty"
    if username in users:
        return False, "Username already exists"
    users[username] = password
    checked_out_books[username] = []
    save_users()
    save_checkouts()
    return True, "User registered successfully"

def login_user(username, password):
    global current_user
    if username not in users:
        return False, "Username not found"
    if users[username] != password:
        return False, "Incorrect password"
    current_user = username
    return True, "Login successful"

def logout_user():
    global current_user
    current_user = None
    return True, "Logged out successfully"

def get_current_user():
    return current_user

# ==================== BOOK MANAGEMENT ====================

def add_book(title, author):
    book_id = len(books) + 1
    book = {
        "id": book_id,
        "title": title,
        "author": author,
        "available": True,
        "checked_out_by": None,
        "due_date": None
    }
    books.append(book)
    save_books()
    return True, "Book added successfully", book_id

def get_all_books():
    return books

def get_available_books():
    available = []
    for book in books:
        if book["available"]:
            available.append(book)
    return available

def get_book_by_id(book_id):
    for book in books:
        if book["id"] == book_id:
            return book
    return None

def calculate_due_date():
    return "2025-11-12"

def checkout_book(book_id, username):
    if not username:
        return False, "No user logged in"
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found"
    if not book["available"]:
        return False, "Book is already checked out"
    book["available"] = False
    book["checked_out_by"] = username
    book["due_date"] = calculate_due_date()
    if username not in checked_out_books:
        checked_out_books[username] = []
    checked_out_books[username].append(book_id)
    save_books()
    save_checkouts()
    return True, "Book checked out successfully"

def return_book(book_id, username):
    if not username:
        return False, "No user logged in"
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found"
    if book["available"]:
        return False, "Book is not checked out"
    if book["checked_out_by"] != username:
        return False, "This book was not checked out by you"
    book["available"] = True
    book["checked_out_by"] = None
    book["due_date"] = None
    if username in checked_out_books and book_id in checked_out_books[username]:
        checked_out_books[username].remove(book_id)
    save_books()
    save_checkouts()
    return True, "Book returned successfully"

def get_user_books(username):
    user_books = []
    if username in checked_out_books:
        for book_id in checked_out_books[username]:
            book = get_book_by_id(book_id)
            if book:
                user_books.append(book)
    return user_books

# ==================== INITIALIZATION ====================

def initialize_system():
    load_users()
    load_books()
    load_checkouts()
    if len(books) == 0:
        add_book("Harry Potter and the Philosopher's Stone", "J.K. Rowling")
        add_book("1984", "George Orwell")
        add_book("To Kill a Mockingbird", "Harper Lee")
        add_book("The Great Gatsby", "F. Scott Fitzgerald")
        add_book("Pride and Prejudice", "Jane Austen")
        add_book("The Catcher in the Rye", "J.D. Salinger")
        add_book("The Hobbit", "J.R.R. Tolkien")
        add_book("Fahrenheit 451", "Ray Bradbury")

# ==================== HTML GENERATION ====================

def generate_html_page():
    html = '''<!DOCTYPE html>
<html>
<head>
    <title>Library Management System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .header h1 { color: #667eea; margin-bottom: 10px; }
        .login-section, .main-section { background: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #333; }
        input { width: 100%; padding: 10px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px; }
        button { background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin-right: 10px; }
        button:hover { background: #5568d3; }
        .book-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
        .book-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; }
        .book-card h3 { color: #333; margin-bottom: 10px; }
        .book-card p { color: #666; margin-bottom: 8px; }
        .available { color: #28a745; font-weight: bold; }
        .unavailable { color: #dc3545; font-weight: bold; }
        .due-date { color: #ffc107; font-weight: bold; }
        .hidden { display: none; }
        .user-info { background: #e8f4f8; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .success { color: #28a745; font-weight: bold; margin: 10px 0; }
        .error { color: #dc3545; font-weight: bold; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> LKR Library Management System</h1>
            <p>Login or create an account to access our library.
        </div>

        <!-- LOGIN SECTION -->
        <div id="loginSection" class="login-section">
            <h2>Login or Register</h2>
            <div class="form-group">
                <label>Username:</label>
                <input type="text" id="username" placeholder="Enter username">
            </div>
            <div class="form-group">
                <label>Password:</label>
                <input type="password" id="password" placeholder="Enter password">
            </div>
            <button onclick="login()">Login</button>
            <button onclick="register()">Register</button>
            <div id="loginMessage"></div>
        </div>

        <!-- MAIN SECTION (Hidden until login) -->
        <div id="mainSection" class="main-section hidden">
            <div class="user-info">
                <strong>Logged in as: <span id="currentUser"></span></strong>
                <button onclick="logout()" style="float: right;">Logout</button>
            </div>

            <h2>Available Books</h2>
            <div id="availableBooks" class="book-grid"></div>

            <h2 style="margin-top: 40px;">My Checked Out Books</h2>
            <div id="myBooks" class="book-grid"></div>

            <div id="actionMessage"></div>
        </div>
    </div>

    <script>
        let currentUsername = "";

        function login() {
            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;
            
            if (!username || !password) {
                showMessage("loginMessage", "Please enter username and password", false);
                return;
            }

            // This would call your Python function
            // For demo, we'll simulate it
            console.log("Login:", username, password);
            showMessage("loginMessage", "Login successful! (In production, this calls Python)", true);
            
            // Show main section
            currentUsername = username;
            document.getElementById("currentUser").textContent = username;
            document.getElementById("loginSection").classList.add("hidden");
            document.getElementById("mainSection").classList.remove("hidden");
            
            loadBooks();
        }

        function register() {
            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;
            
            if (!username || !password) {
                showMessage("loginMessage", "Please enter username and password", false);
                return;
            }

            console.log("Register:", username, password);
            showMessage("loginMessage", "Registration successful! Now please login.", true);
        }

        function logout() {
            currentUsername = "";
            document.getElementById("loginSection").classList.remove("hidden");
            document.getElementById("mainSection").classList.add("hidden");
            document.getElementById("username").value = "";
            document.getElementById("password").value = "";
        }

        function loadBooks() {
            // Sample books for demo
            const availableBooks = [
                {id: 1, title: "Harry Potter", author: "J.K. Rowling", available: true},
                {id: 2, title: "1984", author: "George Orwell", available: true},
                {id: 3, title: "The Great Gatsby", author: "F. Scott Fitzgerald", available: true}
            ];

            let html = "";
            availableBooks.forEach(book => {
                html += `
                    <div class="book-card">
                        <h3>${book.title}</h3>
                        <p><strong>Author:</strong> ${book.author}</p>
                        <p class="available">âœ“ Available</p>
                        <button onclick="checkoutBook(${book.id})">Checkout</button>
                    </div>
                `;
            });
            document.getElementById("availableBooks").innerHTML = html;

            // Load user's books
            document.getElementById("myBooks").innerHTML = "<p>No books checked out yet</p>";
        }

        function checkoutBook(bookId) {
            console.log("Checkout book:", bookId);
            showMessage("actionMessage", `Book ${bookId} checked out! Due: 2025-11-12`, true);
            setTimeout(() => loadBooks(), 1000);
        }

        function returnBook(bookId) {
            console.log("Return book:", bookId);
            showMessage("actionMessage", `Book ${bookId} returned successfully!`, true);
            setTimeout(() => loadBooks(), 1000);
        }

        function showMessage(elementId, message, isSuccess) {
            const element = document.getElementById(elementId);
            element.textContent = message;
            element.className = isSuccess ? "success" : "error";
            setTimeout(() => element.textContent = "", 3000);
        }
    </script>
</body>
</html>'''
    
    try:
        file = open("library.html", "w")
        file.write(html)
        file.close()
        return True
    except:
        return False

# ==================== COMMAND LINE INTERFACE ====================

def print_menu():
    print("\n" + "="*50)
    print("LIBRARY MANAGEMENT SYSTEM")
    print("="*50)
    if current_user:
        print("Logged in as:", current_user)
    else:
        print("Not logged in")
    print("\n1. Register")
    print("2. Login")
    print("3. Logout")
    print("4. View all books")
    print("5. View available books")
    print("6. Checkout book")
    print("7. Return book")
    print("8. View my books")
    print("9. Generate HTML website")
    print("10. Show example usage")
    print("11. Exit")
    print("="*50)

def show_examples():
    """Show example usage of all functions"""
    print("\n" + "="*70)
    print("EXAMPLE USAGE DEMONSTRATION")
    print("="*70)
    
    print("\n“ EXAMPLE 1: Registering a new user")
    print("   Code: register_user('rafi', 'mypassword123')")
    success, msg = register_user('rafi_demo', 'pass123')
    print("   Result:", msg)
    
    print("\n EXAMPLE 2: Logging in")
    print("   Code: login_user('rafi_demo', 'pass123')")
    success, msg = login_user('rafi_demo', 'pass123')
    print("   Result:", msg)
    print("   Current user:", get_current_user())
    
    print("\n“ EXAMPLE 3: Getting all books")
    print("   Code: get_all_books()")
    all_books = get_all_books()
    print("   Found", len(all_books), "books:")
    for book in all_books[:3]:  # Show first 3
        print("     - ID:", book["id"], "| Title:", book["title"], "| Available:", book["available"])
    
    print("\n“– EXAMPLE 4: Getting available books only")
    print("   Code: get_available_books()")
    available = get_available_books()
    print("   Found", len(available), "available books")
    
    print("\n EXAMPLE 5: Checking out a book")
    print("   Code: checkout_book(1, 'rafi_demo')")
    success, msg = checkout_book(1, 'rafi_demo')
    print("   Result:", msg)
    
    print("\n EXAMPLE 6: Getting user's checked out books")
    print("   Code: get_user_books('rafi_demo')")
    user_books = get_user_books('rafi_demo')
    print("   Rafi has", len(user_books), "book(s) checked out:")
    for book in user_books:
        print("     - Title:", book["title"], "| Due:", book["due_date"])
    
    print("\n EXAMPLE 7: Returning a book")
    print("   Code: return_book(1, 'rafi_demo')")
    success, msg = return_book(1, 'rafi_demo')
    print("   Result:", msg)
    
    print("\n EXAMPLE 8: Logging out")
    print("   Code: logout_user()")
    success, msg = logout_user()
    print("   Result:", msg)
    
    print("\n" + "="*70)
    print("EXAMPLES COMPLETE! All functions demonstrated.")
    print("="*70)

def main():
    initialize_system()
    
    while True:
        print_menu()
        choice = input("\nEnter your choice (1-11): ").strip()
        
        if choice == "1":
            print("\n--- REGISTER NEW USER ---")
            print("Example: username='alice', password='secure123'")
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            success, message = register_user(username, password)
            print("\n" + message)
        
        elif choice == "2":
            print("\n--- LOGIN ---")
            print("Example: username='alice', password='secure123'")
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            success, message = login_user(username, password)
            print("\n" + message)
        
        elif choice == "3":
            success, message = logout_user()
            print("\n" + message)
        
        elif choice == "4":
            all_books = get_all_books()
            print("\nAll Books:")
            print("-"*80)
            for book in all_books:
                status = "Available" if book["available"] else "Checked out"
                print("ID:", book["id"], "| Title:", book["title"], "| Author:", book["author"], "| Status:", status)
                if not book["available"]:
                    print("  Checked out by:", book["checked_out_by"], "| Due:", book["due_date"])
        
        elif choice == "5":
            available = get_available_books()
            print("\nAvailable Books:")
            print("-"*80)
            for book in available:
                print("ID:", book["id"], "| Title:", book["title"], "| Author:", book["author"])
        
        elif choice == "6":
            if not current_user:
                print("\nPlease login first!")
                continue
            print("\n--- CHECKOUT BOOK ---")
            print("Example: Enter '1' for first book, '2' for second book, etc.")
            book_id = input("Enter book ID to checkout: ").strip()
            try:
                book_id = int(book_id)
                success, message = checkout_book(book_id, current_user)
                print("\n" + message)
            except:
                print("\nInvalid book ID!")
        
        elif choice == "7":
            if not current_user:
                print("\nPlease login first!")
                continue
            print("\n--- RETURN BOOK ---")
            print("Example: Enter '1' to return book ID 1")
            book_id = input("Enter book ID to return: ").strip()
            try:
                book_id = int(book_id)
                success, message = return_book(book_id, current_user)
                print("\n" + message)
            except:
                print("\nInvalid book ID!")
        
        elif choice == "8":
            if not current_user:
                print("\nPlease login first!")
                continue
            user_books = get_user_books(current_user)
            print("\nYour Checked Out Books:")
            print("-"*80)
            if len(user_books) == 0:
                print("No books checked out")
            else:
                for book in user_books:
                    print("ID:", book["id"], "| Title:", book["title"], "| Due:", book["due_date"])
        
        elif choice == "9":
            print("\n--- GENERATE HTML WEBSITE ---")
            if generate_html_page():
                print("\n“ HTML website generated: library.html")
                print("  Open this file in your web browser!")
            else:
                print("\n— Failed to generate HTML")
        
        elif choice == "10":
            show_examples()
        
        elif choice == "11":
            print("\nThank you for using the Library Management System!")
            break
        
        else:
            print("\nInvalid choice! Please try again.")

# ==================== RUN PROGRAM ====================

if __name__ == "__main__":
    main()