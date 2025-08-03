from typing import List, Optional, Dict, Any
from sqlmodel import select, or_, and_, func, col
from datetime import datetime, timedelta
import logging

from app.database import get_session
from app.models import (
    Content,
    Book,
    Article,
    Magazine,
    Multimedia,
    Author,
    Category,
    ContentType,
    ContentStatus,
    ContentCreate,
    BookCreate,
    ContentAuthor,
    ContentCategory,
)

logger = logging.getLogger(__name__)


class ContentService:
    """Service layer for content management operations."""

    @staticmethod
    def search_content(
        query: str = "", content_type: Optional[ContentType] = None, available_only: bool = True, limit: int = 50
    ) -> List[Content]:
        """Search content by title, description, or tags."""
        with get_session() as session:
            stmt = select(Content)

            # Apply search filter
            if query:
                search_filter = or_(
                    col(Content.title).ilike(f"%{query}%"), col(Content.description).ilike(f"%{query}%")
                )
                stmt = stmt.where(search_filter)

            # Apply content type filter
            if content_type is not None:
                stmt = stmt.where(Content.content_type == content_type)

            # Filter by availability
            if available_only:
                stmt = stmt.where(Content.status == ContentStatus.AVAILABLE)

            # Order by created_at descending
            stmt = stmt.order_by(col(Content.created_at).desc())

            stmt = stmt.limit(limit)
            return list(session.exec(stmt))

    @staticmethod
    def get_content_by_id(content_id: int) -> Optional[Content]:
        """Get content item by ID."""
        with get_session() as session:
            return session.get(Content, content_id)

    @staticmethod
    def get_books(limit: int = 20) -> List[Content]:
        """Get all books with their extended information."""
        with get_session() as session:
            stmt = (
                select(Content)
                .where(Content.content_type == ContentType.BOOK)
                .order_by(col(Content.created_at).desc())
                .limit(limit)
            )
            return list(session.exec(stmt))

    @staticmethod
    def get_content_with_details(content_id: int) -> Optional[Dict[str, Any]]:
        """Get content with all related details (book/article/magazine/multimedia)."""
        with get_session() as session:
            content = session.get(Content, content_id)
            if content is None:
                return None

            result = {
                "content": content,
                "authors": ContentService.get_content_authors(content_id),
                "categories": ContentService.get_content_categories(content_id),
                "extended_info": None,
            }

            # Get type-specific information
            match content.content_type:
                case ContentType.BOOK:
                    stmt = select(Book).where(Book.content_id == content_id)
                    result["extended_info"] = session.exec(stmt).first()
                case ContentType.ARTICLE:
                    stmt = select(Article).where(Article.content_id == content_id)
                    result["extended_info"] = session.exec(stmt).first()
                case ContentType.MAGAZINE:
                    stmt = select(Magazine).where(Magazine.content_id == content_id)
                    result["extended_info"] = session.exec(stmt).first()
                case ContentType.MULTIMEDIA:
                    stmt = select(Multimedia).where(Multimedia.content_id == content_id)
                    result["extended_info"] = session.exec(stmt).first()

            return result

    @staticmethod
    def get_content_authors(content_id: int) -> List[Author]:
        """Get all authors for a content item."""
        with get_session() as session:
            stmt = select(Author).join(ContentAuthor).where(ContentAuthor.content_id == content_id)
            return list(session.exec(stmt))

    @staticmethod
    def get_content_categories(content_id: int) -> List[Category]:
        """Get all categories for a content item."""
        with get_session() as session:
            stmt = select(Category).join(ContentCategory).where(ContentCategory.content_id == content_id)
            return list(session.exec(stmt))

    @staticmethod
    def create_book(
        content_data: ContentCreate,
        book_data: BookCreate,
        author_ids: Optional[List[int]] = None,
        category_ids: Optional[List[int]] = None,
    ) -> Optional[Content]:
        """Create a new book with all related information."""
        with get_session() as session:
            try:
                # Create content
                content = Content(**content_data.model_dump())
                content.content_type = ContentType.BOOK
                session.add(content)
                session.commit()
                session.refresh(content)

                if content.id is None:
                    return None

                # Create book-specific information
                book = Book(**book_data.model_dump(), content_id=content.id)
                session.add(book)

                # Add author relationships
                if author_ids:
                    for author_id in author_ids:
                        content_author = ContentAuthor(content_id=content.id, author_id=author_id)
                        session.add(content_author)

                # Add category relationships
                if category_ids:
                    for category_id in category_ids:
                        content_category = ContentCategory(content_id=content.id, category_id=category_id)
                        session.add(content_category)

                session.commit()
                session.refresh(content)
                return content

            except Exception as e:
                session.rollback()
                raise e

    @staticmethod
    def update_content_status(content_id: int, status: ContentStatus) -> bool:
        """Update content status."""
        with get_session() as session:
            content = session.get(Content, content_id)
            if content is None:
                return False

            content.status = status
            content.updated_at = datetime.utcnow()
            session.add(content)
            session.commit()
            return True

    @staticmethod
    def get_available_content_count() -> Dict[ContentType, int]:
        """Get count of available content by type."""
        with get_session() as session:
            counts = {}
            for content_type in ContentType:
                stmt = select(func.count(col(Content.id))).where(
                    and_(Content.content_type == content_type, Content.status == ContentStatus.AVAILABLE)
                )
                count = session.exec(stmt).first()
                counts[content_type] = count or 0
            return counts

    @staticmethod
    def get_recent_content(days: int = 30, limit: int = 10) -> List[Content]:
        """Get recently added content."""
        with get_session() as session:
            cutoff_date = datetime.utcnow().replace(microsecond=0) - timedelta(days=days)
            stmt = (
                select(Content)
                .where(Content.created_at >= cutoff_date)
                .order_by(col(Content.created_at).desc())
                .limit(limit)
            )
            return list(session.exec(stmt))


