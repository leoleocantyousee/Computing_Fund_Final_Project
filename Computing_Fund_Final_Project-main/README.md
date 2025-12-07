# LKR Library Management System

## Project Goal

A web-based library management system that simulates real-world library operations. Users can browse books and submit checkout/return requests, while librarians manage the catalog, approve requests, and track analytics including fines for overdue books.

## How to Run

**⚠️ PREREQUISITE: You must have Python 3.7+ installed first!**
- Download from: https://python.org/downloads/
- **IMPORTANT**: During installation, check the box "Add Python to PATH" ✅
- After installing, restart your terminal/command prompt

1. **Verify Python is Installed**
   - Open Terminal/Command Prompt:
     - **Windows**: Press `Win + R`, type `cmd`, press Enter (or search "Command Prompt")
     - **Mac**: Press `Cmd + Space`, type `terminal`, press Enter
     - **Linux**: Press `Ctrl + Alt + T`
   - Test Python: `python --version` or `python3 --version`
   - You should see something like "Python 3.x.x"
   - If you get "'python' is not recognized" error, Python isn't installed or not in PATH

2. **Download/Clone the Project**
   ```bash
   # If using Git
   git clone <repository-url>
   cd Computing_Fund_Final_Project-main
   
   # Or download and extract the ZIP file, then navigate to the folder using:
   cd path/to/Computing_Fund_Final_Project-main
   ```

3. **Install Dependencies** (in the same terminal)
   ```bash
   pip install Flask Flask-SQLAlchemy
   ```
   - **If you get "'pip' is not recognized" error**, try: `py -m pip install Flask Flask-SQLAlchemy`
   - If you encounter permission errors, try: `pip install --user Flask Flask-SQLAlchemy`
   - Verify installation worked: `pip list` (should show Flask and Flask-SQLAlchemy)

4. **Run the Application**
   ```bash
   python app.py
   ```
   - You should see: "Database tables ready!" and "Database initialized with default data!"
   - The server will start at `http://127.0.0.1:5000/`
   - Keep this terminal window open while using the application

5. **Access in Browser**
   - Open: `http://127.0.0.1:5000/`
   - You'll see the login/registration page

6. **Login with Default Accounts**
   - **Librarian**: `admin` / `admin123` (full access to manage requests and view analytics)
   - **User**: `john_doe` / `password123` (can browse and request books)
   - **Guest**: Click "Browse as Guest" (can only view catalog)

7. **Using the Application**
   - **As a User**: Browse books → Request Checkout → View "My Checkouts" → Request Return when done
   - **As a Librarian**: View "Pending Requests" → Approve/Deny requests → Check "System Stats" and "Analytics Dashboard" → Add new books
   - **Register New Account**: Click "Register" → Enter username, password (8+ chars, 1+ uppercase), and email

## Requirements

- Python 3.7+
- Flask 2.3.0
- Flask-SQLAlchemy 3.0.0
- Web browser

## Approach/Methodology

**Architecture:** Three-tier system with HTML/CSS/JS frontend, Flask backend, and SQLite database using SQLAlchemy ORM.

**Key Features:**
- Request-approval workflow: Users submit checkout/return requests; librarians approve/deny them
- Role-based access: Different interfaces for users, librarians, and guests
- Automatic fine calculation: $0.50 per day for overdue books
- 5-book checkout limit per user
- Real-time analytics dashboard for librarians

**Design Decisions:**
- Session-based authentication for simplicity
- Client-side rendering with JavaScript for dynamic updates
- Separate pending requests table to track approval workflow
- Password validation (8+ characters, 1+ uppercase letter)

## Results/Demo

**User Interface:**
- Users can browse available books, request checkouts, view active loans with due dates, and submit return requests
- Color-coded interface: green book cards, yellow pending requests, red overdue warnings

**Librarian Dashboard:**
- System statistics: total books, active checkouts, overdue count, pending requests
- Analytics: most borrowed books, total fines, complete borrowed/overdue book tables
- Request management: approve or deny checkout/return requests
- Add new books to catalog

**Sample Workflow:**
1. User requests checkout → librarian approves → book added to user's active checkouts
2. User requests return → librarian approves → fine calculated if overdue → book returned to catalog

**Testing Fines:**
- To test the fine system, change your computer's date to 30+ days in the future
- Books will show as overdue (marked in red)
- When librarian approves a return, the system calculates fines at $0.50/day
- Example: Book due on Dec 1st, returned on Dec 10th = 9 days × $0.50 = $4.50 fine

**Default Data:** System includes 3 sample books (Harry Potter, 1984, To Kill a Mockingbird) and 2 user accounts for testing.

