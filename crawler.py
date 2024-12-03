#!/usr/bin/env python3

import sys
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Set, List, Tuple
import time

class WebsiteCrawler:
    def __init__(self, domain: str):
        self.domain = domain
        self.base_url = f'https://{domain}'
        self.visited_urls: Set[str] = set()
        self.results: List[Tuple[str, str, int]] = []
        self.session = requests.Session()
        # Set a user agent to be more polite
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; PythonWebCrawler/1.0)'
        })

    def is_valid_url(self, url: str) -> bool:
        """Check if the URL belongs to the target domain."""
        parsed_url = urlparse(url)
        # Remove the fragment (#) part of the URL
        clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        if parsed_url.query:
            clean_url += f"?{parsed_url.query}"
        
        # Store the clean URL for future comparisons
        url = clean_url
        return parsed_url.netloc == self.domain

    def crawl_page(self, url: str) -> None:
        """Crawl a single page and extract links."""
        # Clean the URL before checking if visited
        parsed_url = urlparse(url)
        clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        if parsed_url.query:
            clean_url += f"?{parsed_url.query}"
        if clean_url in self.visited_urls:
            return

        self.visited_urls.add(clean_url)
        print(f"Crawling: {url}")

        try:
            response = self.session.get(url, timeout=10)
            status_code = response.status_code
            title = ""

            if status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.title.string.strip() if soup.title else "No title"

                # Find all links on the page
                for link in soup.find_all('a', href=True):
                    next_url = urljoin(url, link['href'])
                    parsed_next_url = urlparse(next_url)
                    clean_next_url = f"{parsed_next_url.scheme}://{parsed_next_url.netloc}{parsed_next_url.path}"
                    if parsed_next_url.query:
                        clean_next_url += f"?{parsed_next_url.query}"
                    if self.is_valid_url(next_url) and clean_next_url not in self.visited_urls:
                        self.crawl_page(next_url)
            
            self.results.append((url, title, status_code))

        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")
            self.results.append((url, "Error", 0))

        # Be polite and don't hammer the server
        time.sleep(1)

    def save_results(self, output_file: str) -> None:
        """Save results to a CSV file."""
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['URL', 'Title', 'Status Code'])
            writer.writerows(self.results)

def main():
    if len(sys.argv) != 3:
        print("Usage: python crawler.py domain output_file")
        print("Example: python crawler.py www.example.com results.csv")
        sys.exit(1)

    domain = sys.argv[1]
    output_file = sys.argv[2]

    crawler = WebsiteCrawler(domain)
    crawler.crawl_page(crawler.base_url)
    crawler.save_results(output_file)
    print(f"\nCrawling complete! Results saved to {output_file}")
    print(f"Total pages crawled: {len(crawler.visited_urls)}")

if __name__ == "__main__":
    main()
