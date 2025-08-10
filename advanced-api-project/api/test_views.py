from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from api.models import Book
from api.serializers import BookSerializer


class BookAPITestCase(APITestCase):
    def setUp(self):
        # Create sample books
        self.book1 = Book.objects.create(
            title="Django for Beginners",
            author="William S. Vincent",
            published_date="2023-08-01"
        )
        self.book2 = Book.objects.create(
            title="Two Scoops of Django",
            author="Daniel Roy Greenfeld",
            published_date="2022-05-15"
        )
        self.book3 = Book.objects.create(
            title="Python Crash Course",
            author="Eric Matthes",
            published_date="2021-01-10"
        )

        self.list_url = reverse('book-list')  # Name from your DRF router

    def test_list_books(self):
        """Test retrieving the list of books"""
        response = self.client.get(self.list_url)
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)  # ✅ compare with serializer
        self.assertEqual(len(response.data), books.count())  # ✅ check length

    def test_create_book(self):
        """Test creating a new book"""
        data = {
            "title": "New Test Book",
            "author": "Jane Doe",
            "published_date": "2024-01-01"
        }
        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("title", response.data)  # ✅ key check
        self.assertEqual(response.data["title"], data["title"])  # ✅ value check

    def test_filter_books_by_author(self):
        """Test filtering books by author"""
        url = f"{self.list_url}?author=William S. Vincent"
        response = self.client.get(url)

        books = Book.objects.filter(author="William S. Vincent")
        serializer = BookSerializer(books, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)  # ✅ filtered match

    def test_search_books_by_title(self):
        """Test searching books by title"""
        url = f"{self.list_url}?search=Python"
        response = self.client.get(url)

        books = Book.objects.filter(title__icontains="Python")
        serializer = BookSerializer(books, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)  # ✅ search match

    def test_order_books_by_published_date_desc(self):
        """Test ordering books by published date descending"""
        url = f"{self.list_url}?ordering=-published_date"
        response = self.client.get(url)

        books = Book.objects.all().order_by('-published_date')
        serializer = BookSerializer(books, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)  # ✅ ordered match
