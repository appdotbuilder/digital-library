from nicegui import ui
from datetime import datetime, date
import logging

from app.content_service import ContentService, AuthorService, CategoryService
from app.models import ContentCreate, BookCreate, ContentType

logger = logging.getLogger(__name__)


def create():
    """Create content management pages."""

    @ui.page("/add-content")
    def add_content_page():
        """Page for adding new content to the library."""

        # Header
        with ui.header().classes("bg-primary text-white shadow-lg"):
            with ui.row().classes("w-full items-center p-4"):
                ui.button(icon="arrow_back", on_click=lambda: ui.navigate.to("/")).props("flat").classes(
                    "text-white mr-4"
                )
                ui.label("Add New Content").classes("text-xl font-bold")

        with ui.column().classes("w-full max-w-4xl mx-auto p-6 gap-6"):
            # Content Type Selection
            with ui.card().classes("w-full p-6"):
                ui.label("Select Content Type").classes("text-xl font-semibold text-gray-800 mb-4")

                content_type_select = ui.select(
                    label="Content Type",
                    options={
                        ContentType.BOOK: "Book",
                        ContentType.ARTICLE: "Article",
                        ContentType.MAGAZINE: "Magazine",
                        ContentType.MULTIMEDIA: "Multimedia",
                    },
                    value=ContentType.BOOK,
                ).classes("w-full")

            # Dynamic form container
            form_container = ui.column().classes("w-full gap-6")

            def update_form():
                """Update form based on selected content type."""
                form_container.clear()

                selected_type = content_type_select.value

                match selected_type:
                    case ContentType.BOOK:
                        create_book_form()
                    case ContentType.ARTICLE:
                        create_article_form()
                    case ContentType.MAGAZINE:
                        create_magazine_form()
                    case ContentType.MULTIMEDIA:
                        create_multimedia_form()

            def create_book_form():
                """Create form for adding a book."""
                with form_container:
                    with ui.card().classes("w-full p-6"):
                        ui.label("Book Information").classes("text-xl font-semibold text-gray-800 mb-4")

                        # Basic content fields
                        title_input = ui.input("Title").classes("w-full mb-4").props("required")
                        description_input = ui.textarea("Description").classes("w-full mb-4").props("rows=4")
                        isbn_input = ui.input("ISBN").classes("w-full mb-4")
                        language_input = ui.input("Language", value="English").classes("w-full mb-4")

                        # Publication date
                        pub_date_input = ui.date("Publication Date").classes("w-full mb-4")

                        # Tags
                        tags_input = ui.input("Tags (comma-separated)").classes("w-full mb-4")

                        # Book-specific fields
                        ui.label("Book Details").classes("text-lg font-semibold text-gray-800 mb-2 mt-4")
                        publisher_input = ui.input("Publisher").classes("w-full mb-4")
                        pages_input = ui.number("Page Count", min=1).classes("w-full mb-4")
                        edition_input = ui.input("Edition").classes("w-full mb-4")
                        format_select = ui.select(
                            options=["paperback", "hardcover", "ebook", "audiobook"], value="paperback", label="Format"
                        ).classes("w-full mb-4")

                        # Author selection
                        ui.label("Authors").classes("text-lg font-semibold text-gray-800 mb-2")
                        author_container = ui.column().classes("w-full mb-4")
                        selected_authors = []

                        def load_authors():
                            """Load available authors."""
                            try:
                                authors = AuthorService.get_all_authors()
                                author_options = {
                                    author.id: f"{author.first_name} {author.last_name}"
                                    for author in authors
                                    if author.id is not None
                                }

                                author_container.clear()
                                with author_container:
                                    if author_options:
                                        author_select = ui.select(
                                            options=author_options, multiple=True, label="Select Authors"
                                        ).classes("w-full")

                                        def update_authors(e):
                                            selected_authors.clear()
                                            if e.value:
                                                selected_authors.extend(e.value)

                                        author_select.on("update:model-value", update_authors)
                                    else:
                                        ui.label("No authors found. Add authors first.").classes("text-gray-500")

                            except Exception as e:
                                logger.error(f"Error loading authors: {str(e)}")
                                with author_container:
                                    ui.label(f"Error loading authors: {str(e)}").classes("text-red-500")

                        load_authors()

                        # Category selection
                        ui.label("Categories").classes("text-lg font-semibold text-gray-800 mb-2")
                        category_container = ui.column().classes("w-full mb-6")
                        selected_categories = []

                        def load_categories():
                            """Load available categories."""
                            try:
                                categories = CategoryService.get_all_categories()
                                category_options = {
                                    category.id: category.name for category in categories if category.id is not None
                                }

                                category_container.clear()
                                with category_container:
                                    if category_options:
                                        category_select = ui.select(
                                            options=category_options, multiple=True, label="Select Categories"
                                        ).classes("w-full")

                                        def update_categories(e):
                                            selected_categories.clear()
                                            if e.value:
                                                selected_categories.extend(e.value)

                                        category_select.on("update:model-value", update_categories)
                                    else:
                                        ui.label("No categories found. Add categories first.").classes("text-gray-500")

                            except Exception as e:
                                logger.error(f"Error loading categories: {str(e)}")
                                with category_container:
                                    ui.label(f"Error loading categories: {str(e)}").classes("text-red-500")

                        load_categories()

                        # Submit button
                        with ui.row().classes("gap-4 justify-end"):
                            ui.button("Cancel", on_click=lambda: ui.navigate.to("/")).props("outline")
                            ui.button("Add Book", icon="add", on_click=lambda: submit_book()).classes(
                                "bg-primary text-white"
                            )

                        def submit_book():
                            """Submit the book form."""
                            try:
                                # Validate required fields
                                if not title_input.value:
                                    ui.notify("Title is required", type="negative")
                                    return

                                # Parse tags
                                tags = []
                                if tags_input.value:
                                    tags = [tag.strip() for tag in tags_input.value.split(",") if tag.strip()]

                                # Parse publication date
                                pub_date = None
                                if pub_date_input.value:
                                    if isinstance(pub_date_input.value, str):
                                        pub_date = datetime.fromisoformat(pub_date_input.value)
                                    elif isinstance(pub_date_input.value, date):
                                        pub_date = datetime.combine(pub_date_input.value, datetime.min.time())

                                # Create content data
                                content_data = ContentCreate(
                                    title=title_input.value,
                                    description=description_input.value or "",
                                    content_type=ContentType.BOOK,
                                    isbn=isbn_input.value,
                                    language=language_input.value or "English",
                                    publication_date=pub_date,
                                    tags=tags,
                                )

                                # Create book data
                                book_data = BookCreate(
                                    publisher=publisher_input.value or "",
                                    page_count=int(pages_input.value) if pages_input.value else None,
                                    edition=edition_input.value or "",
                                    format=format_select.value or "paperback",
                                )

                                # Create the book
                                content = ContentService.create_book(
                                    content_data=content_data,
                                    book_data=book_data,
                                    author_ids=selected_authors if selected_authors else None,
                                    category_ids=selected_categories if selected_categories else None,
                                )

                                if content and content.id is not None:
                                    ui.notify("Book added successfully!", type="positive")
                                    ui.navigate.to(f"/content/{content.id}")
                                else:
                                    ui.notify("Failed to add book", type="negative")

                            except Exception as e:
                                logger.error(f"Error adding book: {str(e)}")
                                ui.notify(f"Error adding book: {str(e)}", type="negative")

            def create_article_form():
                """Create form for adding an article."""
                with form_container:
                    with ui.card().classes("w-full p-6"):
                        ui.label("Article Information").classes("text-xl font-semibold text-gray-800 mb-4")
                        ui.label("Article form coming soon...").classes("text-gray-500")

            def create_magazine_form():
                """Create form for adding a magazine."""
                with form_container:
                    with ui.card().classes("w-full p-6"):
                        ui.label("Magazine Information").classes("text-xl font-semibold text-gray-800 mb-4")
                        ui.label("Magazine form coming soon...").classes("text-gray-500")

            def create_multimedia_form():
                """Create form for adding multimedia content."""
                with form_container:
                    with ui.card().classes("w-full p-6"):
                        ui.label("Multimedia Information").classes("text-xl font-semibold text-gray-800 mb-4")
                        ui.label("Multimedia form coming soon...").classes("text-gray-500")

            # Initial form load
            update_form()

            # Update form when content type changes
            content_type_select.on("update:model-value", lambda: update_form())

    @ui.page("/manage-authors")
    def manage_authors_page():
        """Page for managing authors."""

        # Header
        with ui.header().classes("bg-primary text-white shadow-lg"):
            with ui.row().classes("w-full items-center p-4"):
                ui.button(icon="arrow_back", on_click=lambda: ui.navigate.to("/")).props("flat").classes(
                    "text-white mr-4"
                )
                ui.label("Manage Authors").classes("text-xl font-bold")

        with ui.column().classes("w-full max-w-6xl mx-auto p-6 gap-6"):
            # Add new author form
            with ui.card().classes("w-full p-6"):
                ui.label("Add New Author").classes("text-xl font-semibold text-gray-800 mb-4")

                with ui.row().classes("gap-4 items-end"):
                    first_name_input = ui.input("First Name").classes("flex-1")
                    last_name_input = ui.input("Last Name").classes("flex-1")
                    ui.button("Add Author", icon="person_add", on_click=lambda: add_author()).classes(
                        "bg-primary text-white"
                    )

                biography_input = ui.textarea("Biography (optional)").classes("w-full mt-4").props("rows=3")

                def add_author():
                    """Add a new author."""
                    try:
                        if not first_name_input.value or not last_name_input.value:
                            ui.notify("First name and last name are required", type="negative")
                            return

                        author = AuthorService.create_author(
                            first_name=first_name_input.value,
                            last_name=last_name_input.value,
                            biography=biography_input.value or "",
                        )

                        ui.notify(f"Author {author.first_name} {author.last_name} added successfully!", type="positive")

                        # Clear form
                        first_name_input.value = ""
                        last_name_input.value = ""
                        biography_input.value = ""

                        # Refresh author list
                        load_authors()

                    except Exception as e:
                        logger.error(f"Error adding author: {str(e)}")
                        ui.notify(f"Error adding author: {str(e)}", type="negative")

            # Authors list
            authors_container = ui.column().classes("w-full gap-4")

            def load_authors():
                """Load and display all authors."""
                try:
                    authors = AuthorService.get_all_authors()

                    authors_container.clear()

                    with authors_container:
                        if authors:
                            ui.label(f"All Authors ({len(authors)})").classes(
                                "text-xl font-semibold text-gray-800 mb-4"
                            )

                            with ui.grid(columns=3).classes("w-full gap-4"):
                                for author in authors:
                                    with ui.card().classes("p-4"):
                                        ui.label(f"{author.first_name} {author.last_name}").classes(
                                            "text-lg font-semibold text-gray-800"
                                        )
                                        if author.biography:
                                            ui.label(author.biography).classes(
                                                "text-sm text-gray-600 mt-2 line-clamp-3"
                                            )
                        else:
                            ui.label("No authors found").classes("text-gray-500 text-center")

                except Exception as e:
                    logger.error(f"Error loading authors: {str(e)}")
                    with authors_container:
                        ui.label(f"Error loading authors: {str(e)}").classes("text-red-500")

            # Load initial authors
            load_authors()

    @ui.page("/manage-categories")
    def manage_categories_page():
        """Page for managing categories."""

        # Header
        with ui.header().classes("bg-primary text-white shadow-lg"):
            with ui.row().classes("w-full items-center p-4"):
                ui.button(icon="arrow_back", on_click=lambda: ui.navigate.to("/")).props("flat").classes(
                    "text-white mr-4"
                )
                ui.label("Manage Categories").classes("text-xl font-bold")

        with ui.column().classes("w-full max-w-6xl mx-auto p-6 gap-6"):
            # Add new category form
            with ui.card().classes("w-full p-6"):
                ui.label("Add New Category").classes("text-xl font-semibold text-gray-800 mb-4")

                with ui.row().classes("gap-4 items-end"):
                    name_input = ui.input("Category Name").classes("flex-1")
                    ui.button("Add Category", icon="add", on_click=lambda: add_category()).classes(
                        "bg-primary text-white"
                    )

                description_input = ui.textarea("Description (optional)").classes("w-full mt-4").props("rows=2")

                def add_category():
                    """Add a new category."""
                    try:
                        if not name_input.value:
                            ui.notify("Category name is required", type="negative")
                            return

                        category = CategoryService.create_category(
                            name=name_input.value, description=description_input.value or ""
                        )

                        ui.notify(f'Category "{category.name}" added successfully!', type="positive")

                        # Clear form
                        name_input.value = ""
                        description_input.value = ""

                        # Refresh category list
                        load_categories()

                    except Exception as e:
                        logger.error(f"Error adding category: {str(e)}")
                        ui.notify(f"Error adding category: {str(e)}", type="negative")

            # Categories list
            categories_container = ui.column().classes("w-full gap-4")

            def load_categories():
                """Load and display all categories."""
                try:
                    categories = CategoryService.get_all_categories()

                    categories_container.clear()

                    with categories_container:
                        if categories:
                            ui.label(f"All Categories ({len(categories)})").classes(
                                "text-xl font-semibold text-gray-800 mb-4"
                            )

                            with ui.grid(columns=4).classes("w-full gap-4"):
                                for category in categories:
                                    with ui.card().classes("p-4"):
                                        ui.label(category.name).classes("text-lg font-semibold text-gray-800")
                                        if category.description:
                                            ui.label(category.description).classes("text-sm text-gray-600 mt-2")
                        else:
                            ui.label("No categories found").classes("text-gray-500 text-center")

                except Exception as e:
                    logger.error(f"Error loading categories: {str(e)}")
                    with categories_container:
                        ui.label(f"Error loading categories: {str(e)}").classes("text-red-500")

            # Load initial categories
            load_categories()
