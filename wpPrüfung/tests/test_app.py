import unittest
from app import app


class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Book List', response.data)

    def test_add_book(self):
        response = self.app.post('/add', data=dict(title='New Book', author='New Author'))
        self.assertEqual(response.status_code, 302)  # Redirects to index
        response = self.app.get('/')
        self.assertIn(b'New Book', response.data)

    def test_delete_book(self):
        response = self.app.post('/delete/1')
        self.assertEqual(response.status_code, 302)  # Redirects to index
        response = self.app.get('/')
        self.assertNotIn(b'Book 1', response.data)


if __name__ == '__main__':
    unittest.main()
