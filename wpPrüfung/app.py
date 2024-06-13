# flask anwendung erstellen
import requests
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dummy data
books = [
    {'id': 1, 'title': 'Life of Puppets', 'author': 'T. J. Klune'},
    {'id': 2, 'title': 'Harry Potter and the Philosopher\'s stone', 'author': 'J. K. Rowling'},
    {'id': 3, 'title': 'Good Omens', 'author': 'Terry Pratchett'}
]

GOOGLE_BOOKS_API_KEY = 'AIzaSyCtbLZ2mMlyTfQG07Aiy4AAOQjFQ3iju40'


def fetch_book_info(title, author):
    try:
        query = f"{title} {author}"
        response = requests.get(f'https://www.googleapis.com/books/v1/volumes?q={query}&key={GOOGLE_BOOKS_API_KEY}')
        response.raise_for_status()
        data = response.json()
        print(f'api response: {data}')
        if 'items' in data and len(data['items']) > 0:
            book_info = data['items'][0]['volumeInfo']
            image = book_info['imageLinks'][0]['thumbnail'] if 'imageLinks' in book_info else None
            print(f'book image: {image}')
            return image
    except requests.exceptions.RequestException as e:
        print(f'error fetching book info: {e}')
    except KeyError as e:
        print(f'key error: {e}')
    return None


# Routes
@app.route('/')
def index():
    for book in books:
        if 'image' not in book:
            book['image'] = fetch_book_info(book['title'], book['author'])
    return render_template('index.html', books=books)


@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if requests.method == 'POST':
        title = requests.form['title']
        author = requests.form['author']
        book_id = len(books) + 1
        image = fetch_book_info(title, author)
        books.append({'id': book_id, 'title': title, 'author': author, 'image': image})
        return redirect(url_for('index'))
    return render_template('add.html')


@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    global books
    books = [book for book in books if book['id'] != book_id]
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
