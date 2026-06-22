"""
Marvel Character Scraper
-------------------------
Scrapes structured character data (real name, species, first appearance,
affiliations, abilities, etc.) from Wikipedia infoboxes for a list of
well-known Marvel characters.

Usage:
    pip install requests beautifulsoup4
    python marvel_scraper.py

Output:
    marvel_characters.json
    marvel_characters.csv
"""

import csv
import json
import time

import requests
from bs4 import BeautifulSoup

# Identify ourselves honestly to the server we're requesting from — good scraping etiquette.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PortfolioScraperProject/1.0)"
}

# Wikipedia page titles for each character (must match the exact page slug)
CHARACTERS = [
    "Spider-Man",
    "Iron Man (character)",
    "Captain America",
    "Thor (Marvel Comics)",
    "Hulk (comics)",
    "Black Widow (Natasha Romanova)",
    "Black Panther (character)",
    "Doctor Strange",
    "Scarlet Witch",
    "Wolverine (character)",
    "Deadpool",
    "Carol Danvers",
    "Loki (Marvel Comics character)",
    "Daredevil (Marvel Comics character)",
    "Ant-Man (Scott Lang)",
]


def get_infobox_data(page_title):
    """Fetch a Wikipedia page and pull every label/value pair out of its infobox table."""
    url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    infobox = soup.find("table", class_="infobox")
    if not infobox:
        return None

    data = {
        "name": page_title.split(" (")[0],
        "source_url": url,
    }

    for row in infobox.find_all("tr"):
        header = row.find("th")
        value = row.find("td")
        if not header or not value:
            continue  # skip section divider rows that don't have both a label and a value

        label = header.get_text(" ", strip=True)

        # Some fields (e.g. "Notable aliases", "Abilities") are bullet lists — join them
        items = value.find_all("li")
        if items:
            text = ", ".join(li.get_text(" ", strip=True) for li in items)
        else:
            text = value.get_text(" ", strip=True)

        if text:
            data[label] = text

    return data


def scrape_all():
    results = []
    for title in CHARACTERS:
        print(f"Scraping {title}...")
        try:
            data = get_infobox_data(title)
            if data:
                results.append(data)
            else:
                print(f"  No infobox found for {title}, skipping.")
        except requests.RequestException as e:
            print(f"  Failed to fetch {title}: {e}")
        time.sleep(1)  # be polite — don't hammer the server with rapid requests
    return results


def save_json(data, filename="marvel_characters.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_csv(data, filename="marvel_characters.csv"):
    if not data:
        print("No data to save to CSV.")
        return
    fieldnames = sorted(set().union(*(d.keys() for d in data)))
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    all_data = scrape_all()
    save_json(all_data)
    save_csv(all_data)
    print(f"\nDone. Scraped {len(all_data)} characters.")
    print("Saved to marvel_characters.json and marvel_characters.csv")
