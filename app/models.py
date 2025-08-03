from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from decimal import Decimal


class ContentType(str, Enum):
    """Content type enumeration for different media types."""

    BOOK = "book"
    ARTICLE = "article"
    MAGAZINE = "magazine"
    MULTIMEDIA = "multimedia"


class ContentStatus(str, Enum):
    """Status enumeration for content items."""

    AVAILABLE = "available"
    CHECKED_OUT = "checked_out"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"


# Junction tables for many-to-many relationships
class ContentAuthor(SQLModel, table=True):
    """Junction table for content-author relationships."""

    __tablename__ = "content_authors"  # type: ignore[assignment]

    content_id: int = Field(foreign_key="content.id", primary_key=True)
    author_id: int = Field(foreign_key="authors.id", primary_key=True)


class ContentCategory(SQLModel, table=True):
    """Junction table for content-category relationships."""

    __tablename__ = "content_categories"  # type: ignore[assignment]

    content_id: int = Field(foreign_key="content.id", primary_key=True)
    category_id: int = Field(foreign_key="categories.id", primary_key=True)


# User models
class User(SQLModel, table=True):
    """User model for library patrons and staff."""

    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    is_active: bool = Field(default=True)
    is_staff: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    checkouts: List["Checkout"] = Relationship(back_populates="user")
    reservations: List["Reservation"] = Relationship(back_populates="user")
    reviews: List["Review"] = Relationship(back_populates="user")


# Content models
class Content(SQLModel, table=True):
    """Base content model for all library items."""

    __tablename__ = "content"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=500)
    description: str = Field(default="", max_length=2000)
    content_type: ContentType = Field(default=ContentType.BOOK)
    status: ContentStatus = Field(default=ContentStatus.AVAILABLE)
    isbn: Optional[str] = Field(default=None, max_length=20)
    language: str = Field(default="English", max_length=50)
    publication_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default=[], sa_column=Column(JSON))
    content_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Relationships
    checkouts: List["Checkout"] = Relationship(back_populates="content")
    reservations: List["Reservation"] = Relationship(back_populates="content")
    reviews: List["Review"] = Relationship(back_populates="content")
    book: Optional["Book"] = Relationship(back_populates="content")
    article: Optional["Article"] = Relationship(back_populates="content")
    magazine: Optional["Magazine"] = Relationship(back_populates="content")
    multimedia: Optional["Multimedia"] = Relationship(back_populates="content")


class Book(SQLModel, table=True):
    """Extended book-specific information."""

    __tablename__ = "books"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    content_id: int = Field(foreign_key="content.id", unique=True)
    page_count: Optional[int] = Field(default=None)
    publisher: str = Field(default="", max_length=200)
    edition: str = Field(default="", max_length=50)
    format: str = Field(default="paperback", max_length=50)  # paperback, hardcover, ebook, audiobook

    # Relationship
    content: Content = Relationship(back_populates="book")


class Article(SQLModel, table=True):
    """Extended article-specific information."""

    __tablename__ = "articles"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    content_id: int = Field(foreign_key="content.id", unique=True)
    journal_name: str = Field(default="", max_length=200)
    volume: Optional[str] = Field(default=None, max_length=20)
    issue: Optional[str] = Field(default=None, max_length=20)
    page_range: Optional[str] = Field(default=None, max_length=50)
    doi: Optional[str] = Field(default=None, max_length=100)

    # Relationship
    content: Content = Relationship(back_populates="article")


class Magazine(SQLModel, table=True):
    """Extended magazine-specific information."""

    __tablename__ = "magazines"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    content_id: int = Field(foreign_key="content.id", unique=True)
    issue_number: str = Field(max_length=50)
    frequency: str = Field(default="monthly", max_length=50)  # weekly, monthly, quarterly, etc.
    publisher: str = Field(default="", max_length=200)

    # Relationship
    content: Content = Relationship(back_populates="magazine")


class Multimedia(SQLModel, table=True):
    """Extended multimedia-specific information."""

    __tablename__ = "multimedia"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    content_id: int = Field(foreign_key="content.id", unique=True)
    media_type: str = Field(max_length=50)  # dvd, cd, blu-ray, digital, etc.
    duration_minutes: Optional[int] = Field(default=None)
    file_format: Optional[str] = Field(default=None, max_length=20)  # mp4, mp3, avi, etc.
    file_size_mb: Optional[Decimal] = Field(default=None, decimal_places=2)

    # Relationship
    content: Content = Relationship(back_populates="multimedia")


# Author and Category models
class Author(SQLModel, table=True):
    """Author model for content creators."""

    __tablename__ = "authors"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    biography: str = Field(default="", max_length=2000)
    birth_date: Optional[datetime] = Field(default=None)
    website: Optional[str] = Field(default=None, max_length=255)


