"""
Scrapes a headline from The Daily Pennsylvanian website and saves it to a 
JSON file that tracks headlines over time.
"""

import os
import sys

import daily_event_monitor

import bs4
import requests
import loguru


def scrape_data_point():
    """
    Scrapes the main headline from The Daily Pennsylvanian home page.

    Returns:
        str: The headline text if found, otherwise an empty string.
    """
    headers = {
        "User-Agent": "cis3500-scraper"
    }
    req = requests.get("https://www.thedp.com", headers=headers)
    loguru.logger.info(f"Request URL: {req.url}")
    loguru.logger.info(f"Request status code: {req.status_code}")
    headlines = {
        "Featured": "",
        "News": "",
        "Sports": "",
        "Opinion": ""
    }
    if req.ok:
        soup = bs4.BeautifulSoup(req.text, "html.parser")
        
        # Example selectors below:
        # For the "Featured" section, assume the top headline is within a <section> with a unique class, e.g., "featured-section",
        # and the headline is in an <h2> element.
        featured = soup.select_one("section.featured-section h2")
        headlines["Featured"] = featured.text.strip() if featured else ""
        
        # For the "News" section, assume a section with class "news-section" holds the headline in an <h2> element.
        news = soup.select_one("section.news-section h2")
        headlines["News"] = news.text.strip() if news else ""
        
        # For the "Sports" section, assume a section with class "sports-section" holds the headline in an <h2> element.
        sports = soup.select_one("section.sports-section h2")
        headlines["Sports"] = sports.text.strip() if sports else ""
        
        # For the "Opinion" section, assume a section with class "opinion-section" holds the headline in an <h2> element.
        opinion = soup.select_one("section.opinion-section h2")
        headlines["Opinion"] = opinion.text.strip() if opinion else ""
        
        # Log the scraped headlines for debugging
        for section, headline in headlines.items():
            loguru.logger.info(f"{section} headline: {headline}")

    return headlines


if __name__ == "__main__":

    # Setup logger to track runtime
    loguru.logger.add("scrape.log", rotation="1 day")

    # Create data dir if needed
    loguru.logger.info("Creating data directory if it does not exist")
    try:
        os.makedirs("data", exist_ok=True)
    except Exception as e:
        loguru.logger.error(f"Failed to create data directory: {e}")
        sys.exit(1)

    # Load daily event monitor
    loguru.logger.info("Loading daily event monitor")
    dem = daily_event_monitor.DailyEventMonitor(
        "data/daily_pennsylvanian_headlines.json"
    )

    # Run scrape
    loguru.logger.info("Starting scrape")
    try:
        data_point = scrape_data_point()
    except Exception as e:
        loguru.logger.error(f"Failed to scrape data point: {e}")
        data_point = None

    # Save data
    if data_point is not None:
        dem.add_today(data_point)
        dem.save()
        loguru.logger.info("Saved daily event monitor")

    def print_tree(directory, ignore_dirs=[".git", "__pycache__"]):
        loguru.logger.info(f"Printing tree of files/dirs at {directory}")
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            level = root.replace(directory, "").count(os.sep)
            indent = " " * 4 * (level)
            loguru.logger.info(f"{indent}+--{os.path.basename(root)}/")
            sub_indent = " " * 4 * (level + 1)
            for file in files:
                loguru.logger.info(f"{sub_indent}+--{file}")

    print_tree(os.getcwd())

    loguru.logger.info("Printing contents of data file {}".format(dem.file_path))
    with open(dem.file_path, "r") as f:
        loguru.logger.info(f.read())

    # Finish
    loguru.logger.info("Scrape complete")
    loguru.logger.info("Exiting")
