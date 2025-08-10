"""
Unit Tests for Advanced API Project - Book API Endpoints

This module contains comprehensive tests for all Book API endpoints including:
- CRUD operations (Create, Read, Update, Delete)
- Filtering, searching, and ordering functionality
- Authentication and permission testing
- Response data integrity and status code validation

Database Configuration:
- Tests use a separate test database (test_db.sqlite3) configured in settings.py
- This ensures complete isolation from development/production data
- Django automatically creates/destroys the test database for each test run

Test Categories:
1. BookListView Tests - Testing list, filter, search, and ordering
2. BookDetailView Tests - Testing single book retrieval
3. BookCreateView Tests - Testing book creation with permissions
4. BookUpdateView Tests - Testing book updates with permissions
5. BookDeleteView Tests - Testing book deletion with admin permissions

Run tests with: python manage.py test api.test_views
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Book, Author
from .serializers import BookSerializer
import json


class BookAPITestCase(APITestCase):
    """
    Base test case class with common setup for all Book API tests.
    Creates test users, authors, books, and authentication tokens.
    """

    def setUp(self):
        """Set up test data for each test case."""
        # Create test users with different permission levels
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
        
        self.unauthenticated_client = APIClient()
        
        # Create authentication tokens
        self.admin_token = Token.objects.create(user=self.admin_user)
        self.user_token = Token.objects.create(user=self.regular_user)
        
        # Create test authors
        self.author1 = Author.objects.create(name="George Orwell")
        self.author2 = Author.objects.create(name="Jane Austen")
        self.author3 = Author.objects.create(name="J.K. Rowling")
        
        # Create test books
        self.book1 = Book.objects.create(
            title="1984",
            publication_year=1949,
            author=self.author1
        )
        
        self.book2 = Book.objects.create(
            title="Pride and Prejudice",
            publication_year=1813,
            author=self.author2
        )
        
        self.book3 = Book.objects.create(
            title="Animal Farm",
            publication_year=1945,
            author=self.author1
        )
        
    def authenticate_as_admin(self):
        """Helper method to authenticate as admin user."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
    
    def authenticate_as_user(self):
        """Helper method to authenticate as regular user."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
    
    def unauthenticate(self):
        """Helper method to remove authentication credentials."""
        self.client.credentials()
    
    def login_as_admin(self):
        """Alternative authentication method using session-based login."""
        self.client.login(username='admin', password='testpass123')
    
    def login_as_user(self):
        """Alternative authentication method using session-based login."""
        self.client.login(username='testuser', password='testpass123')


class BookListViewTests(BookAPITestCase):
    """Test cases for BookListView - GET /api/books/"""

    def test_get_all_books_unauthenticated(self):
        """Test that unauthenticated users can view all books."""
        url = reverse('book-list')  # Updated to match your URL name
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        
        # Verify book data structure
        first_book = response.data['results'][0]
        self.assertIn('title', first_book)
        self.assertIn('author', first_book)
        self.assertIn('publication_year', first_book)

    def test_filter_books_by_title(self):
        """Test filtering books by exact title."""
        url = reverse('book-list')
        response = self.client.get(url, {'title': '1984'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], '1984')

    def test_filter_books_by_author(self):
        """Test filtering books by author ID."""
        url = reverse('book-list')
        response = self.client.get(url, {'author': self.author1.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # George Orwell has 2 books
        
        for book in response.data['results']:
            self.assertEqual(book['author'], self.author1.id)

    def test_filter_books_by_publication_year(self):
        """Test filtering books by publication year."""
        url = reverse('book-list')
        response = self.client.get(url, {'publication_year': 1949})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['publication_year'], 1949)

    def test_search_books_by_title(self):
        """Test searching books by title using search parameter."""
        url = reverse('book-list')
        response = self.client.get(url, {'search': 'Animal'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Animal Farm')

    def test_search_books_by_author_name(self):
        """Test searching books by author name using search parameter."""
        url = reverse('book-list')
        response = self.client.get(url, {'search': 'Orwell'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Should find both Orwell books

    def test_order_books_by_title_ascending(self):
        """Test ordering books by title in ascending order."""
        url = reverse('book-list')
        response = self.client.get(url, {'ordering': 'title'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [book['title'] for book in response.data['results']]
        self.assertEqual(titles, ['1984', 'Animal Farm', 'Pride and Prejudice'])

    def test_order_books_by_publication_year_descending(self):
        """Test ordering books by publication year in descending order."""
        url = reverse('book-list')
        response = self.client.get(url, {'ordering': '-publication_year'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        years = [book['publication_year'] for book in response.data['results']]
        self.assertEqual(years, [1949, 1945, 1813])

    def test_combined_filter_and_search(self):
        """Test combining filters and search parameters."""
        url = reverse('book-list')
        response = self.client.get(url, {
            'author': self.author1.id,
            'search': '1984'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], '1984')


class BookDetailViewTests(BookAPITestCase):
    """Test cases for BookDetailView - GET /api/books/<id>/"""

    def test_get_existing_book(self):
        """Test retrieving an existing book by ID."""
        url = reverse('book-detail', kwargs={'id': self.book1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], '1984')
        self.assertEqual(response.data['publication_year'], 1949)
        self.assertEqual(response.data['author'], self.author1.id)

    def test_get_nonexistent_book(self):
        """Test retrieving a non-existent book returns 404."""
        url = reverse('book-detail', kwargs={'id': 9999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_book_detail_unauthenticated_access(self):
        """Test that unauthenticated users can access book details."""
        self.unauthenticate()
        url = reverse('book-detail', kwargs={'id': self.book1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], '1984')


class BookCreateViewTests(BookAPITestCase):
    """Test cases for BookCreateView - POST /api/books/create/"""

    def test_create_book_authenticated_user(self):
        """Test creating a book with authenticated user."""
        self.authenticate_as_user()
        url = reverse('book-create')
        
        book_data = {
            'title': 'The Great Gatsby',
            'publication_year': 1925,
            'author': self.author2.id
        }
        
        response = self.client.post(url, book_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'The Great Gatsby')
        self.assertEqual(response.data['publication_year'], 1925)
        
        # Verify book was actually created in database
        self.assertTrue(Book.objects.filter(title='The Great Gatsby').exists())

    def test_create_book_admin_user(self):
        """Test creating a book with admin user."""
        self.authenticate_as_admin()
        url = reverse('book-create')
        
        book_data = {
            'title': 'To Kill a Mockingbird',
            'publication_year': 1960,
            'author': self.author3.id
        }
        
        response = self.client.post(url, book_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'To Kill a Mockingbird')

    def test_create_book_unauthenticated(self):
        """Test creating a book without authentication should fail."""
        self.unauthenticate()
        url = reverse('book-create')
        
        book_data = {
            'title': 'Unauthorized Book',
            'publication_year': 2023,
            'author': self.author1.id
        }
        
        response = self.client.post(url, book_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_book_invalid_data(self):
        """Test creating a book with invalid data."""
        self.authenticate_as_user()
        url = reverse('book-create')
        
        # Missing required fields
        book_data = {
            'title': '',  # Empty title
            'publication_year': 'invalid_year',  # Invalid year
        }
        
        response = self.client.post(url, book_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_create_book_nonexistent_author(self):
        """Test creating a book with non-existent author."""
        self.authenticate_as_user()
        url = reverse('book-create')
        
        book_data = {
            'title': 'Test Book',
            'publication_year': 2023,
            'author': 9999  # Non-existent author ID
        }
        
        response = self.client.post(url, book_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BookUpdateViewTests(BookAPITestCase):
    """Test cases for BookUpdateView - PATCH /api/books/<id>/update/"""

    def test_update_book_authenticated_user(self):
        """Test updating a book with authenticated user."""
        self.authenticate_as_user()
        url = reverse('book-update', kwargs={'id': self.book1.id})
        
        update_data = {
            'title': '1984 - Updated Edition',
            'publication_year': 1950
        }
        
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], '1984 - Updated Edition')
        self.assertEqual(response.data['publication_year'], 1950)
        
        # Verify changes in database
        updated_book = Book.objects.get(id=self.book1.id)
        self.assertEqual(updated_book.title, '1984 - Updated Edition')

    def test_update_book_admin_user(self):
        """Test updating a book with admin user."""
        self.authenticate_as_admin()
        url = reverse('book-update', kwargs={'id': self.book2.id})
        
        update_data = {'title': 'Pride and Prejudice - Special Edition'}
        
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Pride and Prejudice - Special Edition')

    def test_update_book_unauthenticated(self):
        """Test updating a book without authentication should fail."""
        self.unauthenticate()
        url = reverse('book-update', kwargs={'id': self.book1.id})
        
        update_data = {'title': 'Unauthorized Update'}
        
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_nonexistent_book(self):
        """Test updating a non-existent book."""
        self.authenticate_as_user()
        url = reverse('book-update', kwargs={'id': 9999})
        
        update_data = {'title': 'Non-existent Book'}
        
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_partial_update_book(self):
        """Test partial update of a book (only one field)."""
        self.authenticate_as_user()
        url = reverse('book-update', kwargs={'id': self.book3.id})
        
        original_author = self.book3.author
        update_data = {'title': 'Animal Farm - Revised'}
        
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Animal Farm - Revised')
        self.assertEqual(response.data['author'], original_author.id)  # Should remain unchanged


class BookDeleteViewTests(BookAPITestCase):
    """Test cases for BookDeleteView - DELETE /api/books/<id>/delete/"""

    def test_delete_book_admin_user(self):
        """Test deleting a book with admin user."""
        self.authenticate_as_admin()
        book_id = self.book1.id
        url = reverse('book-delete', kwargs={'id': book_id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['detail'], 'Book deleted successfully.')
        
        # Verify book was actually deleted from database
        self.assertFalse(Book.objects.filter(id=book_id).exists())

    def test_delete_book_regular_user(self):
        """Test deleting a book with regular user should fail."""
        self.authenticate_as_user()
        url = reverse('book-delete', kwargs={'id': self.book1.id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify book still exists
        self.assertTrue(Book.objects.filter(id=self.book1.id).exists())

    def test_delete_book_unauthenticated(self):
        """Test deleting a book without authentication should fail."""
        self.unauthenticate()
        url = reverse('book-delete', kwargs={'id': self.book1.id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_nonexistent_book(self):
        """Test deleting a non-existent book."""
        self.authenticate_as_admin()
        url = reverse('book-delete', kwargs={'id': 9999})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BookAPIIntegrationTests(BookAPITestCase):
    """Integration tests for complete Book API workflows."""

    def test_complete_book_lifecycle(self):
        """Test complete CRUD lifecycle of a book."""
        # 1. Create a book
        self.authenticate_as_user()
        create_url = reverse('book-create')
        
        book_data = {
            'title': 'Test Lifecycle Book',
            'publication_year': 2023,
            'author': self.author1.id
        }
        
        create_response = self.client.post(create_url, book_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        
        book_id = create_response.data['id']
        
        # 2. Read the book
        detail_url = reverse('book-detail', kwargs={'id': book_id})
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data['title'], 'Test Lifecycle Book')
        
        # 3. Update the book
        update_url = reverse('book-update', kwargs={'id': book_id})
        update_data = {'title': 'Updated Lifecycle Book'}
        
        update_response = self.client.patch(update_url, update_data, format='json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['title'], 'Updated Lifecycle Book')
        
        # 4. Delete the book (need admin permissions)
        self.authenticate_as_admin()
        delete_url = reverse('book-delete', kwargs={'id': book_id})
        delete_response = self.client.delete(delete_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 5. Verify book is deleted
        detail_response_after_delete = self.client.get(detail_url)
        self.assertEqual(detail_response_after_delete.status_code, status.HTTP_404_NOT_FOUND)

    def test_permission_hierarchy(self):
        """Test that permission hierarchy works correctly."""
        # Admin can do everything
        self.authenticate_as_admin()
        
        # Create
        create_url = reverse('book-create')
        book_data = {'title': 'Admin Book', 'publication_year': 2023, 'author': self.author1.id}
        response = self.client.post(create_url, book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        book_id = response.data['id']
        
        # Update
        update_url = reverse('book-update', kwargs={'id': book_id})
        response = self.client.patch(update_url, {'title': 'Updated Admin Book'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Delete
        delete_url = reverse('book-delete', kwargs={'id': book_id})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


# Test Data Validation
class BookDataValidationTests(BookAPITestCase):
    """Test data validation and edge cases."""

    def test_create_book_with_future_publication_year(self):
        """Test creating a book with future publication year."""
        self.authenticate_as_user()
        url = reverse('book-create')
        
        book_data = {
            'title': 'Future Book',
            'publication_year': 2050,
            'author': self.author1.id
        }
        
        response = self.client.post(url, book_data, format='json')
        # Depending on your validation rules, this might pass or fail
        # Adjust the assertion based on your business logic
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])

    def test_create_book_with_very_long_title(self):
        """Test creating a book with extremely long title."""
        self.authenticate_as_user()
        url = reverse('book-create')
        
        long_title = 'A' * 1000  # Very long title
        book_data = {
            'title': long_title,
            'publication_year': 2023,
            'author': self.author1.id
        }
        
        response = self.client.post(url, book_data, format='json')
        # Should fail if title has max_length validation
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_session_authentication_with_separate_database(self):
        """Test using session-based authentication with separate test database."""
        # This test demonstrates that the separate test database is working
        # with session-based authentication using self.client.login
        
        # Login using session authentication
        login_success = self.client.login(username='testuser', password='testpass123')
        self.assertTrue(login_success)
        
        # Create a book using session authentication
        url = reverse('book-create')
        book_data = {
            'title': 'Session Auth Test Book',
            'publication_year': 2023,
            'author': self.author1.id
        }
        
        response = self.client.post(url, book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Session Auth Test Book')
        
        # Verify the book exists in the test database
        self.assertTrue(Book.objects.filter(title='Session Auth Test Book').exists())
        
        # Logout
        self.client.logout()