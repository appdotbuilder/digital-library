import pytest
from app.database import reset_db
from app.content_service import ContentService
from app.models import ContentCreate, BookCreate, ContentType


@pytest.fixture()
def fresh_db():
    """Provide a fresh database for each test."""
    reset_db()
    yield
    reset_db()


class TestDigitalLibraryIntegration:
    """Integration tests for digital library functionality."""

    def test_create_and_retrieve_book(self, fresh_db):
        """Test creating and retrieving a book with full details."""
        # Create a book
        content_data = ContentCreate(
            title="Integration Test Book",
            description="A book for integration testing",
            content_type=ContentType.BOOK,
            isbn="978-0123456789",
            language="English",
            tags=["test", "integration"],
        )

        book_data = BookCreate(publisher="Test Publisher", page_count=200, edition="First Edition", format="paperback")

        created_book = ContentService.create_book(content_data, book_data)

        # Verify creation
        assert created_book is not None
        assert created_book.title == "Integration Test Book"
        assert created_book.content_type == ContentType.BOOK

        # Test retrieval
        if created_book.id is not None:
            retrieved_book = ContentService.get_content_by_id(created_book.id)
            assert retrieved_book is not None
            assert retrieved_book.title == "Integration Test Book"

            # Test detailed retrieval
            details = ContentService.get_content_with_details(created_book.id)
            assert details is not None
            assert details["content"].title == "Integration Test Book"
            assert details["extended_info"] is not None
            assert details["extended_info"].publisher == "Test Publisher"

    def test_search_functionality(self, fresh_db):
        """Test search functionality works correctly."""
        # Create multiple books
        books_data = [
            ("Python Programming", "Learn Python programming"),
            ("Java Development", "Java programming guide"),
            ("Web Development", "Learn web development"),
        ]

        for title, description in books_data:
            content_data = ContentCreate(title=title, description=description, content_type=ContentType.BOOK)
            ContentService.create_book(content_data, BookCreate())

        # Test search by title
        python_results = ContentService.search_content(query="Python")
        assert len(python_results) == 1
        assert python_results[0].title == "Python Programming"

        # Test search by description
        programming_results = ContentService.search_content(query="programming")
        assert len(programming_results) >= 2  # Python and Java both have "programming"

        # Test empty search returns all
        all_results = ContentService.search_content(query="")
        assert len(all_results) == 3

    def test_content_statistics(self, fresh_db):
        """Test that content statistics work correctly."""
        # Create content of different types
        book_data = ContentCreate(title="Test Book", content_type=ContentType.BOOK)
        ContentService.create_book(book_data, BookCreate())

        # Get statistics
        stats = ContentService.get_available_content_count()

        assert stats[ContentType.BOOK] == 1
        assert stats[ContentType.ARTICLE] == 0
        assert stats[ContentType.MAGAZINE] == 0
        assert stats[ContentType.MULTIMEDIA] == 0

    def test_get_books_functionality(self, fresh_db):
        """Test getting books specifically."""
        # Create books
        for i in range(3):
            content_data = ContentCreate(title=f"Book {i + 1}", content_type=ContentType.BOOK)
            ContentService.create_book(content_data, BookCreate())

        books = ContentService.get_books()

        assert len(books) == 3
        for book in books:
            assert book.content_type == ContentType.BOOK

    def test_filter_by_content_type(self, fresh_db):
        """Test filtering content by type."""
        # Create book
        book_data = ContentCreate(title="Test Book", content_type=ContentType.BOOK)
        ContentService.create_book(book_data, BookCreate())

        # Search for books only
        book_results = ContentService.search_content(content_type=ContentType.BOOK)
        assert len(book_results) == 1
        assert book_results[0].content_type == ContentType.BOOK

        # Search for articles (should be empty)
        article_results = ContentService.search_content(content_type=ContentType.ARTICLE)
        assert len(article_results) == 0

    def test_search_limit(self, fresh_db):
        """Test search limit functionality."""
        # Create multiple books
        for i in range(10):
            content_data = ContentCreate(title=f"Book {i + 1}", content_type=ContentType.BOOK)
            ContentService.create_book(content_data, BookCreate())

        # Test limit
        limited_results = ContentService.search_content(limit=5)
        assert len(limited_results) == 5

        # Test no limit gets more
        all_results = ContentService.search_content(limit=20)
        assert len(all_results) == 10
