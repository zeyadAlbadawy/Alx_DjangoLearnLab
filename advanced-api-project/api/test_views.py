import json
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework import status
from .models import Book, Author

class BookViewsTestCase(TestCase):
    def setUp(self):
        # Create a user for authentication
        self.user = User.objects.create_user(username='testuser', password='password123')

        # Create an author
        self.author = Author.objects.create(name='Author 1')

        # Create a book
        self.book = Book.objects.create(
            title='Book 1',
            publication_year=2023,
            author=self.author
        )

    def test_book_list_view(self):
        # Unauthenticated request
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Parse JSON without using response.data
        data = json.loads(response.content)
        self.assertTrue(len(data) >= 1)

    def test_book_create_view_authenticated(self):
        self.client.login(username='testuser', password='password123')
        payload = {
            'title': 'New Book',
            'publication_year': 2025,
            'author': self.author.id
        }
        response = self.client.post('/api/books/create/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_book_detail_view(self):
        response = self.client.get(f'/api/books/{self.book.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(data['title'], self.book.title)

    def test_book_update_view_authenticated(self):
        self.client.login(username='testuser', password='password123')
        payload = {
            'title': 'Updated Book',
            'publication_year': 2024,
            'author': self.author.id
        }
        response = self.client.put(
            f'/api/books/{self.book.id}/update/',
            json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_book = Book.objects.get(id=self.book.id)
        self.assertEqual(updated_book.title, 'Updated Book')

    def test_book_delete_view_authenticated(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.delete(f'/api/books/{self.book.id}/delete/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=self.book.id).exists())
