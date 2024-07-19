import requests
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# erstellt flask-anwendung mit dem namen app (application)
app = Flask(__name__)
# konfiguriert die Datenbank-URI für SQLite und deaktiviert die SQLAlchemy Änderungsverfolgung
# Datenbank-URI: Datenbank-URI (Uniform Resource Identifier) ist eine spezielle Zeichenkette, die die Informationen
# enthält, die eine Anwendung benötigt, um eine Verbindung zu einer Datenbank herzustellen
# beinhaltet: Datenbanktyp, den Pfad zur Datenbankdatei oder den Server, auf dem die Datenbank läuft
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db' #datenbank im selben verzeichnis wie in der anwendung
# konfiguartionsparameter, legt uri der datenbank fest
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# deaktiviert das feature trackmodifications, sqalchemy überwacht nicht die änderungen an objekten und signalen
# initialisierung sqalchemy mit der flask-awendung
db = SQLAlchemy(app)

#definiert ein modell für die buch-datenbank
# id: name der spalte in der datenbank
# db.Column: neue spalte wird in der datenbank definiert
# db.string(100): datentyp und max länge der zeichenkette
# db.integer: spezifiziert den datentyp der spalte
# primary key: dient zur eindeutigen identifikation jeder zeile
# nullable die spalte darf nicht null sein oder kann frei gelassen werden
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)  # titel (pflicht, nullable)
    author = db.Column(db.String(100), nullable=False)  # autor (pflicht)
    publisher = db.Column(db.String(100), nullable=False)  #verlag (pflicht)
    image = db.Column(db.String(200), nullable=True)  # bild-url (optional)


#erstellen datenbanktabelle
with app.app_context():
    db.create_all()

#google books api-schlüssel
GOOGLE_BOOKS_API_KEY = 'AIzaSyCtbLZ2mMlyTfQG07Aiy4AAOQjFQ3iju40'

#funktion zum abrufen von buchinfromationen von der google books api
def fetch_book_info(title, author, publisher):  #nimmt parameter aus der claa entgegen
    try:    #ausnahmenbehandlung
        query = f"{title} {author} {publisher}"  #erstellen suchanfrage durch kombi aus autor, titel und verlag
        response = requests.get(f'https://www.googleapis.com/books/v1/volumes?q={query}&key={GOOGLE_BOOKS_API_KEY}')
        # sendet http get anfrage an die google api mit der erstellten suchanfrage und dem key
        response.raise_for_status()  #prüfung auf http-fehler
        data = response.json()  #antwort als json dekodieren
        if 'items' in data and len(data['items']) > 0: #prüft ob die antwort der api in 'items'schlüssel ist und nicht leer
            book_info = data['items'][0]['volumeInfo'] #extrahiert den schlüssel und speichert ihn als book_info
            print(f"Book info found: {book_info}")  # Debugging-Ausgabe
            image = book_info['imageLinks']['thumbnail'] if 'imageLinks' in book_info else None  #bild url extrahieren
            #Überprüft, ob in den Buchinformationen ein Bildlink vorhanden ist, und extrahiert die URL des Thumbnails
            # des Buchcovers, falls vorhanden. Andernfalls wird None zurückgegeben.
            return image #gibt die bild url zurück
    except requests.exceptions.RequestException as e: # falls fehler in der http-anfrage auftritt
        print(f"Error fetching book info: {e}")  #fehlerprotokoll (Anfragefehler)
    except KeyError as e: #ausnahmen, die auftreten können, wenn ein erwarteter schlüssel im json-antwort-dictionary fehlt
        print(f"Key error: {e}")  #fehlerprotokoll (Schlüsselzugriffsfeher)
    return None #wenn ein fehlerauftritt oder keine  uchinfos gefunden werden konnten


