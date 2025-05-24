from playwright.sync_api import sync_playwright
import time
import csv
import re


# --- Regex Extraction Functions (Placeholders) ---
def extract_address_with_regex(text):
    # TODO: Implement regex for address
    # Example: pattern = re.compile(r"your_address_regex_here")
    # match = pattern.search(text)
    # return match.group(1).strip() if match else "N/A"
    return "N/A # Address via Regex TODO"


def extract_price_with_regex(text):
    if text == "N/A" or not text:
        return "N/A"
    # Matches price like €2,549 per month or €2549 per month
    match = re.search(r"€([\d,]+(?:\.\d{2})?)\s*per month", text, re.IGNORECASE)
    return match.group(1).replace(",", "") if match else "N/A"


def extract_beds_with_regex(text):
    if text == "N/A" or not text:
        return ""
    # Matches "1 Bed", "2 Beds", etc. or "Studio"
    studio_match = re.search(r"(Studio)", text, re.IGNORECASE)
    if studio_match:
        return "0"

    match = re.search(r"(\d+)\s*Bed(s)?", text, re.IGNORECASE)
    return match.group(1) if match else ""  # Return empty string if no bed info


def extract_baths_with_regex(text):
    if text == "N/A" or not text:
        return ""
    # Matches "1 Bath", "2 Baths", etc.
    match = re.search(r"(\d+)\s*Bath(s)?", text, re.IGNORECASE)
    return match.group(1) if match else ""  # Return empty string if no bath info


def extract_property_type_with_regex(text):
    if text == "N/A" or not text:
        return ""
    # Matches common property types. Order matters if types can be substrings of others.
    # For "Studio", it's often a type itself and might also imply 0 beds.
    # If "Studio" is already captured by extract_beds_with_regex, we might not need it here or handle it differently.
    # Assuming "Studio" is a distinct type here if not already handled as beds.
    if "Studio" in text and extract_beds_with_regex(text) == "Studio":
        return "Studio"  # If beds function identified it as Studio type

    # More specific types first
    type_patterns = [
        r"(Townhouse)",
        r"(Apartment)",
        r"(House)",
        r"(Studio)",  # General Studio if not caught by bed logic
        r"(Duplex)",
        # Add other types as needed, e.g., Bungalow, Semi-Detached House, etc.
    ]
    for pattern in type_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""  # Return empty string if no type found


# --- Helper function to process a single mini-card (an <a> tag representing a unit) ---
def _process_mini_card(a_tag_locator, main_listing_idx, unit_idx):
    try:
        all_texts_for_unit = []
        extracted_link_href_for_unit = None

        # Try to get href for link extraction
        # This check can be simplified as we are processing one a_tag_locator
        href = a_tag_locator.get_attribute("href")
        if href and href.startswith("/for-rent/"):
            extracted_link_href_for_unit = href

        # Get text content for other details
        tag_texts = a_tag_locator.all_text_contents()
        for text_content in tag_texts:
            cleaned_text = text_content.strip()
            if cleaned_text:
                all_texts_for_unit.append(cleaned_text)

        combined_text_for_unit = (
            " ".join(all_texts_for_unit) if all_texts_for_unit else "N/A"
        )

        if extracted_link_href_for_unit:
            link_for_unit = "https://www.daft.ie" + extracted_link_href_for_unit
        else:
            # If no specific /for-rent/ link, this unit might not be a direct property link
            # Depending on requirements, might set to N/A or try to find another link
            link_for_unit = "N/A"

        price = extract_price_with_regex(combined_text_for_unit)
        beds = extract_beds_with_regex(combined_text_for_unit)
        baths = extract_baths_with_regex(combined_text_for_unit)
        prop_type = extract_property_type_with_regex(combined_text_for_unit)

        if prop_type.lower() == "studio":
            beds = "0"
            baths = "0"

        listing_info = {
            "price": price,
            "beds": beds,
            "baths": baths,
            "prop_type": prop_type,
            "link": link_for_unit,
            "source_page": current_url,
        }
        return listing_info

    except Exception as e_mini_card:
        print(
            f"    Error processing mini-card (unit {unit_idx + 1} of main listing {main_listing_idx + 1}): {e_mini_card}"
        )
        return None


# --- Helper function to process a single large card ---
def _process_large_card(listing_locator, main_listing_idx):
    try:
        price_text = "N/A"
        meta_text = "N/A"
        link_for_listing = "N/A"

        # Extract price
        price_div_locator = listing_locator.locator("div[data-tracking='srp_price']")
        if price_div_locator.is_visible(timeout=2000):
            price_text = price_div_locator.text_content(timeout=2000).strip()

        # Extract meta (beds, baths, type)
        meta_div_locator = listing_locator.locator("div[data-tracking='srp_meta']")
        if meta_div_locator.is_visible(timeout=2000):
            meta_text = meta_div_locator.text_content(timeout=2000).strip()

        # For large cards, we assume price is in price_text and other details are in meta_text
        # The regex functions expect a single string, so we might need to combine or pass them separately.
        # Let's assume extract_price_with_regex works on price_text, and others on meta_text.

        price = extract_price_with_regex(price_text)
        beds = extract_beds_with_regex(
            meta_text
        )  # meta_text typically like "1 Bed • 1 Bath • Apartment"
        baths = extract_baths_with_regex(meta_text)
        prop_type = extract_property_type_with_regex(meta_text)

        if prop_type.lower() == "studio":
            beds = "0"
            baths = "0"

        listing_info = {
            "price": price,
            "beds": beds,
            "baths": baths,
            "prop_type": prop_type,
            "link": "N/A",
        }
        return listing_info

    except Exception as e_large_card:
        print(
            f"    Error processing large card (main listing {main_listing_idx + 1}): {e_large_card}"
        )
        return None


