from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
import logging
import re
import requests
import time

# Set up basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- App-specific imports ---
from app.core.database import SessionLocal
from app.models.regulation import Regulation
from app.scraper import BPKRegulationScraper

# --- Constants ---
BASE_URL = "https://peraturan.bpk.go.id"
BASE_LIST_URL = "https://peraturan.bpk.go.id/Search?tema=49"


def get_last_page_number(session: requests.Session, url: str) -> int | None:
    """
    Finds the last page number from the pagination control on the search results page.
    """
    logging.info("Attempting to dynamically find the last page number...")
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")

        # Find the link with the text "Last"
        last_page_link = soup.find(
            "a", class_="page-link", string=re.compile(r"\s*Last\s*")
        )

        if not last_page_link:
            logging.warning(
                "Could not find the 'Last' page link. Scraping may be incomplete."
            )
            return None

        href = last_page_link.get("href")
        if not href:
            return None

        match = re.search(r"p=(\d+)", href)
        if match:
            last_page = int(match.group(1))
            logging.info(f"Successfully found the last page: {last_page}")
            return last_page

    except requests.RequestException as e:
        logging.error(f"Could not fetch first page to determine pagination: {e}")

    return None


def get_all_regulation_links() -> list[str]:
    """
    Fetches all regulation links by dynamically finding the last page and iterating through all pages.
    """
    all_links = set()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    # Use a session for all requests in this function
    with requests.Session() as session:
        session.headers.update(headers)

        # Dynamically determine the total number of pages
        max_pages = get_last_page_number(session, BASE_LIST_URL)
        if not max_pages:
            logging.error("Could not determine total pages. Aborting link scraping.")
            return []

        for page_num in range(1, max_pages + 1):
            page_url = f"{BASE_LIST_URL}&p={page_num}"
            logging.info(f"Scraping page {page_num}/{max_pages}: {page_url}")

            try:
                response = session.get(page_url, timeout=30)
                response.raise_for_status()
            except requests.RequestException as e:
                logging.error(f"Could not fetch page {page_num}: {e}. Skipping.")
                continue

            soup = BeautifulSoup(response.content, "lxml")
            link_elements = soup.select('a[href^="/Details/"]:not(.text-danger)')

            found_on_page = 0
            for link_element in link_elements:
                relative_path = link_element.get("href")
                if relative_path:
                    full_url = BASE_URL + relative_path
                    if full_url not in all_links:
                        all_links.add(full_url)
                        found_on_page += 1

            logging.info(f"Found {found_on_page} new links on this page.")
            time.sleep(0.5)

    logging.info(
        f"Finished scraping all pages. Found a total of {len(all_links)} unique regulation links."
    )
    return list(all_links)


def populate_database():
    # This function remains unchanged
    db: Session = SessionLocal()
    scraper = BPKRegulationScraper()
    regulation_links = get_all_regulation_links()
    total_links = len(regulation_links)
    for i, link in enumerate(regulation_links):
        logging.info(f"Processing link {i+1}/{total_links}: {link}")
        existing = (
            db.query(Regulation).filter(Regulation.link_peraturan == link).first()
        )
        if existing:
            logging.warning(f"Regulation from {link} already exists. Skipping.")
            continue
        try:
            details = scraper.scrape_regulation_detail(link)
            new_regulation = Regulation(**details)
            db.add(new_regulation)
            db.commit()
            logging.info(f"Successfully added: {details.get('nama_peraturan', 'N/A')}")
        except Exception as e:
            logging.error(f"!!! Failed to process {link}: {e}")
            db.rollback()
        finally:
            time.sleep(1)
    db.close()
    logging.info("Database population complete.")


if __name__ == "__main__":
    populate_database()
