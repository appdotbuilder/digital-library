from nicegui import ui
from typing import List
import logging

from app.content_service import ContentService
from app.models import Content, ContentType, ContentStatus

logger = logging.getLogger(__name__)


def create():
    """Create the digital library application pages."""

    # Apply modern theme
    ui.colors(
        primary="#2563eb",
        secondary="#64748b",
        accent="#10b981",
        positive="#10b981",
        negative="#ef4444",
        warning="#f59e0b",
        info="#3b82f6",
    )

    @ui.page("/")
    def home_page():
        """Digital library home page with search and book display."""

        # Header
        with ui.header().classes("bg-primary text-white shadow-lg"):
            with ui.row().classes("w-full items-center justify-between p-4"):
                ui.label("📚 Digital Library").classes("text-2xl font-bold")

                # Navigation
                with ui.row().classes("gap-4"):
                    ui.link("Home", "/").classes("text-white hover:text-blue-200")
                    ui.link("Browse", "/browse").classes("text-white hover:text-blue-200")
                    ui.link("Add Content", "/add-content").classes("text-white hover:text-blue-200")
                    ui.link("Authors", "/manage-authors").classes("text-white hover:text-blue-200")
                    ui.link("Categories", "/manage-categories").classes("text-white hover:text-blue-200")

        # Main content
        with ui.column().classes("w-full max-w-6xl mx-auto p-6 gap-6"):
            # Welcome section
            with ui.card().classes("w-full p-6 bg-gradient-to-r from-blue-50 to-indigo-100"):
                ui.label("Welcome to Your Digital Library").classes("text-3xl font-bold text-gray-800 mb-2")
                ui.label("Discover and explore books, articles, magazines, and multimedia content").classes(
                    "text-lg text-gray-600"
                )

            # Search section
            with ui.card().classes("w-full p-6 shadow-lg"):
                ui.label("Search Library").classes("text-xl font-semibold text-gray-800 mb-4")

                with ui.row().classes("w-full gap-4 items-end"):
                    search_input = ui.input(placeholder="Search for books, articles, magazines...").classes("flex-1")

                    content_type_select = ui.select(
                        label="Content Type",
                        options={
                            "all": "All Types",
                            ContentType.BOOK: "Books",
                            ContentType.ARTICLE: "Articles",
                            ContentType.MAGAZINE: "Magazines",
                            ContentType.MULTIMEDIA: "Multimedia",
                        },
                        value="all",
                    ).classes("w-40")

                    ui.button("Search", icon="search", on_click=lambda: perform_search()).classes(
                        "bg-primary text-white"
                    )

            # Results section
            results_container = ui.column().classes("w-full gap-4")

            # Statistics section
            stats_container = ui.row().classes("w-full gap-4 mb-6")

            def load_statistics():
                """Load and display library statistics."""
                try:
                    stats_container.clear()
                    counts = ContentService.get_available_content_count()

                    with stats_container:
                        create_stat_card("📚 Books", str(counts.get(ContentType.BOOK, 0)), "Available for checkout")
                        create_stat_card(
                            "📄 Articles", str(counts.get(ContentType.ARTICLE, 0)), "Research papers & articles"
                        )
                        create_stat_card("📰 Magazines", str(counts.get(ContentType.MAGAZINE, 0)), "Latest issues")
                        create_stat_card(
                            "🎬 Multimedia", str(counts.get(ContentType.MULTIMEDIA, 0)), "Videos & audio content"
                        )

                except Exception as e:
                    logger.error(f"Error loading statistics: {str(e)}")
                    with stats_container:
                        ui.label(f"Error loading statistics: {str(e)}").classes("text-red-500")

            def create_stat_card(title: str, value: str, subtitle: str):
                """Create a statistics card."""
                with ui.card().classes("p-4 text-center bg-white shadow-md hover:shadow-lg transition-shadow flex-1"):
                    ui.label(title).classes("text-lg font-semibold text-gray-700")
                    ui.label(value).classes("text-3xl font-bold text-primary mt-2")
                    ui.label(subtitle).classes("text-sm text-gray-500 mt-1")

            def perform_search():
                """Perform content search and display results."""
                try:
                    query = search_input.value or ""
                    content_type = None if content_type_select.value == "all" else content_type_select.value

                    results = ContentService.search_content(
                        query=query, content_type=content_type, available_only=True, limit=20
                    )

                    display_search_results(results, query)

                except Exception as e:
                    logger.error(f"Search error: {str(e)}")
                    ui.notify(f"Search error: {str(e)}", type="negative")

            def display_search_results(results: List[Content], query: str):
                """Display search results."""
                results_container.clear()

                with results_container:
                    # Results header
                    if query:
                        ui.label(f'Search Results for "{query}" ({len(results)} items found)').classes(
                            "text-xl font-semibold text-gray-800 mb-4"
                        )
                    else:
                        ui.label(f"Latest Content ({len(results)} items)").classes(
                            "text-xl font-semibold text-gray-800 mb-4"
                        )

                    if not results:
                        with ui.card().classes("p-6 text-center"):
                            ui.icon("search_off", size="48px").classes("text-gray-400 mb-4")
                            ui.label("No content found").classes("text-lg text-gray-500")
                            ui.label("Try adjusting your search terms or browse all content").classes("text-gray-400")
                        return

                    # Results grid
                    with ui.grid(columns=3).classes("w-full gap-6"):
                        for content in results:
                            create_content_card(content)

            def create_content_card(content: Content):
                """Create a content display card."""
                with ui.card().classes("p-4 shadow-lg hover:shadow-xl transition-shadow cursor-pointer"):
                    # Content type badge
                    type_colors = {
                        ContentType.BOOK: "bg-blue-100 text-blue-800",
                        ContentType.ARTICLE: "bg-green-100 text-green-800",
                        ContentType.MAGAZINE: "bg-purple-100 text-purple-800",
                        ContentType.MULTIMEDIA: "bg-orange-100 text-orange-800",
                    }

                    with ui.row().classes("justify-between items-start mb-3"):
                        ui.label(content.content_type.value.title()).classes(
                            f"px-2 py-1 rounded-full text-xs font-medium {type_colors.get(content.content_type, 'bg-gray-100 text-gray-800')}"
                        )

                        status_color = "text-green-500" if content.status == ContentStatus.AVAILABLE else "text-red-500"
                        ui.label(content.status.value.replace("_", " ").title()).classes(f"text-xs {status_color}")

                    # Title and description
                    ui.label(content.title).classes("text-lg font-semibold text-gray-800 mb-2 line-clamp-2")

                    if content.description:
                        ui.label(content.description).classes("text-sm text-gray-600 mb-3 line-clamp-3")

                    # Metadata
                    with ui.column().classes("gap-1"):
                        if content.publication_date:
                            ui.label(f"Published: {content.publication_date.strftime('%Y-%m-%d')}").classes(
                                "text-xs text-gray-500"
                            )

                        if content.language and content.language != "English":
                            ui.label(f"Language: {content.language}").classes("text-xs text-gray-500")

                        if content.tags:
                            tags_str = ", ".join(content.tags[:3])  # Show first 3 tags
                            if len(content.tags) > 3:
                                tags_str += f" +{len(content.tags) - 3} more"
                            ui.label(f"Tags: {tags_str}").classes("text-xs text-gray-500")

                    # Action button
                    if content.id is not None:
                        ui.button(
                            "View Details",
                            on_click=lambda content_id=content.id: ui.navigate.to(f"/content/{content_id}"),
                        ).classes("w-full mt-3 bg-primary text-white")

            def load_initial_content():
                """Load initial content (recent books) on page load."""
                try:
                    recent_books = ContentService.get_books(limit=12)
                    display_search_results(recent_books, "")
                except Exception as e:
                    logger.error(f"Error loading content: {str(e)}")
                    with results_container:
                        ui.label(f"Error loading content: {str(e)}").classes("text-red-500")

            # Load initial data
            load_statistics()
            load_initial_content()

            # Allow search on Enter key
            search_input.on("keydown.enter", perform_search)

    @ui.page("/content/{content_id}")
    def content_detail_page(content_id: int):
        """Detailed view of a specific content item."""

        # Header
        with ui.header().classes("bg-primary text-white shadow-lg"):
            with ui.row().classes("w-full items-center p-4"):
                ui.button(icon="arrow_back", on_click=lambda: ui.navigate.back()).props("flat").classes(
                    "text-white mr-4"
                )
                ui.label("Content Details").classes("text-xl font-bold")

        with ui.column().classes("w-full max-w-4xl mx-auto p-6 gap-6"):
            content_container = ui.column().classes("w-full")

            def load_content_details():
                """Load and display detailed content information."""
                try:
                    details = ContentService.get_content_with_details(content_id)
                    if details is None:
                        with content_container:
                            ui.label("Content not found").classes("text-xl text-red-500")
                        return

                    content = details["content"]
                    authors = details["authors"]
                    categories = details["categories"]
                    extended_info = details["extended_info"]

                    content_container.clear()

                    with content_container:
                        # Content header
                        with ui.card().classes("w-full p-6"):
                            with ui.row().classes("justify-between items-start mb-4"):
                                ui.label(content.title).classes("text-3xl font-bold text-gray-800")

                                status_colors = {
                                    ContentStatus.AVAILABLE: "bg-green-100 text-green-800",
                                    ContentStatus.CHECKED_OUT: "bg-red-100 text-red-800",
                                    ContentStatus.RESERVED: "bg-yellow-100 text-yellow-800",
                                    ContentStatus.MAINTENANCE: "bg-gray-100 text-gray-800",
                                }
                                ui.label(content.status.value.replace("_", " ").title()).classes(
                                    f"px-3 py-1 rounded-full text-sm font-medium {status_colors.get(content.status, 'bg-gray-100 text-gray-800')}"
                                )

                            # Content type and basic info
                            with ui.row().classes("gap-4 mb-4"):
                                ui.label(f"Type: {content.content_type.value.title()}").classes("text-lg text-gray-600")
                                if content.language:
                                    ui.label(f"Language: {content.language}").classes("text-lg text-gray-600")
                                if content.publication_date:
                                    ui.label(f"Published: {content.publication_date.strftime('%Y-%m-%d')}").classes(
                                        "text-lg text-gray-600"
                                    )

                            # Description
                            if content.description:
                                ui.label("Description").classes("text-xl font-semibold text-gray-800 mb-2")
                                ui.label(content.description).classes("text-gray-700 mb-4")

                            # Authors
                            if authors:
                                ui.label("Authors").classes("text-xl font-semibold text-gray-800 mb-2")
                                with ui.row().classes("gap-2 flex-wrap mb-4"):
                                    for author in authors:
                                        ui.label(f"{author.first_name} {author.last_name}").classes(
                                            "px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm"
                                        )

                            # Categories
                            if categories:
                                ui.label("Categories").classes("text-xl font-semibold text-gray-800 mb-2")
                                with ui.row().classes("gap-2 flex-wrap mb-4"):
                                    for category in categories:
                                        ui.label(category.name).classes(
                                            "px-3 py-1 bg-purple-50 text-purple-700 rounded-full text-sm"
                                        )

                            # Tags
                            if content.tags:
                                ui.label("Tags").classes("text-xl font-semibold text-gray-800 mb-2")
                                with ui.row().classes("gap-2 flex-wrap mb-4"):
                                    for tag in content.tags:
                                        ui.label(tag).classes("px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm")

                        # Extended information based on content type
                        if extended_info:
                            with ui.card().classes("w-full p-6"):
                                ui.label(f"{content.content_type.value.title()} Details").classes(
                                    "text-xl font-semibold text-gray-800 mb-4"
                                )

                                match content.content_type:
                                    case ContentType.BOOK:
                                        display_book_details(extended_info)
                                    case ContentType.ARTICLE:
                                        display_article_details(extended_info)
                                    case ContentType.MAGAZINE:
                                        display_magazine_details(extended_info)
                                    case ContentType.MULTIMEDIA:
                                        display_multimedia_details(extended_info)

                        # Actions
                        with ui.card().classes("w-full p-6"):
                            ui.label("Actions").classes("text-xl font-semibold text-gray-800 mb-4")
                            with ui.row().classes("gap-4"):
                                if content.status == ContentStatus.AVAILABLE:
                                    ui.button("Check Out", icon="bookmark_add").classes("bg-primary text-white")
                                    ui.button("Reserve", icon="schedule").classes("bg-secondary text-white")
                                ui.button("Add Review", icon="rate_review").classes("bg-accent text-white")

                except Exception as e:
                    logger.error(f"Error loading content details: {str(e)}")
                    with content_container:
                        ui.label(f"Error loading content details: {str(e)}").classes("text-red-500 text-xl")

            def display_book_details(book):
                """Display book-specific details."""
                details = []
                if book.publisher:
                    details.append(f"Publisher: {book.publisher}")
                if book.page_count:
                    details.append(f"Pages: {book.page_count}")
                if book.edition:
                    details.append(f"Edition: {book.edition}")
                if book.format:
                    details.append(f"Format: {book.format.title()}")

                for detail in details:
                    ui.label(detail).classes("text-gray-700 mb-1")

            def display_article_details(article):
                """Display article-specific details."""
                details = []
                if article.journal_name:
                    details.append(f"Journal: {article.journal_name}")
                if article.volume:
                    details.append(f"Volume: {article.volume}")
                if article.issue:
                    details.append(f"Issue: {article.issue}")
                if article.page_range:
                    details.append(f"Pages: {article.page_range}")
                if article.doi:
                    details.append(f"DOI: {article.doi}")

                for detail in details:
                    ui.label(detail).classes("text-gray-700 mb-1")

            def display_magazine_details(magazine):
                """Display magazine-specific details."""
                details = []
                if magazine.issue_number:
                    details.append(f"Issue: {magazine.issue_number}")
                if magazine.frequency:
                    details.append(f"Frequency: {magazine.frequency.title()}")
                if magazine.publisher:
                    details.append(f"Publisher: {magazine.publisher}")

                for detail in details:
                    ui.label(detail).classes("text-gray-700 mb-1")

            def display_multimedia_details(multimedia):
                """Display multimedia-specific details."""
                details = []
                if multimedia.media_type:
                    details.append(f"Media Type: {multimedia.media_type.title()}")
                if multimedia.duration_minutes:
                    hours = multimedia.duration_minutes // 60
                    minutes = multimedia.duration_minutes % 60
                    if hours > 0:
                        details.append(f"Duration: {hours}h {minutes}m")
                    else:
                        details.append(f"Duration: {minutes}m")
                if multimedia.file_format:
                    details.append(f"Format: {multimedia.file_format.upper()}")
                if multimedia.file_size_mb:
                    details.append(f"Size: {multimedia.file_size_mb} MB")

                for detail in details:
                    ui.label(detail).classes("text-gray-700 mb-1")

            # Load content details on page load
            load_content_details()

    @ui.page("/browse")
    def browse_page():
        """Browse all content with filters."""

        # Header
        with ui.header().classes("bg-primary text-white shadow-lg"):
            with ui.row().classes("w-full items-center p-4"):
                ui.button(icon="arrow_back", on_click=lambda: ui.navigate.to("/")).props("flat").classes(
                    "text-white mr-4"
                )
                ui.label("Browse Library").classes("text-xl font-bold")

        with ui.column().classes("w-full max-w-6xl mx-auto p-6 gap-6"):
            # Filters
            with ui.card().classes("w-full p-4"):
                ui.label("Filters").classes("text-lg font-semibold mb-4")

                with ui.row().classes("gap-4 items-end"):
                    content_type_filter = ui.select(
                        label="Content Type",
                        options={
                            "all": "All Types",
                            ContentType.BOOK: "Books",
                            ContentType.ARTICLE: "Articles",
                            ContentType.MAGAZINE: "Magazines",
                            ContentType.MULTIMEDIA: "Multimedia",
                        },
                        value="all",
                    ).classes("w-48")

                    status_filter = ui.select(
                        label="Status", options={"available": "Available Only", "all": "All Status"}, value="available"
                    ).classes("w-48")

                    ui.button("Apply Filters", icon="filter_alt", on_click=lambda: apply_filters()).classes(
                        "bg-primary text-white"
                    )

            # Results
            browse_results = ui.column().classes("w-full gap-4")

            def apply_filters():
                """Apply filters and display results."""
                try:
                    content_type = None if content_type_filter.value == "all" else content_type_filter.value
                    available_only = status_filter.value == "available"

                    results = ContentService.search_content(
                        query="", content_type=content_type, available_only=available_only, limit=50
                    )

                    browse_results.clear()

                    with browse_results:
                        ui.label(f"Found {len(results)} items").classes("text-lg font-semibold text-gray-800 mb-4")

                        if results:
                            with ui.grid(columns=3).classes("w-full gap-6"):
                                for content in results:
                                    create_content_card(content)
                        else:
                            with ui.card().classes("p-6 text-center"):
                                ui.label("No content found with current filters").classes("text-lg text-gray-500")

                except Exception as e:
                    logger.error(f"Filter error: {str(e)}")
                    ui.notify(f"Filter error: {str(e)}", type="negative")

            # Load initial browse results
            apply_filters()

    def create_content_card(content: Content):
        """Create a content display card (shared function)."""
        with ui.card().classes("p-4 shadow-lg hover:shadow-xl transition-shadow cursor-pointer"):
            # Content type badge
            type_colors = {
                ContentType.BOOK: "bg-blue-100 text-blue-800",
                ContentType.ARTICLE: "bg-green-100 text-green-800",
                ContentType.MAGAZINE: "bg-purple-100 text-purple-800",
                ContentType.MULTIMEDIA: "bg-orange-100 text-orange-800",
            }

            with ui.row().classes("justify-between items-start mb-3"):
                ui.label(content.content_type.value.title()).classes(
                    f"px-2 py-1 rounded-full text-xs font-medium {type_colors.get(content.content_type, 'bg-gray-100 text-gray-800')}"
                )

                status_color = "text-green-500" if content.status == ContentStatus.AVAILABLE else "text-red-500"
                ui.label(content.status.value.replace("_", " ").title()).classes(f"text-xs {status_color}")

            # Title and description
            ui.label(content.title).classes("text-lg font-semibold text-gray-800 mb-2 line-clamp-2")

            if content.description:
                ui.label(content.description).classes("text-sm text-gray-600 mb-3 line-clamp-3")

            # Metadata
            with ui.column().classes("gap-1"):
                if content.publication_date:
                    ui.label(f"Published: {content.publication_date.strftime('%Y-%m-%d')}").classes(
                        "text-xs text-gray-500"
                    )

                if content.language and content.language != "English":
                    ui.label(f"Language: {content.language}").classes("text-xs text-gray-500")

                if content.tags:
                    tags_str = ", ".join(content.tags[:3])
                    if len(content.tags) > 3:
                        tags_str += f" +{len(content.tags) - 3} more"
                    ui.label(f"Tags: {tags_str}").classes("text-xs text-gray-500")

            # Action button
            if content.id is not None:
                ui.button(
                    "View Details", on_click=lambda content_id=content.id: ui.navigate.to(f"/content/{content_id}")
                ).classes("w-full mt-3 bg-primary text-white")