#route startseite
@app.route('/')
def index():
    search_query = request.args.get('q', '')  # abrufen suchbefgriff aus der url, wenn nicht vorhanden leer
    page = request.args.get('page', 1, type=int)  # abrufen aktuelle seite, standard ist 1
    per_page = 5  #anzahl der bücher pro seite
    sort_by = request.args.get('sort_by', 'title')
    books_query = Book.query  # grundlegende datenbankabfrage der buch-tabelle

    if search_query:  #filtern der bücher nach title oder author, ob überhaupt gesucht wird
        books_query = books_query.filter(  #ilike für eineunabhöngige suche
            (Book.title.ilike(f"%{search_query}%")) | #titel oder autor als suchbegriff
            (Book.author.ilike(f"%{search_query}%"))
        )

    if sort_by == 'title':
        books_query = books_query.order_by(Book.title)
    elif sort_by == 'author':
        books_query = books_query.order_by(Book.author)


    total = books_query.count()  #anzahl gefundener bücher
    books = books_query.offset((page - 1) * per_page).limit(per_page).all()  #paginierung der abfrage
    #abfrage überspringt eine gewisse anzahl an büchern(offset) basierend auf der aktuellen seite, anschließend wird die anzahl
    #der bücher pro seite abgerufen

    for book in books: #iteriert über die gefundenen bücher
        if not book.image: #wenn das buch kein bild hat wird fetch_book_info aufgerufen
            print(f"Fetching image for book: {book.title}")  # Debugging-Ausgabe
            book.image = fetch_book_info(book.title, book.author, book.publisher)  # bild abrufen
            db.session.commit()  #änderungen speichern (bild in der datenbank speichern)

    return render_template('index.html', books=books, page=page, per_page=per_page, total=total,
                           search_query=search_query)
    #rendert die index.html-vorlage und übergibt die liste der bücher, die aktuelle seite , die anzahl der
    # bücher pro seite , die gesamtanzahl der gefundenen bücher  und den suchbegriff
    # an die vorlage.


#route hinzufügen buch
@app.route('/add', methods=['GET', 'POST']) #akzeptiert get und post anfragen
def add_book():
    if request.method == 'POST': #überprüft ob es sich um eine post-anfrage handelt es auf der seite abgesendet wurde)
        title = request.form['title']
        author = request.form['author']
        publisher = request.form['publisher']
        # extrahiert die formulardaten, inhalte werden in der jeweiligen variable gespeichert
        print(f"Adding book: {title} by {author}")  # Debugging-Ausgabe des titel und autoren
        image = fetch_book_info(title, author, publisher)  #bild abrufen
        new_book = Book(title=title, author=author, publisher=publisher, image=image)  #neues buch erstellen
        #der klasse buch mit den abgerufenen daten, repräsentiert das buch, das in der db hinzugefügt werden soll
        db.session.add(new_book)  #buch zur sitzung hinzufügen
        db.session.commit()  #änderungen speichern
        return redirect(url_for('index'))  #weiterleiten startseite
    return render_template('add.html') # wenn es keine post anfarge ist, wird das formular angezeigt


# route bearbeiten buch
@app.route('/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Book.query.get(book_id)  #buch anhand id abrufen, sucht mit der gegeben id in der book tabelle
    if not book: #prüft ob es das buch gibt
        return redirect(url_for('index'))  #falls buch nicht gefungen -> startseite

    if request.method == 'POST':  #daten abrufen und buchdetails aktualisieren
        book.title = request.form['title']
        book.author = request.form['author']
        book.publisher = request.form['publisher']
        #aktualisierung aufgrund der formulardaten
        book.image = fetch_book_info(book.title, book.author, book.publisher)  #bild aktualisieren
        db.session.commit()  #änderungen speichern
        return redirect(url_for('index')) #leitet auf die startseite weiter

    return render_template('edit.html', book=book) #bei einer get anfrage wird das edit htm gerendert
    # so dass das bearbeitungsformular angezeit wird,
    # book wird an die vorlage übergeben um die aktuellen details darzustellen


#route löschen buch
@app.route('/delete/<int:book_id>', methods=['POST']) #akzeptiert nur post anfragen
def delete_book(book_id):
    book = Book.query.get(book_id)  #buch anhand id abrufen, sucht in der book tabelle mit der gegebenen book_id
    if book: #prüft ob ein buch vorhanden ist
        print(f"Deleting book: {book.title}")  # Debugging-Ausgabe
        db.session.delete(book)  #buch aus sitzung entfernen
        db.session.commit()  # änderungen speichern
    else:
        print(f"Book with ID {book_id} not found.")  # Debugging-Ausgabe falls das buch nicht existiert
    return redirect(url_for('index'))


#starten flask-anwendung
if __name__ == '__main__':
    app.run(debug=True)
