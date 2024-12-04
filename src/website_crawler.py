#!/usr/bin/env python3

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

    def clean_url(self, url: str) -> str:
        """Clean the URL by removing fragments and query parameters."""
        parsed_url = urlparse(url)
        # Remove both fragment (#) and query parameters (?)
        clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        return clean_url

    def is_valid_url(self, url: str) -> bool:
        """Check if the URL belongs to the target domain and uses a valid protocol."""
        try:
            parsed_url = urlparse(url)
            return (parsed_url.netloc == self.domain and 
                   parsed_url.scheme in ('http', 'https'))
        except Exception:
            return False

    def crawl_page(self, url: str) -> None:
        """Crawl a single page and extract links."""
        # Clean the URL before checking if visited
        clean_url = self.clean_url(url)
        if clean_url in self.visited_urls:
            return

        self.visited_urls.add(clean_url)
        print(f"Crawling: {clean_url}")

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
                    if self.is_valid_url(next_url):
                        clean_next_url = self.clean_url(next_url)
                        if clean_next_url not in self.visited_urls:
                            self.crawl_page(next_url)
            
            self.results.append((clean_url, title, status_code))

        except Exception as e:
            print(f"Error crawling {clean_url}: {str(e)}")
            self.results.append((clean_url, "Error", 0))

        # Be polite and don't hammer the server
        time.sleep(1)

    def save_results(self, output_file: str) -> None:
        """Save results to a CSV file."""
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['URL', 'Title', 'Status Code'])
            writer.writerows(self.results)
