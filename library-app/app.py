from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, Book, Borrow
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'library-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    return redirect(url_for('books'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return render_template('register.html')
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('register.html')
        user = User(username=username, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash('Invalid username or password.', 'danger')
            return render_template('login.html')
        session['user_id'] = user.id
        session['username'] = user.username
        flash(f'Welcome, {user.username}!', 'success')
        return redirect(url_for('books'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/books')
@login_required
def books():
    query = request.args.get('q', '').strip()
    if query:
        book_list = Book.query.filter(
            (Book.title.ilike(f'%{query}%')) | (Book.author.ilike(f'%{query}%'))
        ).all()
    else:
        book_list = Book.query.all()
    borrowed_ids = {b.book_id for b in Borrow.query.filter_by(user_id=session['user_id'], returned=False).all()}
    return render_template('books.html', books=book_list, query=query, borrowed_ids=borrowed_ids)

@app.route('/books/add', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        isbn = request.form.get('isbn', '').strip()
        if not title or not author:
            flash('Title and author are required.', 'danger')
            return render_template('add_book.html')
        book = Book(title=title, author=author, isbn=isbn)
        db.session.add(book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('books'))
    return render_template('add_book.html')

@app.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        isbn = request.form.get('isbn', '').strip()
        if not title or not author:
            flash('Title and author are required.', 'danger')
            return render_template('edit_book.html', book=book)
        book.title = title
        book.author = author
        book.isbn = isbn
        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('books'))
    return render_template('edit_book.html', book=book)

@app.route('/books/delete/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    Borrow.query.filter_by(book_id=book_id).delete()
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('books'))

@app.route('/books/borrow/<int:book_id>', methods=['POST'])
@login_required
def borrow_book(book_id):
    book = Book.query.get_or_404(book_id)
    existing = Borrow.query.filter_by(book_id=book_id, user_id=session['user_id'], returned=False).first()
    if existing:
        flash('You have already borrowed this book.', 'warning')
        return redirect(url_for('books'))
    borrow = Borrow(book_id=book_id, user_id=session['user_id'])
    book.available = False
    db.session.add(borrow)
    db.session.commit()
    flash(f'You borrowed "{book.title}".', 'success')
    return redirect(url_for('books'))

@app.route('/books/return/<int:book_id>', methods=['POST'])
@login_required
def return_book(book_id):
    borrow = Borrow.query.filter_by(book_id=book_id, user_id=session['user_id'], returned=False).first()
    if not borrow:
        flash('No active borrow found.', 'warning')
        return redirect(url_for('books'))
    borrow.returned = True
    book = Book.query.get(book_id)
    book.available = True
    db.session.commit()
    flash(f'You returned "{book.title}".', 'success')
    return redirect(url_for('books'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