class AuthorService:
    """Service layer for author management."""

    @staticmethod
    def get_all_authors() -> List[Author]:
        """Get all authors."""
        with get_session() as session:
            stmt = select(Author).order_by(Author.last_name, Author.first_name)
            return list(session.exec(stmt))

    @staticmethod
    def search_authors(query: str) -> List[Author]:
        """Search authors by name."""
        with get_session() as session:
            stmt = (
                select(Author)
                .where(or_(col(Author.first_name).ilike(f"%{query}%"), col(Author.last_name).ilike(f"%{query}%")))
                .order_by(Author.last_name, Author.first_name)
            )
            return list(session.exec(stmt))

    @staticmethod
    def create_author(
        first_name: str,
        last_name: str,
        biography: str = "",
        birth_date: Optional[datetime] = None,
        website: Optional[str] = None,
    ) -> Author:
        """Create a new author."""
        with get_session() as session:
            author = Author(
                first_name=first_name, last_name=last_name, biography=biography, birth_date=birth_date, website=website
            )
            session.add(author)
            session.commit()
            session.refresh(author)
            return author


class CategoryService:
    """Service layer for category management."""

    @staticmethod
    def get_all_categories() -> List[Category]:
        """Get all categories."""
        with get_session() as session:
            stmt = select(Category).order_by(Category.name)
            return list(session.exec(stmt))

    @staticmethod
    def get_root_categories() -> List[Category]:
        """Get top-level categories (no parent)."""
        with get_session() as session:
            stmt = select(Category).where(col(Category.parent_id).is_(None)).order_by(Category.name)
            return list(session.exec(stmt))

    @staticmethod
    def create_category(name: str, description: str = "", parent_id: Optional[int] = None) -> Category:
        """Create a new category."""
        with get_session() as session:
            category = Category(name=name, description=description, parent_id=parent_id)
            session.add(category)
            session.commit()
            session.refresh(category)
            return category
