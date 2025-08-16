import logging
from app.core.database import engine, Base

# --- IMPORTANT ---
# You must import all of your SQLAlchemy models here.
# This is how the 'Base' object learns about the tables that need to be created.
from app.models.regulation import Regulation
from app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db() -> None:
    logger.info("Creating all database tables from Base metadata...")

    # Base.metadata.create_all uses the imported models to create the tables
    Base.metadata.create_all(bind=engine)

    logger.info("Tables created successfully.")


if __name__ == "__main__":
    init_db()
