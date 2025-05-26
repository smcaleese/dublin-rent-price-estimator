import requests
from bs4 import BeautifulSoup
import time
import csv  # To save data to a CSV file

# --- Configuration ---
# Base URL for constructing page URLs
PAGINATION_BASE_URL = "https://www.rent.ie/houses-to-let/renting_dublin/page_"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
OUTPUT_FILE = "data.csv"
MAX_PAGES_TO_SCRAPE = 1
START_PAGE_NUMBER = 1
REQUEST_DELAY = 3


def scrape_page_data(url):
    """
    Scrapes a single page of listings.
    Returns a list of dictionaries (each representing a listing).
    """
    print(f"Scraping page: {url}")
    listings_data = []

    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {url}: {e}")
        return listings_data  # Return empty list on error

    soup = BeautifulSoup(response.content, "html.parser")

    main_container = soup.find("div", id="searchresults_container")
    if not main_container:
        print("No main container found.")
        return []

    listing_containers = main_container.find_all("div", class_="search_result")
    print(f"Number of listings in the container: {len(listing_containers)}")

    if not listing_containers:
        print(
            f"No listing containers found on {url} with the specified selector. Please inspect the website HTML and update the script, or it might be the end of results."
        )

    for container in listing_containers:
        try:
            price = None
            address = None
            beds_baths_furnished = None
            description = None

            # --- Address Extraction ---
            address_container = container.find("div", class_="sresult_address")
            if address_container:
                h2_tag = address_container.find("h2")
                if h2_tag:
                    address = h2_tag.get_text(separator=" ", strip=True)

            # --- Price and Features Extraction ---
            details_container = container.find("div", class_="sresult_details")
            if details_container:
                description_container = details_container.find(
                    "div", class_="sresult_description"
                )
                if description_container:
                    # Price: first h4
                    h4_tag = description_container.find("h4")
                    if h4_tag:
                        price = h4_tag.text.strip()
                    # Features: second h3 (if present)
                    h3_tag = description_container.find("h3")
                    if h3_tag:
                        beds_baths_furnished = h3_tag.text.strip()
                    description_div = description_container.find("div")
                    if description_div:
                        description = description_div.get_text(separator=" ", strip=True)

            listings_data.append(
                {
                    "address": address or "N/A",
                    "price": price or "N/A",
                    "features": beds_baths_furnished or "N/A",
                    "description": description or "N/A",
                }
            )
            print(f"  Scraped: {address} - {price}")

        except Exception as e:
            print(f"    Error scraping one listing item on {url}: {e}")
            continue  # Skip to the next item in this page

    return listings_data


def main():
    all_listings_data = []

    print(
        f"Starting scraper. Will attempt to scrape up to {MAX_PAGES_TO_SCRAPE} pages."
    )

    for page_number in range(
        START_PAGE_NUMBER, START_PAGE_NUMBER + MAX_PAGES_TO_SCRAPE
    ):
        current_url = f"{PAGINATION_BASE_URL}{page_number}"

        print(f"\n--- Attempting to scrape Page {page_number} ---")
        listings_on_page = scrape_page_data(current_url)

        if listings_on_page:
            all_listings_data.extend(listings_on_page)
        else:
            print(f"No listings found on {current_url}.")

        if page_number < (
            START_PAGE_NUMBER + MAX_PAGES_TO_SCRAPE - 1
        ):  # No need to sleep after the last page
            print(f"Sleeping for {REQUEST_DELAY} seconds before next page...")
            time.sleep(REQUEST_DELAY)

    print(
        f"\n--- Scraping Finished. Total listings scraped: {len(all_listings_data)} from {MAX_PAGES_TO_SCRAPE} attempted pages. ---"
    )

    # Save data to CSV
    if all_listings_data:
        # It's good practice to define a consistent order for columns
        ordered_field_names = ["address", "price", "features", "description"]

        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=ordered_field_names)
            dict_writer.writeheader()
            dict_writer.writerows(all_listings_data)
        print(f"Data saved to {OUTPUT_FILE}")
    else:
        print("No data was scraped to save.")


if __name__ == "__main__":
    print("Starting scraper for rent.ie...")
    print("=" * 30)
    main()
