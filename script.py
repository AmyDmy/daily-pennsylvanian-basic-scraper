"""
Scrapes a headline from The Daily Pennsylvanian website and saves it to a 
JSON file that tracks headlines over time.
"""

import os
import sys
import re

import daily_event_monitor

import bs4
import requests
import loguru

def get_top_headline(soup, section_name):
    """
    Finds the first headline link following a header that contains the section name.
    This version uses a regex to robustly match the section name in header text.
    """
    # Look for header tags that might contain the section name (e.g., <h2> or <h3>)
    header = soup.find(lambda tag: tag.name in ["h2", "h3"] and 
                       re.search(r'\b' + re.escape(section_name) + r'\b', tag.get_text(strip=True), re.IGNORECASE))
    if header:
        # Assume the top headline is the first <a> tag after the header
        anchor = header.find_next("a")
        if anchor:
            return anchor.get_text(strip=True)
    return ""

def scrape_data_point():
    """
    Scrapes the top headlines from the "Featured", "News", "Sports", and "Opinion"
    sections on The Daily Pennsylvanian home page.

    Returns:
        dict: A dictionary mapping each section name to its top headline text.
    """
    headers = {
        "User-Agent": "cis3500-scraper"
    }
    req = requests.get("https://www.thedp.com", headers=headers)
    loguru.logger.info(f"Request URL: {req.url}")
    loguru.logger.info(f"Request status code: {req.status_code}")

    # Prepare a dictionary for our sections.
    headlines = {
        "Featured": "",
        "News": "",
        "Sports": "",
        "Opinion": ""
    }

    if req.ok:
        soup = bs4.BeautifulSoup(req.text, "html.parser")
        for section in headlines.keys():
            headline = get_top_headline(soup, section)
            headlines[section] = headline
            loguru.logger.info(f"{section} headline: {headline}")

    return headlines

if __name__ == "__main__":

    # Setup logger to track runtime events.
    loguru.logger.add("scrape.log", rotation="1 day")

    # Create data directory if it does not exist.
    loguru.logger.info("Creating data directory if it does not exist")
    try:
        os.makedirs("data", exist_ok=True)
    except Exception as e:
        loguru.logger.error(f"Failed to create data directory: {e}")
        sys.exit(1)

    # Load daily event monitor.
    loguru.logger.info("Loading daily event monitor")
    dem = daily_event_monitor.DailyEventMonitor(
        "data/daily_pennsylvanian_headlines.json"
    )

    # Run the scrape.
    loguru.logger.info("Starting scrape")
    try:
        data_point = scrape_data_point()
    except Exception as e:
        loguru.logger.error(f"Failed to scrape data point: {e}")
        data_point = None

    # Save scraped data.
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

    # Finish.
    loguru.logger.info("Scrape complete")
    loguru.logger.info("Exiting")
