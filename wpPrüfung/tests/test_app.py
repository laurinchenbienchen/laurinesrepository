import unittest
from app import app, db, Book #aus app die anwendung die db und das modell

class TestApp(unittest.TestCase): #definiert eine testklasse TestApp, die von unittest.TestCase ist
    # dadurch wird diese klasse zu einer testeinheit für unittest

    def setUp(self):
        # vor jedem Test ausgeführt
        # Methode konfiguriert die App für den Testmodus und erstellt eine in-memory SQLite-Datenbank
        self.app = app.test_client()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()  # Erstellen der Datenbanktabellen
        # hier wird die Flask-Testclient-Instanz erstellt, um anfragen an die anwendung zu senden
        # anwendung wird für den testmodus konfiguriert und eine SQLite-Datenbank im arbeitsspeicher (:memory:)
        # wird für die tests eingerichtet
        # danach werden alle benötigten datenbanktabellen erstellt


    def tearDown(self):
        # nach jedem Test ausgeführt
        # Methode entfernt alle Sitzungen und löscht die Datenbank damit die tests unabhängig voneinander bleiben
        with app.app_context():
            db.session.remove()
            db.drop_all()  # Löschen der Datenbanktabellen

    def test_index(self):
        # Testen, ob die Index-Seite erfolgreich geladen wird und ob der Text 'To be read - List' auf der Seite
        # enthalten ist.
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)  # Überprüfen, ob der HTTP-Statuscode 200 ist
        self.assertIn(b'To be read - List', response.data)  # Überprüfen, ob der Text 'To be read - List' in
        # der Antwort enthalten ist

    def test_add_book(self):
        # Testen des Hinzufügens eines neuen Buches über die '/add'-Route.
        response = self.app.post('/add', data=dict(
            title='New Book',       #post anfrage an die url gesendet, data=dict enthält die daten des neuen buches
            author='New Author',
            publisher='New Publisher'
        ), follow_redirects=True) #follow_redirects=True testclient folgt  der Anwendung automatisch auf Weiterleitungen
        self.assertEqual(response.status_code, 200)  # Überprüfen, ob der HTTP-Statuscode 200 ist
        self.assertIn(b'New Book', response.data)  # Überprüfen, ob das neue Buch in der Antwort enthalten ist

        # Überprüfen, ob das Buch tatsächlich in der Datenbank gespeichert wurde.
        with app.app_context():
            book = Book.query.filter_by(title='New Book').first()  # Sucht das Buch in der Datenbank
            self.assertIsNotNone(book)  # Überprüfen, ob das Buch gefunden wurde
            self.assertEqual(book.author, 'New Author')  # Überprüfen, ob der Autor korrekt gespeichert wurde
            self.assertEqual(book.publisher, 'New Publisher')  # Überprüfen, ob der Verlag korrekt
            # gespeichert wurde

    def test_delete_book(self):
        # Fügt ein Buch zur Datenbank hinzu, um das Löschen zu testen.
        with app.app_context(): #anwendungskontext um auf die db zuzugreifen
            book = Book(title='Book to Delete', author='Author', publisher='Publisher') #erstellt buch mit eigenschaften
            db.session.add(book) #fügt das buch hinzu
            db.session.commit()  # Speichern des Buches in der Datenbank
            book_id = book.id  # Speichern der Buch-ID für den Löschtest

        # Testen ob das Löschen eines Buches über die '/delete/<id>'-Route funktioniert
        response = self.app.post(f'/delete/{book_id}', follow_redirects=True) #folgen von weiterleitungen
        # post anfrage an die url
        self.assertEqual(response.status_code, 200)  # Überprüfen, ob der HTTP-Statuscode 200 ist

        # Überprüfen, ob das Buch tatsächlich aus der Datenbank gelöscht wurde
        with app.app_context(): #anwendungskontext um auf die datenbank zuzugreifen
            book = Book.query.get(book_id)  # Sucht das Buch in der Datenbank
            self.assertIsNone(book)  # Überprüfen, ob das Buch nicht mehr in der Datenbank vorhanden ist

if __name__ == '__main__':
    unittest.main()  # Führt die Unit-Tests aus
