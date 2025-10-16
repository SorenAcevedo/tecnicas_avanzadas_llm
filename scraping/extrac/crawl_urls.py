import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import json

START_URL = "https://www.colgatepalmolive.com.co/"
MAX_PAGES = 100  # Set a reasonable limit to avoid infinite crawling
CRAWL_DELAY = 1  # seconds between requests

visited = set()
queue = [START_URL]
all_urls = set()

while queue and len(visited) < MAX_PAGES:
    url = queue.pop(0)
    if url in visited:
        continue
    print(f"Crawling: {url}")
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            continue
        soup = BeautifulSoup(resp.text, "html.parser")
        visited.add(url)
        all_urls.add(url)
        # Find all internal links
        for a in soup.find_all("a", href=True):
            link = a["href"]
            # Normalize link
            abs_link = urljoin(url, link)
            # Skip anchor links (fragments)
            parsed = urlparse(abs_link)
            abs_link_no_fragment = parsed._replace(fragment="").geturl()
            # Only crawl links within the same domain and without fragment
            if parsed.netloc == urlparse(START_URL).netloc:
                if abs_link_no_fragment not in visited and abs_link_no_fragment not in queue:
                    queue.append(abs_link_no_fragment)
        time.sleep(CRAWL_DELAY)
    except Exception as e:
        print(f"Error crawling {url}: {e}")

# Save results
import os
os.makedirs("scraping/extrac", exist_ok=True)
with open("scraping/extrac/colgate_urls_crawled.json", "w", encoding="utf-8") as f:
    json.dump(sorted(list(all_urls)), f, ensure_ascii=False, indent=2)

print(f"Crawled {len(all_urls)} URLs. Saved to scraping/extrac/colgate_urls_crawled.json.")
