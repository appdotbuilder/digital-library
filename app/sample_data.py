from datetime import datetime
import logging

from app.content_service import ContentService, AuthorService, CategoryService
from app.models import ContentCreate, BookCreate, ContentType

logger = logging.getLogger(__name__)


def create_sample_data():
    """Create sample data for the digital library."""

    try:
        # Create sample authors
        authors = [
            AuthorService.create_author(
                "Jane", "Austen", "English novelist known primarily for her six major novels.", datetime(1775, 12, 16)
            ),
            AuthorService.create_author(
                "George",
                "Orwell",
                "English novelist and journalist known for his dystopian works.",
                datetime(1903, 6, 25),
            ),
            AuthorService.create_author(
                "Agatha", "Christie", "English writer known for her detective novels.", datetime(1890, 9, 15)
            ),
            AuthorService.create_author(
                "Isaac",
                "Asimov",
                "American writer and professor of biochemistry, known for science fiction.",
                datetime(1920, 1, 2),
            ),
            AuthorService.create_author(
                "Virginia", "Woolf", "English writer and modernist pioneer.", datetime(1882, 1, 25)
            ),
        ]

        # Create sample categories
        categories = [
            CategoryService.create_category("Fiction", "Fictional literature"),
            CategoryService.create_category("Science Fiction", "Speculative fiction with futuristic concepts"),
            CategoryService.create_category("Mystery", "Detective and mystery novels"),
            CategoryService.create_category("Classic Literature", "Timeless literary works"),
            CategoryService.create_category("Dystopian", "Dark future societies"),
            CategoryService.create_category("Romance", "Romantic literature"),
            CategoryService.create_category("Modernist", "Modernist literary movement"),
        ]

        # Create sample books
        sample_books = [
            {
                "content": ContentCreate(
                    title="Pride and Prejudice",
                    description="A romantic novel that critiques the British landed gentry at the end of the 18th century.",
                    content_type=ContentType.BOOK,
                    language="English",
                    publication_date=datetime(1813, 1, 28),
                    tags=["romance", "social commentary", "british literature"],
                ),
                "book": BookCreate(publisher="T. Egerton", page_count=432, edition="First Edition", format="paperback"),
                "author_names": ["Jane Austen"],
                "category_names": ["Fiction", "Romance", "Classic Literature"],
            },
            {
                "content": ContentCreate(
                    title="1984",
                    description="A dystopian social science fiction novel about totalitarian control and surveillance.",
                    content_type=ContentType.BOOK,
                    language="English",
                    publication_date=datetime(1949, 6, 8),
                    tags=["dystopian", "totalitarianism", "surveillance", "political fiction"],
                ),
                "book": BookCreate(
                    publisher="Secker & Warburg", page_count=328, edition="First Edition", format="hardcover"
                ),
                "author_names": ["George Orwell"],
                "category_names": ["Fiction", "Dystopian", "Science Fiction"],
            },
            {
                "content": ContentCreate(
                    title="Murder on the Orient Express",
                    description="A detective novel featuring Hercule Poirot solving a murder on a luxury train.",
                    content_type=ContentType.BOOK,
                    language="English",
                    publication_date=datetime(1934, 1, 1),
                    tags=["detective", "murder mystery", "hercule poirot"],
                ),
                "book": BookCreate(
                    publisher="Collins Crime Club", page_count=256, edition="First Edition", format="paperback"
                ),
                "author_names": ["Agatha Christie"],
                "category_names": ["Fiction", "Mystery"],
            },
            {
                "content": ContentCreate(
                    title="Foundation",
                    description="The first novel in the Foundation series, exploring a galactic empire's decline and renewal.",
                    content_type=ContentType.BOOK,
                    language="English",
                    publication_date=datetime(1951, 5, 1),
                    tags=["space opera", "galactic empire", "psychohistory", "science fiction"],
                ),
                "book": BookCreate(
                    publisher="Gnome Press", page_count=244, edition="First Edition", format="hardcover"
                ),
                "author_names": ["Isaac Asimov"],
                "category_names": ["Science Fiction", "Fiction"],
            },
            {
                "content": ContentCreate(
                    title="To the Lighthouse",
                    description="A modernist novel exploring the Ramsay family's experiences over a decade.",
                    content_type=ContentType.BOOK,
                    language="English",
                    publication_date=datetime(1927, 5, 5),
                    tags=["modernist", "stream of consciousness", "family drama"],
                ),
                "book": BookCreate(
                    publisher="Hogarth Press", page_count=209, edition="First Edition", format="hardcover"
                ),
                "author_names": ["Virginia Woolf"],
                "category_names": ["Fiction", "Modernist", "Classic Literature"],
            },
            {
                "content": ContentCreate(
                    title="Animal Farm",
                    description="An allegorical novella about farm animals who rebel against their human farmer.",
                    content_type=ContentType.BOOK,
                    language="English",
                    publication_date=datetime(1945, 8, 17),
                    tags=["allegory", "political satire", "fable"],
                ),
                "book": BookCreate(
                    publisher="Secker & Warburg", page_count=112, edition="First Edition", format="paperback"
                ),
                "author_names": ["George Orwell"],
                "category_names": ["Fiction", "Political Satire"],
            },
            {
                "content": ContentCreate(
                    title="The Robots of Dawn",
                    description="A science fiction mystery novel featuring detective Elijah Baley and robot R. Daneel.",
                    content_type=ContentType.BOOK,
                    language="English",
                    publication_date=datetime(1983, 10, 1),
                    tags=["robots", "detective story", "future society"],
                ),
                "book": BookCreate(publisher="Doubleday", page_count=384, edition="First Edition", format="hardcover"),
                "author_names": ["Isaac Asimov"],
                "category_names": ["Science Fiction", "Mystery", "Fiction"],
            },
            {
                "content": ContentCreate(
                    title="Emma",
                    description="A novel about Emma Woodhouse, a young woman who meddles in the romantic lives of others.",
                    content_type=ContentType.BOOK,
                    language="English",
                    publication_date=datetime(1815, 12, 23),
                    tags=["romance", "matchmaking", "social comedy"],
                ),
                "book": BookCreate(
                    publisher="John Murray", page_count=474, edition="First Edition", format="paperback"
                ),
                "author_names": ["Jane Austen"],
                "category_names": ["Fiction", "Romance", "Classic Literature"],
            },
        ]

        # Create the books with relationships
        created_books = []
        for book_data in sample_books:
            # Find author IDs
            author_ids = []
            for author_name in book_data["author_names"]:
                for author in authors:
                    full_name = f"{author.first_name} {author.last_name}"
                    if full_name == author_name and author.id is not None:
                        author_ids.append(author.id)
                        break

            # Find category IDs
            category_ids = []
            for category_name in book_data["category_names"]:
                for category in categories:
                    if category.name == category_name and category.id is not None:
                        category_ids.append(category.id)
                        break

            # Create the book
            created_book = ContentService.create_book(
                content_data=book_data["content"],
                book_data=book_data["book"],
                author_ids=author_ids if author_ids else None,
                category_ids=category_ids if category_ids else None,
            )

            if created_book:
                created_books.append(created_book)

        logger.info("Created sample data:")
        logger.info(f"- {len(authors)} authors")
        logger.info(f"- {len(categories)} categories")
        logger.info(f"- {len(created_books)} books")

        return {"authors": authors, "categories": categories, "books": created_books}

    except Exception as e:
        logger.error(f"Error creating sample data: {str(e)}")
        return None


def has_sample_data() -> bool:
    """Check if sample data already exists."""
    try:
        books = ContentService.get_books(limit=1)
        return len(books) > 0
    except Exception as e:
        logger.error(f"Error checking for sample data: {str(e)}")
        return False


def initialize_sample_data_if_needed():
    """Initialize sample data if database is empty."""
    if not has_sample_data():
        logger.info("No existing data found. Creating sample data...")
        create_sample_data()
    else:
        logger.info("Sample data already exists.")
