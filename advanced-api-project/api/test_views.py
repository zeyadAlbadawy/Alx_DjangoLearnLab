"""
Unit Tests for Advanced API Project - Book API Endpoints

Testing Strategy:
- Uses Django's built-in test framework with Python's unittest
- Configures separate test database via Django TestCase
- Tests CRUD operations with authentication scenarios
- Verifies filtering, searching and ordering
- Includes negative test cases for error handling

To run tests:
python manage.py test api
"""

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Book, Author


class BookAPITestCase(APITestCase):
    """
    Base test case for Book API tests
    Configures test database with sample data
    """
    
    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole TestCase (runs once)"""
        # Create users
        cls.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        cls.regular_user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )

        # Auth tokens
        cls.admin_token = Token.objects.create(user=cls.admin_user)
        cls.user_token = Token.objects.create(user=cls.regular_user)

        # Authors
        cls.author1 = Author.objects.create(name="George Orwell")
        cls.author2 = Author.objects.create(name="Jane Austen")
        cls.author3 = Author.objects.create(name="J.K. Rowling")

        # Books
        cls.book1 = Book.objects.create(
            title="1984", publication_year=1949, author=cls.author1
        )
        cls.book2 = Book.objects.create(
            title="Pride and Prejudice", publication_year=1813, author=cls.author2
        )
        cls.book3 = Book.objects.create(
            title="Animal Farm", publication_year=1945, author=cls.author1
        )

    def setUp(self):
        """Runs before each test"""
        # Default to regular user auth
        self.authenticate_as_user()

    def authenticate_as_admin(self):
        """Set admin credentials for requests"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')

    def authenticate_as_user(self):
        """Set regular user credentials for requests"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')

    def unauthenticate(self):
        """Remove any credentials"""
        self.client.credentials()


class BookListViewTests(BookAPITestCase):
    """Tests for GET /books/ endpoint"""
    
    def test_get_all_books_unauthenticated(self):
        """Verify public access to book list"""
        self.unauthenticate()
        url = reverse('book-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 3)
        # Verify response data structure
        for book in response.data['results']:
            self.assertIn('id', book)
            self.assertIn('title', book)
            self.assertIn('publication_year', book)
            self.assertIn('author', book)

    def test_filter_by_title(self):
        """Test title filter"""
        url = reverse('book-list')
        response = self.client.get(url, {'title': '1984'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], '1984')
        self.assertEqual(response.data['results'][0]['publication_year'], 1949)
        self.assertEqual(response.data['results'][0]['author'], self.author1.id)

    def test_filter_by_author(self):
        """Test author filter"""
        url = reverse('book-list')
        response = self.client.get(url, {'author': self.author1.id})
        self.assertEqual(len(response.data['results']), 2)
        titles = {b['title'] for b in response.data['results']}
        self.assertEqual(titles, {'1984', 'Animal Farm'})

    def test_search_by_title(self):
        """Test title search"""
        url = reverse('book-list')
        response = self.client.get(url, {'search': 'Animal'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Animal Farm')
        self.assertEqual(response.data['results'][0]['author'], self.author1.id)

    def test_order_by_year_desc(self):
        """Test ordering by publication year"""
        url = reverse('book-list')
        response = self.client.get(url, {'ordering': '-publication_year'})
        years = [b['publication_year'] for b in response.data['results']]
        self.assertEqual(years, [1949, 1945, 1813])
        # Verify first book is 1984
        self.assertEqual(response.data['results'][0]['title'], '1984')


class BookDetailViewTests(BookAPITestCase):
    """Tests for GET /books/<id>/ endpoint"""

    def test_get_existing_book(self):
        """Verify book detail retrieval"""
        url = reverse('book-detail', kwargs={'id': self.book1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], '1984')
        self.assertEqual(response.data['publication_year'], 1949)
        self.assertEqual(response.data['author'], self.author1.id)
        # Verify all expected fields are present
        expected_fields = {'id', 'title', 'publication_year', 'author'}
        self.assertEqual(set(response.data.keys()), expected_fields)

    def test_get_nonexistent_book(self):
        """Verify 404 for invalid book ID"""
        url = reverse('book-detail', kwargs={'id': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Verify error message in response data
        self.assertIn('detail', response.data)


class BookCreateViewTests(BookAPITestCase):
    """Tests for POST /books/create/ endpoint"""

    def test_create_book_authenticated_user(self):
        """Verify authenticated users can create books"""
        url = reverse('book-create')
        data = {
            'title': 'The Great Gatsby', 
            'publication_year': 1925, 
            'author': self.author2.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Verify response data matches input
        self.assertEqual(response.data['title'], 'The Great Gatsby')
        self.assertEqual(response.data['publication_year'], 1925)
        self.assertEqual(response.data['author'], self.author2.id)
        # Verify database record
        book = Book.objects.get(title='The Great Gatsby')
        self.assertEqual(book.publication_year, 1925)

    def test_create_book_unauthenticated(self):
        """Verify unauthenticated users cannot create books"""
        self.unauthenticate()
        url = reverse('book-create')
        data = {
            'title': 'Unauthorized', 
            'publication_year': 2023, 
            'author': self.author1.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Verify error message in response data
        self.assertIn('detail', response.data)

    def test_create_book_invalid_data(self):
        """Verify validation for invalid book data"""
        url = reverse('book-create')
        test_cases = [
            ({'title': '', 'publication_year': 2023, 'author': self.author1.id}, 'title'),
            ({'title': 'No Year', 'author': self.author1.id}, 'publication_year'),
            ({'title': 'No Author', 'publication_year': 2023}, 'author'),
            ({'title': 'Invalid Year', 'publication_year': 'abc', 'author': self.author1.id}, 'publication_year'),
        ]
        
        for data, error_field in test_cases:
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(error_field, response.data)


class BookUpdateViewTests(BookAPITestCase):
    """Tests for PATCH /books/<id>/update/ endpoint"""

    def test_update_book_authenticated_user(self):
        """Verify authenticated users can update books"""
        url = reverse('book-update', kwargs={'id': self.book1.id})
        new_title = '1984 - Updated Edition'
        response = self.client.patch(url, {'title': new_title}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify response data
        self.assertEqual(response.data['title'], new_title)
        # Verify other fields unchanged
        self.assertEqual(response.data['publication_year'], 1949)
        self.assertEqual(response.data['author'], self.author1.id)
        # Verify database
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, new_title)

    def test_update_nonexistent_book(self):
        """Verify 404 for invalid book ID"""
        url = reverse('book-update', kwargs={'id': 999})
        response = self.client.patch(url, {'title': 'Does Not Exist'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)

    def test_update_book_unauthenticated(self):
        """Verify unauthenticated users cannot update books"""
        self.unauthenticate()
        url = reverse('book-update', kwargs={'id': self.book1.id})
        response = self.client.patch(url, {'title': 'Unauthorized Update'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('detail', response.data)
        # Verify no changes were made
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, '1984')


class BookDeleteViewTests(BookAPITestCase):
    """Tests for DELETE /books/<id>/delete/ endpoint"""

    def test_delete_book_admin_user(self):
        """Verify admin users can delete books"""
        self.authenticate_as_admin()
        url = reverse('book-delete', kwargs={'id': self.book1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Verify empty response
        self.assertEqual(response.data, None)
        # Verify book was deleted
        self.assertFalse(Book.objects.filter(id=self.book1.id).exists())

    def test_delete_book_regular_user_forbidden(self):
        """Verify regular users cannot delete books"""
        url = reverse('book-delete', kwargs={'id': self.book1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('detail', response.data)
        # Verify book still exists
        self.assertTrue(Book.objects.filter(id=self.book1.id).exists())

    def test_delete_nonexistent_book(self):
        """Verify 404 for invalid book ID"""
        self.authenticate_as_admin()
        url = reverse('book-delete', kwargs={'id': 999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)


class BookAPIIntegrationTests(BookAPITestCase):
    """End-to-end CRUD workflow tests"""

    def test_complete_lifecycle(self):
        """Test full create-read-update-delete cycle"""
        # Create
        create_url = reverse('book-create')
        book_data = {
            'title': 'Lifecycle Book',
            'publication_year': 2023,
            'author': self.author1.id
        }
        create_response = self.client.post(create_url, book_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        book_id = create_response.data['id']
        # Verify create response data
        self.assertEqual(create_response.data['title'], 'Lifecycle Book')
        self.assertEqual(create_response.data['publication_year'], 2023)

        # Read
        detail_url = reverse('book-detail', kwargs={'id': book_id})
        read_response = self.client.get(detail_url)
        self.assertEqual(read_response.status_code, status.HTTP_200_OK)
        # Verify read response matches created data
        self.assertEqual(read_response.data['title'], 'Lifecycle Book')
        self.assertEqual(read_response.data['author'], self.author1.id)

        # Update
        update_url = reverse('book-update', kwargs={'id': book_id})
        update_response = self.client.patch(
            update_url, 
            {'title': 'Updated Title'}, 
            format='json'
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        # Verify update response
        self.assertEqual(update_response.data['title'], 'Updated Title')
        self.assertEqual(update_response.data['publication_year'], 2023)  # unchanged

        # Verify update by reading again
        updated_read_response = self.client.get(detail_url)
        self.assertEqual(updated_read_response.data['title'], 'Updated Title')

        # Delete as admin
        self.authenticate_as_admin()
        delete_url = reverse('book-delete', kwargs={'id': book_id})
        delete_response = self.client.delete(delete_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(delete_response.data, None)

        # Verify deletion
        verify_response = self.client.get(detail_url)
        self.assertEqual(verify_response.status_code, status.HTTP_404_NOT_FOUND)