# --- Helper function to process listings on a single page ---
def _process_listings_on_page(
    listing_card_locators, current_url, all_listings_data, page_index
):
    count = listing_card_locators.count()
    print(f"  Found {count} potential listing elements on page {page_index + 1}.")

    if count == 0:
        print(
            f"  No individual listings found on page {page_index + 1} with current selectors."
        )
        return  # No listings to process

    # Loop over each card
    for j in range(count):
        listing_locator = listing_card_locators.nth(j)

        # HTML structure within this main listing card:
        # div data-testid="card-container" contains the options for individual units
        # Each div contains multiple 'a' elements, each representing a unit

        # check if the first child is an 'a' tag
        a_element = listing_locator.locator("div").nth(0)
        # get the a link from the first child
        a_link = a_element.locator("a")
        if a_link.is_visible(timeout=5000):
            href = a_link.get_attribute("href")
            if href:
                print(f"  Found a link: {href}")

        try:
            card_container_locator = listing_locator.locator(
                "div[data-testid='card-container']"
            ).nth(1)

            if card_container_locator.is_visible(timeout=5000):
                # look for a div:
                div_locator = card_container_locator.locator("div")
                num_divs = div_locator.count()
                print(f"Found {num_divs} divs in card container")

                if num_divs == 1:
                    # process the single listing
                    print(
                        f"  Processing as large card (1 div found in card container) for listing {j + 1}"
                    )
                    listing_info = _process_large_card(listing_locator, j)
                    if listing_info:
                        all_listings_data.append(listing_info)
                else:
                    continue
                    # process the mini-cards
                    print(
                        f"  Processing as mini-cards ({num_divs} divs, expected a_tags) for listing {j + 1}"
                    )
                    a_tags = card_container_locator.locator("a")
                    num_a_tags = a_tags.count()
                    print(f"Found {num_a_tags} a tags in card container")

                    for k in range(num_a_tags):
                        unit_listing_info = _process_mini_card(a_tags.nth(k), j, k)
                        if unit_listing_info:
                            all_listings_data.append(unit_listing_info)
            else:
                print(
                    f"    Card container with unit links not found for main listing {j + 1} on page {page_index + 1}"
                )

        except Exception as e_item:
            # Note: Using (j + 1) for listing index on the current page.
            print(
                f"    Error processing main listing card ({j + 1}) on page {page_index + 1}: {e_item}"
            )
            continue  # Move to the next listing_locator on the current page

    if count > 0:
        print(
            f"  Successfully attempted to process {count} main listings on page {page_index + 1}."
        )


# --- Configuration ---
# PROPERTY_ADDRESS_SELECTOR = "p[data-testid='address']" # Address extraction deferred
BASE_URL = "https://www.daft.ie/property-for-rent/dublin-city"  # Base URL for Dublin City rentals
OUTPUT_FILE = "output.csv"
MAX_PAGES_TO_SCRAPE = 1
PAGE_SIZE = 20  # Number of results per page
REQUEST_DELAY_BETWEEN_PAGES = 5

COOKIE_BUTTON_SELECTOR = "button[id='didomi-notice-agree-button']"
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
                try:
                    if page.is_visible(COOKIE_BUTTON_SELECTOR, timeout=5000):
                        page.click(COOKIE_BUTTON_SELECTOR)
                        print("Clicked cookie consent button.")
                        time.sleep(2)
                    else:
                        print(
                            "Cookie consent button not found or not visible within timeout."
                        )
                except Exception as e_cookie:
                    print(f"No cookie button, or error interacting with it: {e_cookie}")

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
                    page.screenshot(
                        path=f"debug_daft_page_{i + 1}_no_listings_area.png"
                    )
                    print(
                        f"  Screenshot saved to debug_daft_page_{i + 1}_no_listings_area.png"
                    )
                    continue  # Skip to the next page

                listing_card_locators = listings_area_locator.locator(
                    LISTING_CARD_SELECTOR
                )

                # Call the new helper function to process listings on this page
                _process_listings_on_page(
                    listing_card_locators, current_url, all_listings_data, i
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
            "link",
            "source_page",
        ]
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=field_names)
            dict_writer.writeheader()
            dict_writer.writerows(all_listings_data)
        print(f"Data saved to {OUTPUT_FILE}")
    else:
        print("No data was scraped to save.")


if __name__ == "__main__":
    print("Starting Playwright scraper for Daft.ie...")
    print("=" * 60)
    scrape_daft_playwright()
