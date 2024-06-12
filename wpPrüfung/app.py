# flask anwendung erstellen
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dummy data
books = [
    {'id': 1, 'title': 'Book 1', 'author': 'Author 1'},
    {'id': 2, 'title': 'Book 2', 'author': 'Author 2'},
    {'id': 3, 'title': 'Book 3', 'author': 'Author 3'}
]

# Routes
@app.route('/')
def index():
    return render_template('index.html', books=books)

@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        book_id = len(books) + 1
        books.append({'id': book_id, 'title': title, 'author': author})
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    global books
    books = [book for book in books if book['id'] != book_id]
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
