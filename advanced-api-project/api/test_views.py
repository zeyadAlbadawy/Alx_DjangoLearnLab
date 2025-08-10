"""
Unit Tests for Advanced API Project - Book API Endpoints
"""

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Book, Author


class BookAPITestCase(APITestCase):
    """Common setup for all Book API tests"""

    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        self.regular_user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )

        # Explicitly test self.client.login requirement here
        logged_in = self.client.login(username='testuser', password='testpass123')
        self.assertTrue(logged_in, "Login failed in setUp()")

        # Auth tokens
        self.admin_token = Token.objects.create(user=self.admin_user)
        self.user_token = Token.objects.create(user=self.regular_user)

        # Authors
        self.author1 = Author.objects.create(name="George Orwell")
        self.author2 = Author.objects.create(name="Jane Austen")
        self.author3 = Author.objects.create(name="J.K. Rowling")

        # Books
        self.book1 = Book.objects.create(
            title="1984", publication_year=1949, author=self.author1
        )
        self.book2 = Book.objects.create(
            title="Pride and Prejudice", publication_year=1813, author=self.author2
        )
        self.book3 = Book.objects.create(
            title="Animal Farm", publication_year=1945, author=self.author1
        )

    def authenticate_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')

    def authenticate_as_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')

    def unauthenticate(self):
        self.client.credentials()


class BookListViewTests(BookAPITestCase):
    """GET /books/ tests"""

    def test_get_all_books_unauthenticated(self):
        url = reverse('book-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('results', res.data)
        self.assertEqual(len(res.data['results']), 3)

    def test_filter_by_title(self):
        url = reverse('book-list')
        res = self.client.get(url, {'title': '1984'})
        self.assertEqual(len(res.data['results']), 1)
        self.assertEqual(res.data['results'][0]['title'], '1984')

    def test_filter_by_author(self):
        url = reverse('book-list')
        res = self.client.get(url, {'author': self.author1.id})
        self.assertEqual(len(res.data['results']), 2)

    def test_search_by_title(self):
        url = reverse('book-list')
        res = self.client.get(url, {'search': 'Animal'})
        self.assertEqual(len(res.data['results']), 1)
        self.assertEqual(res.data['results'][0]['title'], 'Animal Farm')

    def test_order_by_year_desc(self):
        url = reverse('book-list')
        res = self.client.get(url, {'ordering': '-publication_year'})
        years = [b['publication_year'] for b in res.data['results']]
        self.assertEqual(years, [1949, 1945, 1813])


class BookDetailViewTests(BookAPITestCase):
    """GET /books/<id>/ tests"""

    def test_get_existing_book(self):
        url = reverse('book-detail', kwargs={'id': self.book1.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('title', res.data)
        self.assertEqual(res.data['title'], '1984')

    def test_get_nonexistent_book(self):
        url = reverse('book-detail', kwargs={'id': 999})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class BookCreateViewTests(BookAPITestCase):
    """POST /books/create/ tests"""

    def test_create_book_authenticated_user(self):
        self.authenticate_as_user()
        url = reverse('book-create')
        data = {'title': 'The Great Gatsby', 'publication_year': 1925, 'author': self.author2.id}
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('title', res.data)

    def test_create_book_unauthenticated(self):
        self.unauthenticate()
        url = reverse('book-create')
        data = {'title': 'Unauthorized', 'publication_year': 2023, 'author': self.author1.id}
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class BookUpdateViewTests(BookAPITestCase):
    """PATCH /books/<id>/update/ tests"""

    def test_update_book_authenticated_user(self):
        self.authenticate_as_user()
        url = reverse('book-update', kwargs={'id': self.book1.id})
        res = self.client.patch(url, {'title': '1984 - Updated'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], '1984 - Updated')

    def test_update_nonexistent_book(self):
        self.authenticate_as_user()
        url = reverse('book-update', kwargs={'id': 999})
        res = self.client.patch(url, {'title': 'Does Not Exist'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class BookDeleteViewTests(BookAPITestCase):
    """DELETE /books/<id>/delete/ tests"""

    def test_delete_book_admin_user(self):
        self.authenticate_as_admin()
        url = reverse('book-delete', kwargs={'id': self.book1.id})
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_book_regular_user_forbidden(self):
        self.authenticate_as_user()
        url = reverse('book-delete', kwargs={'id': self.book1.id})
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class BookAPIIntegrationTests(BookAPITestCase):
    """Full CRUD workflow"""

    def test_complete_lifecycle(self):
        # Create
        self.authenticate_as_user()
        create_url = reverse('book-create')
        data = {'title': 'Lifecycle Book', 'publication_year': 2023, 'author': self.author1.id}
        res = self.client.post(create_url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', res.data)
        book_id = res.data['id']

        # Read
        detail_url = reverse('book-detail', kwargs={'id': book_id})
        res = self.client.get(detail_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('title', res.data)

        # Update
        update_url = reverse('book-update', kwargs={'id': book_id})
        res = self.client.patch(update_url, {'title': 'Updated'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Delete as admin
        self.authenticate_as_admin()
        delete_url = reverse('book-delete', kwargs={'id': book_id})
        res = self.client.delete(delete_url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
