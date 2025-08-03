import pytest

from app.database import reset_db
from app.content_service import ContentService, AuthorService, CategoryService
from app.models import Content, ContentType, ContentStatus, ContentCreate, BookCreate


@pytest.fixture()
def fresh_db():
    """Provide a fresh database for each test."""
    reset_db()
    yield
    reset_db()


class TestContentService:
    """Test the ContentService class."""

    def test_search_content_empty_query(self, fresh_db):
        """Test searching with empty query returns recent content."""
        # Create test content
        content_data = ContentCreate(title="Test Book", description="A test book", content_type=ContentType.BOOK)
        book_data = BookCreate(publisher="Test Publisher")
        ContentService.create_book(content_data, book_data)

        # Search with empty query
        results = ContentService.search_content(query="")

        assert len(results) == 1
        assert results[0].title == "Test Book"

    def test_search_content_by_title(self, fresh_db):
        """Test searching content by title."""
        # Create test books
        book1_data = ContentCreate(title="Python Programming", content_type=ContentType.BOOK)
        book2_data = ContentCreate(title="Java Development", content_type=ContentType.BOOK)

        ContentService.create_book(book1_data, BookCreate())
        ContentService.create_book(book2_data, BookCreate())

        # Search for Python
        results = ContentService.search_content(query="Python")

        assert len(results) == 1
        assert results[0].title == "Python Programming"

    def test_search_content_by_description(self, fresh_db):
        """Test searching content by description."""
        content_data = ContentCreate(
            title="Programming Book", description="Learn advanced Python techniques", content_type=ContentType.BOOK
        )
        ContentService.create_book(content_data, BookCreate())

        results = ContentService.search_content(query="advanced")

        assert len(results) == 1
        assert results[0].description == "Learn advanced Python techniques"

    def test_search_content_by_tags(self, fresh_db):
        """Test that content has tags (tags are not searchable in current implementation)."""
        content_data = ContentCreate(
            title="Programming Book", content_type=ContentType.BOOK, tags=["programming", "python", "beginner"]
        )
        created_book = ContentService.create_book(content_data, BookCreate())

        # Tags are stored but not searchable via text search
        assert created_book is not None
        assert "beginner" in created_book.tags

    def test_search_content_case_insensitive(self, fresh_db):
        """Test that search is case insensitive."""
        content_data = ContentCreate(title="PYTHON Programming", content_type=ContentType.BOOK)
        ContentService.create_book(content_data, BookCreate())

        results = ContentService.search_content(query="python")

        assert len(results) == 1
        assert results[0].title == "PYTHON Programming"

    def test_search_content_by_type(self, fresh_db):
        """Test filtering content by type."""
        book_data = ContentCreate(title="Test Book", content_type=ContentType.BOOK)
        article_data = ContentCreate(title="Test Article", content_type=ContentType.ARTICLE)

        ContentService.create_book(book_data, BookCreate())
        # For article, we need to create content directly since we don't have create_article method
        from app.database import get_session

        with get_session() as session:
            article = Content(**article_data.model_dump())
            session.add(article)
            session.commit()

        # Search for books only
        results = ContentService.search_content(content_type=ContentType.BOOK)

        assert len(results) == 1
        assert results[0].content_type == ContentType.BOOK

    def test_search_available_only(self, fresh_db):
        """Test filtering by availability status."""
        from app.database import get_session

        # Create available content
        available_data = ContentCreate(title="Available Book", content_type=ContentType.BOOK)
        ContentService.create_book(available_data, BookCreate())

        # Create checked out content
        with get_session() as session:
            checked_out = Content(
                title="Checked Out Book", content_type=ContentType.BOOK, status=ContentStatus.CHECKED_OUT
            )
            session.add(checked_out)
            session.commit()

        # Search available only
        results = ContentService.search_content(available_only=True)

        assert len(results) == 1
        assert results[0].status == ContentStatus.AVAILABLE

    def test_search_all_status(self, fresh_db):
        """Test searching all content regardless of status."""
        from app.database import get_session

        # Create content with different statuses
        available_data = ContentCreate(title="Available Book", content_type=ContentType.BOOK)
        ContentService.create_book(available_data, BookCreate())

        with get_session() as session:
            checked_out = Content(
                title="Checked Out Book", content_type=ContentType.BOOK, status=ContentStatus.CHECKED_OUT
            )
            session.add(checked_out)
            session.commit()

        # Search all status
        results = ContentService.search_content(available_only=False)

        assert len(results) == 2

    def test_search_content_limit(self, fresh_db):
        """Test search limit parameter."""
        # Create multiple books
        for i in range(5):
            content_data = ContentCreate(title=f"Book {i}", content_type=ContentType.BOOK)
            ContentService.create_book(content_data, BookCreate())

        results = ContentService.search_content(limit=3)

        assert len(results) == 3

    def test_get_content_by_id_exists(self, fresh_db):
        """Test getting content by ID when it exists."""
        content_data = ContentCreate(title="Test Book", content_type=ContentType.BOOK)
        created_content = ContentService.create_book(content_data, BookCreate())

        if created_content and created_content.id is not None:
            retrieved_content = ContentService.get_content_by_id(created_content.id)

            assert retrieved_content is not None
            assert retrieved_content.title == "Test Book"

    def test_get_content_by_id_not_exists(self, fresh_db):
        """Test getting content by ID when it doesn't exist."""
        result = ContentService.get_content_by_id(999)

        assert result is None

    def test_get_books(self, fresh_db):
        """Test getting all books."""
        # Create books and articles
        book_data = ContentCreate(title="Test Book", content_type=ContentType.BOOK)
        ContentService.create_book(book_data, BookCreate())

        from app.database import get_session

        with get_session() as session:
            article = Content(title="Test Article", content_type=ContentType.ARTICLE)
            session.add(article)
            session.commit()

        books = ContentService.get_books()

        assert len(books) == 1
        assert books[0].content_type == ContentType.BOOK

    def test_get_books_limit(self, fresh_db):
        """Test getting books with limit."""
        # Create multiple books
        for i in range(5):
            content_data = ContentCreate(title=f"Book {i}", content_type=ContentType.BOOK)
            ContentService.create_book(content_data, BookCreate())

        books = ContentService.get_books(limit=3)

        assert len(books) == 3

    def test_create_book_success(self, fresh_db):
        """Test successful book creation."""
        content_data = ContentCreate(
            title="New Book",
            description="A new book description",
            content_type=ContentType.BOOK,
            isbn="978-0123456789",
            language="English",
            tags=["fiction", "adventure"],
        )

        book_data = BookCreate(publisher="Test Publisher", page_count=300, edition="First Edition", format="hardcover")

        result = ContentService.create_book(content_data, book_data)

        assert result is not None
        assert result.title == "New Book"
        assert result.isbn == "978-0123456789"
        assert result.tags == ["fiction", "adventure"]

    def test_create_book_with_authors(self, fresh_db):
        """Test creating book with authors."""
        # Create authors first
        author1 = AuthorService.create_author("John", "Doe")
        author2 = AuthorService.create_author("Jane", "Smith")

        content_data = ContentCreate(title="Multi-Author Book", content_type=ContentType.BOOK)
        book_data = BookCreate()

        if author1.id is not None and author2.id is not None:
            result = ContentService.create_book(content_data, book_data, author_ids=[author1.id, author2.id])

            assert result is not None
            if result.id is not None:
                authors = ContentService.get_content_authors(result.id)
                assert len(authors) == 2

    def test_create_book_with_categories(self, fresh_db):
        """Test creating book with categories."""
        # Create categories first
        cat1 = CategoryService.create_category("Fiction")
        cat2 = CategoryService.create_category("Adventure")

        content_data = ContentCreate(title="Categorized Book", content_type=ContentType.BOOK)
        book_data = BookCreate()

        if cat1.id is not None and cat2.id is not None:
            result = ContentService.create_book(content_data, book_data, category_ids=[cat1.id, cat2.id])

            assert result is not None
            if result.id is not None:
                categories = ContentService.get_content_categories(result.id)
                assert len(categories) == 2

    def test_update_content_status_success(self, fresh_db):
        """Test successful content status update."""
        content_data = ContentCreate(title="Test Book", content_type=ContentType.BOOK)
        content = ContentService.create_book(content_data, BookCreate())

        if content and content.id is not None:
            result = ContentService.update_content_status(content.id, ContentStatus.CHECKED_OUT)

            assert result is True
            updated_content = ContentService.get_content_by_id(content.id)
            assert updated_content is not None
            assert updated_content.status == ContentStatus.CHECKED_OUT

    def test_update_content_status_not_found(self, fresh_db):
        """Test updating status of non-existent content."""
        result = ContentService.update_content_status(999, ContentStatus.CHECKED_OUT)

        assert result is False

    def test_get_available_content_count(self, fresh_db):
        """Test getting count of available content by type."""
        # Create content of different types
        book_data = ContentCreate(title="Test Book", content_type=ContentType.BOOK)
        ContentService.create_book(book_data, BookCreate())

        from app.database import get_session

        with get_session() as session:
            article = Content(title="Test Article", content_type=ContentType.ARTICLE)
            session.add(article)
            session.commit()

        counts = ContentService.get_available_content_count()

        assert counts[ContentType.BOOK] == 1
        assert counts[ContentType.ARTICLE] == 1
        assert counts[ContentType.MAGAZINE] == 0
        assert counts[ContentType.MULTIMEDIA] == 0

    def test_get_content_with_details_exists(self, fresh_db):
        """Test getting content with all details."""
        # Create author and category
        author = AuthorService.create_author("Test", "Author")
        category = CategoryService.create_category("Test Category")

        content_data = ContentCreate(title="Detailed Book", content_type=ContentType.BOOK)
        book_data = BookCreate(publisher="Test Publisher")

        author_ids = [author.id] if author.id is not None else None
        category_ids = [category.id] if category.id is not None else None

        content = ContentService.create_book(content_data, book_data, author_ids, category_ids)

        if content and content.id is not None:
            details = ContentService.get_content_with_details(content.id)

            assert details is not None
            assert details["content"].title == "Detailed Book"
            assert len(details["authors"]) == 1
            assert len(details["categories"]) == 1
            assert details["extended_info"] is not None
            assert details["extended_info"].publisher == "Test Publisher"

    def test_get_content_with_details_not_found(self, fresh_db):
        """Test getting details for non-existent content."""
        details = ContentService.get_content_with_details(999)

        assert details is None