class Category(SQLModel, table=True):
    """Category model for content classification."""

    __tablename__ = "categories"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=100)
    description: str = Field(default="", max_length=500)
    parent_id: Optional[int] = Field(default=None, foreign_key="categories.id")

    # Relationships
    parent: Optional["Category"] = Relationship(
        back_populates="children", sa_relationship_kwargs={"remote_side": "Category.id"}
    )
    children: List["Category"] = Relationship(back_populates="parent")


# Library operations models
class Checkout(SQLModel, table=True):
    """Checkout model for tracking borrowed items."""

    __tablename__ = "checkouts"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    content_id: int = Field(foreign_key="content.id")
    checkout_date: datetime = Field(default_factory=datetime.utcnow)
    due_date: datetime
    return_date: Optional[datetime] = Field(default=None)
    is_returned: bool = Field(default=False)
    fine_amount: Decimal = Field(default=Decimal("0.00"), decimal_places=2)

    # Relationships
    user: User = Relationship(back_populates="checkouts")
    content: Content = Relationship(back_populates="checkouts")


class Reservation(SQLModel, table=True):
    """Reservation model for holding items."""

    __tablename__ = "reservations"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    content_id: int = Field(foreign_key="content.id")
    reservation_date: datetime = Field(default_factory=datetime.utcnow)
    expiry_date: datetime
    is_active: bool = Field(default=True)

    # Relationships
    user: User = Relationship(back_populates="reservations")
    content: Content = Relationship(back_populates="reservations")


class Review(SQLModel, table=True):
    """Review model for user content ratings and comments."""

    __tablename__ = "reviews"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    content_id: int = Field(foreign_key="content.id")
    rating: int = Field(ge=1, le=5)  # 1-5 star rating
    comment: str = Field(default="", max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="reviews")
    content: Content = Relationship(back_populates="reviews")


# Non-persistent schemas for validation and API
class UserCreate(SQLModel, table=False):
    """Schema for creating new users."""

    email: str = Field(max_length=255)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    is_staff: bool = Field(default=False)


class UserUpdate(SQLModel, table=False):
    """Schema for updating user information."""

    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    is_active: Optional[bool] = Field(default=None)


class ContentCreate(SQLModel, table=False):
    """Schema for creating new content."""

    title: str = Field(max_length=500)
    description: str = Field(default="", max_length=2000)
    content_type: ContentType
    isbn: Optional[str] = Field(default=None, max_length=20)
    language: str = Field(default="English", max_length=50)
    publication_date: Optional[datetime] = Field(default=None)
    tags: List[str] = Field(default=[])
    content_metadata: Dict[str, Any] = Field(default={})


class ContentUpdate(SQLModel, table=False):
    """Schema for updating content information."""

    title: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[ContentStatus] = Field(default=None)
    language: Optional[str] = Field(default=None, max_length=50)
    publication_date: Optional[datetime] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    content_metadata: Optional[Dict[str, Any]] = Field(default=None)


class BookCreate(SQLModel, table=False):
    """Schema for creating book-specific information."""

    page_count: Optional[int] = Field(default=None)
    publisher: str = Field(default="", max_length=200)
    edition: str = Field(default="", max_length=50)
    format: str = Field(default="paperback", max_length=50)


class AuthorCreate(SQLModel, table=False):
    """Schema for creating new authors."""

    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    biography: str = Field(default="", max_length=2000)
    birth_date: Optional[datetime] = Field(default=None)
    website: Optional[str] = Field(default=None, max_length=255)


class CategoryCreate(SQLModel, table=False):
    """Schema for creating new categories."""

    name: str = Field(max_length=100)
    description: str = Field(default="", max_length=500)
    parent_id: Optional[int] = Field(default=None)


class CheckoutCreate(SQLModel, table=False):
    """Schema for creating new checkouts."""

    user_id: int
    content_id: int
    due_date: datetime


class ReservationCreate(SQLModel, table=False):
    """Schema for creating new reservations."""

    user_id: int
    content_id: int
    expiry_date: datetime


class ReviewCreate(SQLModel, table=False):
    """Schema for creating new reviews."""

    user_id: int
    content_id: int
    rating: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=1000)


class SearchQuery(SQLModel, table=False):
    """Schema for search queries."""

    query: str = Field(max_length=500)
    content_type: Optional[ContentType] = Field(default=None)
    category_id: Optional[int] = Field(default=None)
    author_id: Optional[int] = Field(default=None)
    language: Optional[str] = Field(default=None, max_length=50)
    available_only: bool = Field(default=True)
