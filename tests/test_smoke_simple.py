import pytest
from app.database import reset_db
from app.content_service import ContentService, AuthorService, CategoryService
from app.models import ContentCreate, BookCreate, ContentType


@pytest.fixture()
def fresh_db():
    """Provide a fresh database for each test."""
    reset_db()
    yield
    reset_db()


def test_digital_library_smoke(fresh_db):
    """Simple smoke test for digital library functionality."""
    # Test author creation
    author = AuthorService.create_author("Test", "Author")
    assert author.first_name == "Test"
    assert author.last_name == "Author"

    # Test category creation
    category = CategoryService.create_category("Fiction")
    assert category.name == "Fiction"

    # Test book creation
    content_data = ContentCreate(
        title="Smoke Test Book", description="A book for smoke testing", content_type=ContentType.BOOK
    )
    book_data = BookCreate(publisher="Test Publisher")

    book = ContentService.create_book(content_data, book_data)
    assert book is not None
    assert book.title == "Smoke Test Book"

    # Test search functionality
    results = ContentService.search_content(query="Smoke")
    assert len(results) == 1
    assert results[0].title == "Smoke Test Book"

    # Test statistics
    stats = ContentService.get_available_content_count()
    assert stats[ContentType.BOOK] == 1

    # Test getting all books
    books = ContentService.get_books()
    assert len(books) == 1
    assert books[0].title == "Smoke Test Book"


def test_app_modules_importable():
    """Test that all app modules can be imported without errors."""
    # Test service imports
    from app.content_service import ContentService, AuthorService, CategoryService
    from app.digital_library import create as create_digital_library
    from app.content_management import create as create_content_management
    from app.sample_data import create_sample_data, has_sample_data

    # Basic sanity checks
    assert ContentService is not None
    assert AuthorService is not None
    assert CategoryService is not None
    assert create_digital_library is not None
    assert create_content_management is not None
    assert create_sample_data is not None
    assert has_sample_data is not None


def test_database_operations():
    """Test basic database operations work."""
    from app.database import create_tables, get_session

    # Test table creation
    create_tables()

    # Test session creation
    with get_session() as session:
        assert session is not None