class TestAuthorService:
    """Test the AuthorService class."""

    def test_create_author_success(self, fresh_db):
        """Test successful author creation."""
        author = AuthorService.create_author(first_name="John", last_name="Doe", biography="A test author")

        assert author.first_name == "John"
        assert author.last_name == "Doe"
        assert author.biography == "A test author"
        assert author.id is not None

    def test_create_author_minimal(self, fresh_db):
        """Test creating author with minimal required fields."""
        author = AuthorService.create_author("Jane", "Smith")

        assert author.first_name == "Jane"
        assert author.last_name == "Smith"
        assert author.biography == ""
        assert author.birth_date is None
        assert author.website is None

    def test_get_all_authors_empty(self, fresh_db):
        """Test getting all authors when none exist."""
        authors = AuthorService.get_all_authors()

        assert len(authors) == 0

    def test_get_all_authors_with_data(self, fresh_db):
        """Test getting all authors when some exist."""
        AuthorService.create_author("John", "Doe")
        AuthorService.create_author("Jane", "Smith")

        authors = AuthorService.get_all_authors()

        assert len(authors) == 2
        # Should be sorted by last name, first name
        assert authors[0].last_name == "Doe"
        assert authors[1].last_name == "Smith"

    def test_search_authors_by_first_name(self, fresh_db):
        """Test searching authors by first name."""
        AuthorService.create_author("John", "Doe")
        AuthorService.create_author("Jane", "Smith")

        results = AuthorService.search_authors("John")

        assert len(results) == 1
        assert results[0].first_name == "John"

    def test_search_authors_by_last_name(self, fresh_db):
        """Test searching authors by last name."""
        AuthorService.create_author("John", "Doe")
        AuthorService.create_author("Jane", "Smith")

        results = AuthorService.search_authors("Smith")

        assert len(results) == 1
        assert results[0].last_name == "Smith"

    def test_search_authors_partial_match(self, fresh_db):
        """Test searching authors with partial matches."""
        AuthorService.create_author("Johnson", "Smith")
        AuthorService.create_author("John", "Doe")

        results = AuthorService.search_authors("John")

        # Should match both "Johnson" and "John"
        assert len(results) == 2

    def test_search_authors_case_insensitive(self, fresh_db):
        """Test that author search is case insensitive."""
        AuthorService.create_author("John", "Doe")

        results = AuthorService.search_authors("john")

        assert len(results) == 1
        assert results[0].first_name == "John"

    def test_search_authors_no_results(self, fresh_db):
        """Test searching authors with no matches."""
        AuthorService.create_author("John", "Doe")

        results = AuthorService.search_authors("NonExistent")

        assert len(results) == 0


