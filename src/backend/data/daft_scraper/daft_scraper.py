from playwright.sync_api import sync_playwright
import time
import csv
from utils import _process_listings_on_page, accept_cookies_if_present
from dataclasses import asdict

BASE_URL = "https://www.daft.ie/property-for-rent/dublin-city"  # Base URL for Dublin City rentals
OUTPUT_FILE = "data.csv"
MAX_PAGES_TO_SCRAPE = 3
PAGE_SIZE = 20  # Number of results per page
REQUEST_DELAY_BETWEEN_PAGES = 5

LISTINGS_AREA_SELECTOR = "ul[data-testid='results']"

LISTING_CARD_SELECTOR = (
    "li[data-testid^='result-']"  # li items whose data-testid starts with 'result-'
)


def scrape_daft_playwright():
    all_listings_data = []

    with sync_playwright() as p:
        # Launch browser. Headless=False lets you see the browser actions.
        # For actual scraping runs, set headless=True for speed and no UI.
        # slow_mo adds a delay (in ms) between Playwright operations, useful for debugging.
        browser = p.chromium.launch(headless=False, slow_mo=250)

        # Create a new browser context with a realistic User-Agent
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        )
        page = context.new_page()

        print(
            f"Starting Playwright scraper for Daft.ie. Will attempt to scrape up to {MAX_PAGES_TO_SCRAPE} pages."
        )

        for i in range(MAX_PAGES_TO_SCRAPE):
            current_offset = i * PAGE_SIZE
            # Construct URL based on Daft.ie's pagination (uses 'from' as an offset)
            current_url = f"{BASE_URL}?pageSize={PAGE_SIZE}&from={current_offset}"

            print(
                f"\n--- Attempting to scrape Page {i + 1} (offset {current_offset}) ---"
            )
            print(f"Navigating to: {current_url}")

            try:
                page.goto(
                    current_url, timeout=90000
                )  # 90 seconds timeout for page load
                print(f"Page loaded: {page.title()}")

                # Click accept all cookies button if it exists
                accept_cookies_if_present(page)

                try:
                    listings_area_locator = page.locator(LISTINGS_AREA_SELECTOR)
                    listings_area_locator.wait_for(state="visible", timeout=45000)
                    print(
                        f"Listings area ({LISTINGS_AREA_SELECTOR}) found and visible."
                    )
                except Exception as e_wait:
                    print(
                        f"Could not find or wait for listings area with selector '{LISTINGS_AREA_SELECTOR}': {e_wait}"
                    )
                    continue  # Skip to the next page

                listing_card_locators = listings_area_locator.locator(
                    LISTING_CARD_SELECTOR
                )

                # Call the new helper function to process listings on this page
                _process_listings_on_page(
                    listing_card_locators, all_listings_data, i
                )

                # Respectful delay before fetching the next page
                if i < MAX_PAGES_TO_SCRAPE - 1:
                    print(
                        f"  Sleeping for {REQUEST_DELAY_BETWEEN_PAGES} seconds before next page..."
                    )
                    time.sleep(REQUEST_DELAY_BETWEEN_PAGES)

            except Exception as e_page:
                print(
                    f"  An error occurred while processing page {current_url}: {e_page}"
                )
                continue  # Move to the next page

        # Close the browser
        browser.close()
        print(
            f"\n--- Scraping Finished. Total listings scraped: {len(all_listings_data)} ---"
        )

    # Save data to CSV
    if all_listings_data:
        field_names = [
            "price",
            "beds",
            "baths",
            "prop_type",
            "address",
            "link",
        ]
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=field_names)
            dict_writer.writeheader()
            # Convert Listing objects to dictionaries for CSV writing
            dict_writer.writerows([asdict(listing) for listing in all_listings_data])
        print(f"Data saved to {OUTPUT_FILE}")
    else:
        print("No data was scraped to save.")


if __name__ == "__main__":
    print("Starting Playwright scraper for Daft.ie...")
    print("=" * 60)
    scrape_daft_playwright()
