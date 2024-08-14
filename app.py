from flask import Flask, redirect, request, session, url_for, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from modooles import maily
import base64


app = Flask(__name__)

app.config['SECRET_KEY'] = 'q0uUfrw3IRER5E1F8jP6'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.jinja_env.filters['b64encode'] = base64.b64encode
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(20), nullable=False)
    genre = db.Column(db.String(20), nullable=False)
    uploadedby = db.Column(db.String(20), nullable=False)
    bookimg = db.Column(db.LargeBinary, nullable=False)


@app.template_filter('b64_codec')
def b64_codec(s):
    k=str(s)[2:]
    p=k[:-1]
    return p

@app.route('/')
@app.route('/home')
def home():
    return render_template('homepage.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        pwd1 = request.form['password1']
        pwd2 = request.form['password2']

        pwd_hashed = bcrypt.generate_password_hash(pwd1).decode('utf-8')

        if pwd1 != pwd2:
            flash('Passwords do not match. Please try again.','error')
            return render_template('signup.html')

        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or email already exists. Please choose a different one.','error')
            return render_template('signup.html')

        user = User(username=username, email=email, password=pwd_hashed)
        db.session.add(user)
        db.session.commit()

        #maily.send_mailTo(email)
        print(f'ADDED USER: username: {username}, email: {email}')

        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']

        session['username'] = username

        user = User.query.filter_by(username=username).first()
        if user==None:
            flash('No such user exists', 'error')
            return render_template('login.html')
        
        check_pwd = bcrypt.check_password_hash(user.password, pwd)
        if check_pwd==False:
            flash('Username or password does not match', 'error')
            return render_template('login.html')
                
        return redirect(url_for('dashboard', username=username))

    return render_template('login.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/dashboard/<username>')
def dashboard(username):
    usrnm=session.get('username')
    if usrnm:
        return render_template('dashboard.html', username=username)
    else:
        return redirect(url_for('login'))

@app.route('/mybooks', methods=['GET','POST'])
def mybooks():
    username = session.get('username')
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        uploadedby = username
        bookimg = request.files['image']

        book = Book(title=title, author=author, genre=genre, uploadedby=uploadedby, bookimg=bookimg.read())
        db.session.add(book)
        db.session.commit()

        return redirect(url_for('mybooks'))
    else:
        if username:
            user_books = Book.query.filter_by(uploadedby=username).all()
            return render_template('mybooks.html', user_books=user_books)
        else:
            return redirect(url_for('login'))
        
@app.route('/remove_book', methods=['POST'])
def remove_book():
    book_id = request.form['bookid']
    book = Book.query.get(book_id)
    usn = session.get('username')
    if book:
        if book.uploadedby == usn:
            db.session.delete(book)
            db.session.commit()

            return redirect(url_for('mybooks'))
        else:
            flash("That book is not yours!!")
            return redirect(url_for('mybooks'))
    else:
        flash("No such book ID exists")
        return redirect(url_for('mybooks'))

@app.route('/hub')
def hub():
    all_books = Book.query.all()
    return render_template('hub.html', all_books=all_books)

@app.route('/add_trade', methods=['POST'])
def add_trade():
    username = session.get('username')
    if username:
        book_id = request.form['bookid']
        
        book = db.session.get(Book, book_id)
        if book.tradeinfo:
            if ", "+username+"," not in book.tradeinfo and username+"," not in book.tradeinfo and username not in book.tradeinfo:
                book.tradeinfo += ", " + username
                b_owner_name = book.uploadedby
                b_owner = User.query.filter_by(username=b_owner_name).first()
                #maily.notify_trade(b_owner.email, b_owner_name, username, book.title)
            else:
                flash("You have already added the book for trade!!")
                return redirect(url_for('hub'))
        else:
            if book.uploadedby != username:
                book.tradeinfo = username
            else:
                flash("You can't put add trade on your book!")
        
        db.session.commit()

        return redirect(url_for('hub'))

    else:
        return redirect(url_for('login'))
        


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)