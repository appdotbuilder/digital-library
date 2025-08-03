from app.database import create_tables
from app.sample_data import initialize_sample_data_if_needed
import app.digital_library
import app.content_management


def startup() -> None:
    # this function is called before the first request
    create_tables()

    # Initialize sample data if database is empty
    initialize_sample_data_if_needed()

    # Initialize all application modules
    app.digital_library.create()
    app.content_management.create()
