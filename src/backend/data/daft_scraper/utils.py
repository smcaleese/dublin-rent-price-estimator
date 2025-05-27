from dataclasses import dataclass, asdict
import time
import csv
import re

COOKIE_BUTTON_SELECTOR = "button[id='didomi-notice-agree-button']"


@dataclass
class Listing:
    price: str
    beds: str
    baths: str
    prop_type: str
    link: str
    address: str


def accept_cookies_if_present(page):
    """Attempt to click the cookie consent button if it is present and visible."""
    try:
        if page.is_visible(COOKIE_BUTTON_SELECTOR, timeout=5000):
            page.click(COOKIE_BUTTON_SELECTOR)
            time.sleep(2)
            print("Clicked cookie consent button.")
        else:
            print("Cookie consent button not found or not visible within timeout.")
    except Exception as e_cookie:
        print(f"No cookie button, or error interacting with it: {e_cookie}")


def extract_price_with_regex(text):
    if text == "N/A" or not text:
        return "N/A"
    # Matches price like €2,549 per month or €2549 per week
    match = re.search(r"€([\d,]+)\s*per (?:month|week)", text, re.IGNORECASE)
    return match.group(1).replace(",", "") if match else "N/A"


def extract_beds_with_regex(text):
    if text == "N/A" or not text:
        return ""

    # Check for "Studio"
    studio_match = re.search(r"\bStudio\b", text, re.IGNORECASE)
    if studio_match:
        return "0"

    # Check for "Single"
    single_match = re.search(r"\bSingle\b", text, re.IGNORECASE)
    if single_match:
        return "single"

    # Check for "Twin"
    twin_match = re.search(r"\bTwin\b", text, re.IGNORECASE)
    if twin_match:
        return "twin"

    # Check for "Double"
    double_match = re.search(r"\bDouble\b", text, re.IGNORECASE)
    if double_match:
        return "double"

    # Check for numeric bed count, e.g., "1 Bed", "2 Beds"
    match = re.search(r"(\d+)\s*Bed(?:s)?", text, re.IGNORECASE)
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


def _process_large_card(listing_locator, link, main_listing_idx) -> Listing:
    try:
        price_text = "N/A"
        meta_text = "N/A"

        # Find address
        address_div_locator = listing_locator.locator(
            "div[data-tracking='srp_address']"
        )
        address_text = address_div_locator.text_content().strip()

        # Extract price
        price_div_locator = listing_locator.locator("div[data-tracking='srp_price']")
        if price_div_locator.is_visible(timeout=2000):
            price_text = price_div_locator.text_content(timeout=2000).strip()

        # Extract meta (beds, baths, type)
        meta_div_locator = listing_locator.locator("div[data-tracking='srp_meta']")
        if meta_div_locator.is_visible(timeout=2000):
            meta_text = meta_div_locator.text_content(timeout=2000).strip()

        price = extract_price_with_regex(price_text)
        # multiply weekly price by 4 to get monthly price
        if int(price) <= 300:
            price *= 4

        beds = extract_beds_with_regex(
            meta_text
        )  # meta_text typically like "1 Bed • 1 Bath • Apartment"
        baths = extract_baths_with_regex(meta_text)
        prop_type = extract_property_type_with_regex(meta_text)

        if prop_type.lower() == "studio":
            beds = "0"
            baths = "0"

        # Create and return a Listing object
        return Listing(
            price=price,
            beds=beds,
            baths=baths,
            prop_type=prop_type,
            address=address_text,
            link=link,
        )

    except Exception as e_large_card:
        print(
            f"Error processing large card (main listing {main_listing_idx + 1}): {e_large_card}"
        )
        return None


def _process_card_with_mini_cards(
    first_card_container, second_card_container, main_listing_idx
):
    listing_items = []
    try:
        # the address is in the first card container:
        address_div_locator = first_card_container.locator(
            "div[data-tracking='srp_address']"
        )
        address_text = address_div_locator.text_content().strip()

        # the second card container contains several mini-cards, each with an <a> tag
        a_tag_locator = second_card_container.locator("a")
        num_a_tags = a_tag_locator.count()

        for i in range(num_a_tags):
            mini_card = a_tag_locator.nth(i)
            mini_card_link = f"https://www.daft.ie{mini_card.get_attribute('href')}"

            main_info_locator = mini_card.locator("div[data-tracking='srp_units']")
            main_info_text = main_info_locator.text_content().strip()

            price = extract_price_with_regex(main_info_text)
            if int(price) <= 300:
                price *= 4

            beds = extract_beds_with_regex(main_info_text)
            baths = extract_baths_with_regex(main_info_text)
            prop_type = extract_property_type_with_regex(main_info_text)

            if prop_type.lower() == "studio":
                beds = "0"
                baths = "0"

            # Create and return a Listing object instead of a dictionary
            listing_item = Listing(
                price=price,
                beds=beds,
                baths=baths,
                prop_type=prop_type,
                link=mini_card_link,
                address=address_text,
            )
            listing_items.append(listing_item)

    except Exception as e_mini_card:
        print(
            f"Error processing mini-card (unit {i + 1} of main listing {main_listing_idx + 1}): {e_mini_card}"
        )
        return []

    return listing_items


def _process_listings_on_page(listing_card_locators, all_listings_data, page_index):
    count = listing_card_locators.count()
    print(f"Found {count} potential listing elements on page {page_index + 1}.")

    if count == 0:
        print(
            f"No individual listings found on page {page_index + 1} with current selectors."
        )
        return

    for j in range(count):
        listing_locator = listing_card_locators.nth(j)

        link = "N/A"
        a_element = listing_locator.locator("div").nth(0)
        a_link = a_element.locator("a")
        if a_link.is_visible(timeout=5000):
            href = a_link.get_attribute("href")
            link = "https://www.daft.ie" + href
            if href:
                print(f"Found a link: {href}")

        try:
            card_container_locator = listing_locator.locator(
                "div[data-testid='card-container']"
            )
            card_container_locator_count = card_container_locator.count()

            # 1. If there is only one card container, process as a large card
            # 2. If there are two card containers, get the address from the first container and process the second container as a card with mini-cards
            if card_container_locator_count > 0:
                if card_container_locator_count == 1:
                    first_card_container = card_container_locator.nth(0)
                    listing_item = _process_large_card(first_card_container, link, j)
                    if listing_item:
                        all_listings_data.append(listing_item)
                elif card_container_locator_count == 2:
                    first_card_container = card_container_locator.nth(0)
                    second_card_container = card_container_locator.nth(1)
                    listing_items = _process_card_with_mini_cards(
                        first_card_container, second_card_container, j
                    )
                    if listing_items:
                        all_listings_data.extend(listing_items)
            else:
                print(
                    f"Card container with unit links not found for main listing {j + 1} on page {page_index + 1}"
                )

        except Exception as e_item:
            print(
                f"Error processing main listing card ({j + 1}) on page {page_index + 1}: {e_item}"
            )
            continue

    if count > 0:
        print(
            f"Successfully attempted to process {count} main listings on page {page_index + 1}."
        )