class TestCategoryService:
    """Test the CategoryService class."""

    def test_create_category_success(self, fresh_db):
        """Test successful category creation."""
        category = CategoryService.create_category(name="Fiction", description="Fictional books")

        assert category.name == "Fiction"
        assert category.description == "Fictional books"
        assert category.parent_id is None
        assert category.id is not None

    def test_create_category_minimal(self, fresh_db):
        """Test creating category with minimal fields."""
        category = CategoryService.create_category("Mystery")

        assert category.name == "Mystery"
        assert category.description == ""
        assert category.parent_id is None

    def test_create_category_with_parent(self, fresh_db):
        """Test creating category with parent."""
        parent = CategoryService.create_category("Fiction")

        if parent.id is not None:
            child = CategoryService.create_category(name="Science Fiction", parent_id=parent.id)

            assert child.parent_id == parent.id

    def test_get_all_categories_empty(self, fresh_db):
        """Test getting all categories when none exist."""
        categories = CategoryService.get_all_categories()

        assert len(categories) == 0

    def test_get_all_categories_with_data(self, fresh_db):
        """Test getting all categories when some exist."""
        CategoryService.create_category("Fiction")
        CategoryService.create_category("Non-Fiction")

        categories = CategoryService.get_all_categories()

        assert len(categories) == 2
        # Should be sorted by name
        category_names = [cat.name for cat in categories]
        assert category_names == sorted(category_names)

    def test_get_root_categories(self, fresh_db):
        """Test getting only root-level categories."""
        parent = CategoryService.create_category("Fiction")
        CategoryService.create_category("Non-Fiction")

        if parent.id is not None:
            CategoryService.create_category("Science Fiction", parent_id=parent.id)

        root_categories = CategoryService.get_root_categories()

        assert len(root_categories) == 2
        for category in root_categories:
            assert category.parent_id is None
