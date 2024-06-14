import requests
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
db = SQLAlchemy(app)
# Dummy data
books = [
    {'id': 1, 'title': 'Life of Puppets', 'author': 'T. J. Klune', 'publisher': 'Tor Books'},
    {'id': 2, 'title': 'Harry Potter and the Philosopher\'s Stone', 'author': 'J. K. Rowling',
     'publisher': 'Bloomsbury'},
    {'id': 3, 'title': 'Good Omens', 'author': 'Terry Pratchett', 'publisher': 'Gollancz'}
]


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    publisher = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return '<Book %r>' % self.title


GOOGLE_BOOKS_API_KEY = 'AIzaSyCtbLZ2mMlyTfQG07Aiy4AAOQjFQ3iju40'


def fetch_book_info(title, author, publisher):
    try:
        query = f"{title} {author} {publisher}"
        response = requests.get(f'https://www.googleapis.com/books/v1/volumes?q={query}&key={GOOGLE_BOOKS_API_KEY}')
        response.raise_for_status()
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            book_info = data['items'][0]['volumeInfo']
            image = book_info['imageLinks']['thumbnail'] if 'imageLinks' in book_info else None
            return image
    except requests.exceptions.RequestException as e:
        print(f"Error fetching book info: {e}")
    except KeyError as e:
        print(f"Key error: {e}")
    return None


# Routes
@app.route('/')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)



@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        publisher = request.form['publisher']
        image = fetch_book_info(title, author, publisher)
        new_book = Book(title=title, author=author, publisher=publisher, image=image)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html')


@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
