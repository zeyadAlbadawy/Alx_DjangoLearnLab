from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from api.models import Book, Author  # Adjust import if your Author model is elsewhere


class BookAPITestCase(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.client = APIClient()
        self.client.login(username="testuser", password="testpass123")

        # Create an author
        self.author = Author.objects.create(name="John Doe")

        # Create a sample book
        self.book = Book.objects.create(
            title="Sample Book",
            publication_year=2024,
            author=self.author
        )

        # URL endpoints
        self.list_url = reverse("book-list")
        self.create_url = reverse("book-create")
        self.update_url = reverse("book-update", args=[self.book.id])
        self.delete_url = reverse("book-delete", args=[self.book.id])

    def test_create_book(self):
        data = {
            "title": "New Book",
            "publication_year": 2025,
            "author": self.author.id
        }
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)
        self.assertEqual(Book.objects.last().title, "New Book")

    def test_update_book(self):
        data = {"title": "Updated Title"}
        response = self.client.patch(self.update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "Updated Title")

    def test_delete_book(self):
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)

    def test_filter_books_by_title(self):
        response = self.client.get(self.list_url, {"title": "Sample Book"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(book["title"] == "Sample Book" for book in response.data))

    def test_filter_books_by_year(self):
        response = self.client.get(self.list_url, {"publication_year": 2024})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_books(self):
        response = self.client.get(self.list_url, {"search": "Sample"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any("Sample" in book["title"] for book in response.data))

    def test_order_books_by_year(self):
        Book.objects.create(title="Older Book", publication_year=2020, author=self.author)
        response = self.client.get(self.list_url, {"ordering": "publication_year"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        years = [book["publication_year"] for book in response.data]
        self.assertEqual(years, sorted(years))

    def test_permissions_required(self):
        self.client.logout()
        response = self.client.post(self.create_url, {"title": "No Auth"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
