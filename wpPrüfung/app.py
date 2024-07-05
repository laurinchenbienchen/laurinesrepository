import requests
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
#konfihuriert die Datenbank-URI für SQLite und deaktiviert die SQLAlchemy Änderungsverfolgung
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# initialisierung sqalchemy mit der flask-awendung
db = SQLAlchemy(app)


#definiert ein modell für die buch-datenbank
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)  # titel (pflicht)
    author = db.Column(db.String(100), nullable=False)  # autor (pflicht)
    publisher = db.Column(db.String(100), nullable=False)  #verlag (pflicht)
    image = db.Column(db.String(200), nullable=True)  # bild-url (optional)


#erstellen datenbanktabelle
with app.app_context():
    db.create_all()
#google books api-schlüssel
GOOGLE_BOOKS_API_KEY = 'AIzaSyCtbLZ2mMlyTfQG07Aiy4AAOQjFQ3iju40'


#funktion zum abrufen von buchinfromationen von der google books api
def fetch_book_info(title, author, publisher):
    try:
        query = f"{title} {author} {publisher}"  #erstellen suchanfrage
        response = requests.get(f'https://www.googleapis.com/books/v1/volumes?q={query}&key={GOOGLE_BOOKS_API_KEY}')
        response.raise_for_status()  #prüfung auf http-fehler
        data = response.json()  #antwort als json dekodieren
        if 'items' in data and len(data['items']) > 0:
            book_info = data['items'][0]['volumeInfo']
            print(f"Book info found: {book_info}")  # Debugging-Ausgabe
            image = book_info['imageLinks']['thumbnail'] if 'imageLinks' in book_info else None  #bild url extrahieren
            return image
    except requests.exceptions.RequestException as e:
        print(f"Error fetching book info: {e}")  #fehlerprotokoll (Anfragefehler)
    except KeyError as e:
        print(f"Key error: {e}")  #fehlerprotokoll (Schlüsselzugriffsfeher)
    return None


#route startseite
@app.route('/')
def index():
    search_query = request.args.get('q', '')  # abrufen suchbefgriff aus der url
    page = request.args.get('page', 1, type=int)  # abrufen aktuelle seite, standard ist 1
    per_page = 5  #anzahl der bücher pro seite
    books_query = Book.query  # grundlegende datenbankabfrage

    if search_query:  #filtern der bücher nach title oder author
        books_query = books_query.filter(
            (Book.title.ilike(f"%{search_query}%")) |
            (Book.author.ilike(f"%{search_query}%"))
        )

    total = books_query.count()  #anzahl gefundener bücher
    books = books_query.offset((page - 1) * per_page).limit(per_page).all()  #paginierung

    for book in books:
        if not book.image:
            print(f"Fetching image for book: {book.title}")  # Debugging-Ausgabe
            book.image = fetch_book_info(book.title, book.author, book.publisher)  # bild abrufen
            db.session.commit()  #änderungen speichern

    return render_template('index.html', books=books, page=page, per_page=per_page, total=total,
                           search_query=search_query)


#route hinzufügen buch
@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        publisher = request.form['publisher']
        print(f"Adding book: {title} by {author}")  # Debugging-Ausgabe
        image = fetch_book_info(title, author, publisher)  #bild abrufen
        new_book = Book(title=title, author=author, publisher=publisher, image=image)  #neues buch erstellen
        db.session.add(new_book)  #buch zur sitzung hinzufügen
        db.session.commit()  #änderungen speichern
        return redirect(url_for('index'))  #weiterleiten startseite
    return render_template('add.html')


# route bearbeiten buch
@app.route('/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Book.query.get(book_id)  #buch anhand id abrufen
    if not book:
        return redirect(url_for('index'))  #falls buch nicht gefungen -> startseite

    if request.method == 'POST':  #daten abrufen und buchdetails aktualisieren
        book.title = request.form['title']
        book.author = request.form['author']
        book.publisher = request.form['publisher']
        book.image = fetch_book_info(book.title, book.author, book.publisher)  #bil aktualisieren
        db.session.commit()  #änderungen speichern
        return redirect(url_for('index'))

    return render_template('edit.html', book=book)


#route löschen buch
@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get(book_id)  #buch anhand id abrufen
    if book:
        print(f"Deleting book: {book.title}")  # Debugging-Ausgabe
        db.session.delete(book)  #buch aus sitzung entfernen
        db.session.commit()  # änderungen speichern
    else:
        print(f"Book with ID {book_id} not found.")  # Debugging-Ausgabe
    return redirect(url_for('index'))


#starten flask-anwendung
if __name__ == '__main__':
    app.run(debug=True)
