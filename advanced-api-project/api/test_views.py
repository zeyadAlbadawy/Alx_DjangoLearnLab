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
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('results', res.data)
        self.assertEqual(len(res.data['results']), 3)

    def test_filter_by_title(self):
        """Test title filter"""
        url = reverse('book-list')
        res = self.client.get(url, {'title': '1984'})
        self.assertEqual(len(res.data['results']), 1)
        self.assertEqual(res.data['results'][0]['title'], '1984')

    def test_filter_by_author(self):
        """Test author filter"""
        url = reverse('book-list')
        res = self.client.get(url, {'author': self.author1.id})
        self.assertEqual(len(res.data['results']), 2)
        titles = {b['title'] for b in res.data['results']}
        self.assertEqual(titles, {'1984', 'Animal Farm'})

    def test_search_by_title(self):
        """Test title search"""
        url = reverse('book-list')
        res = self.client.get(url, {'search': 'Animal'})
        self.assertEqual(len(res.data['results']), 1)
        self.assertEqual(res.data['results'][0]['title'], 'Animal Farm')

    def test_order_by_year_desc(self):
        """Test ordering by publication year"""
        url = reverse('book-list')
        res = self.client.get(url, {'ordering': '-publication_year'})
        years = [b['publication_year'] for b in res.data['results']]
        self.assertEqual(years, [1949, 1945, 1813])

    def test_pagination(self):
        """Test pagination works"""
        url = reverse('book-list')
        res = self.client.get(url, {'page_size': 2})
        self.assertEqual(len(res.data['results']), 2)
        self.assertIn('next', res.data)


class BookDetailViewTests(BookAPITestCase):
    """Tests for GET /books/<id>/ endpoint"""

    def test_get_existing_book(self):
        """Verify book detail retrieval"""
        url = reverse('book-detail', kwargs={'id': self.book1.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], '1984')
        self.assertEqual(res.data['publication_year'], 1949)
        self.assertEqual(res.data['author'], self.author1.id)

    def test_get_nonexistent_book(self):
        """Verify 404 for invalid book ID"""
        url = reverse('book-detail', kwargs={'id': 999})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


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
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['title'], 'The Great Gatsby')
        self.assertTrue(Book.objects.filter(title='The Great Gatsby').exists())

    def test_create_book_unauthenticated(self):
        """Verify unauthenticated users cannot create books"""
        self.unauthenticate()
        url = reverse('book-create')
        data = {
            'title': 'Unauthorized', 
            'publication_year': 2023, 
            'author': self.author1.id
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Book.objects.filter(title='Unauthorized').exists())

    def test_create_book_invalid_data(self):
        """Verify validation for invalid book data"""
        url = reverse('book-create')
        invalid_data = [
            {'title': '', 'publication_year': 2023, 'author': self.author1.id},  # Empty title
            {'title': 'No Year', 'author': self.author1.id},  # Missing year
            {'title': 'No Author', 'publication_year': 2023},  # Missing author
        ]
        
        for data in invalid_data:
            res = self.client.post(url, data, format='json')
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class BookUpdateViewTests(BookAPITestCase):
    """Tests for PATCH /books/<id>/update/ endpoint"""

    def test_update_book_authenticated_user(self):
        """Verify authenticated users can update books"""
        url = reverse('book-update', kwargs={'id': self.book1.id})
        res = self.client.patch(url, {'title': '1984 - Updated'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], '1984 - Updated')
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, '1984 - Updated')

    def test_update_nonexistent_book(self):
        """Verify 404 for invalid book ID"""
        url = reverse('book-update', kwargs={'id': 999})
        res = self.client.patch(url, {'title': 'Does Not Exist'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_book_unauthenticated(self):
        """Verify unauthenticated users cannot update books"""
        self.unauthenticate()
        url = reverse('book-update', kwargs={'id': self.book1.id})
        res = self.client.patch(url, {'title': 'Unauthorized Update'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, '1984')  # Verify no change


class BookDeleteViewTests(BookAPITestCase):
    """Tests for DELETE /books/<id>/delete/ endpoint"""

    def test_delete_book_admin_user(self):
        """Verify admin users can delete books"""
        self.authenticate_as_admin()
        url = reverse('book-delete', kwargs={'id': self.book1.id})
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=self.book1.id).exists())

    def test_delete_book_regular_user_forbidden(self):
        """Verify regular users cannot delete books"""
        url = reverse('book-delete', kwargs={'id': self.book1.id})
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Book.objects.filter(id=self.book1.id).exists())  # Verify still exists

    def test_delete_nonexistent_book(self):
        """Verify 404 for invalid book ID"""
        self.authenticate_as_admin()
        url = reverse('book-delete', kwargs={'id': 999})
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class BookAPIIntegrationTests(BookAPITestCase):
    """End-to-end CRUD workflow tests"""

    def test_complete_lifecycle(self):
        """Test full create-read-update-delete cycle"""
        # Create
        create_url = reverse('book-create')
        data = {
            'title': 'Lifecycle Book',
            'publication_year': 2023,
            'author': self.author1.id
        }
        res = self.client.post(create_url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book_id = res.data['id']

        # Read
        detail_url = reverse('book-detail', kwargs={'id': book_id})
        res = self.client.get(detail_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], 'Lifecycle Book')

        # Update
        update_url = reverse('book-update', kwargs={'id': book_id})
        res = self.client.patch(update_url, {'title': 'Updated Title'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], 'Updated Title')

        # Verify update
        res = self.client.get(detail_url)
        self.assertEqual(res.data['title'], 'Updated Title')

        # Delete as admin
        self.authenticate_as_admin()
        delete_url = reverse('book-delete', kwargs={'id': book_id})
        res = self.client.delete(delete_url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        # Verify deletion
        res = self.client.get(detail_url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)