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
        self.base_url = f"https://{domain}"
        self.visited_urls: Set[str] = set()
        self.results: List[Tuple[str, str, int]] = []
        self.external_links: Set[str] = set()  # Store external links found
        self.session = requests.Session()
        # Set a user agent to be more polite
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; WebsiteCrawler/1.0; +https://github.com/stratofax/website-crawler)'
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

    def is_external_link(self, url: str) -> bool:
        """Check if a URL is external to the base domain."""
        try:
            return self.domain not in url and url.startswith(('http://', 'https://'))
        except:
            return False

    def check_external_links(self):
        """
        Crawl the website and collect external links from all pages.
        Recursively follows internal links to find external links on subpages.
        """
        print("\nStarting recursive crawl to find external links...")
        self.crawl_page(self.base_url, collect_external=True, recursive=True)
        print(f"\nFound {len(self.external_links)} unique external links across {len(self.visited_urls)} pages")

    def crawl_page(self, url: str, collect_external: bool = False, recursive: bool = False) -> None:
        """
        Crawl a page and its links.
        
        Args:
            url: The URL to crawl
            collect_external: If True, collect external links instead of crawling them
            recursive: If True, follow internal links recursively
        """
        # Clean the URL before checking if visited
        clean_url = self.clean_url(url)
        if clean_url in self.visited_urls:
            return

        # Add to visited URLs before making request to prevent revisits on error
        self.visited_urls.add(clean_url)

        try:
            print(f"\nFetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else "No title"
            print(f"Title: {title}")
            self.results.append((clean_url, title, response.status_code))

            # Find all links on the page
            print("\nFound links:")
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if not href or href.startswith(('mailto:', 'tel:', 'javascript:')):
                    continue

                next_url = urljoin(url, href)
                print(f"- {href} -> {next_url}")

                if self.is_external_link(next_url):
                    if collect_external:
                        print(f"  (external)")
                        self.external_links.add(next_url)
                elif recursive and self.is_valid_url(next_url):
                    clean_next_url = self.clean_url(next_url)
                    if clean_next_url not in self.visited_urls:
                        self.crawl_page(next_url, collect_external=collect_external, recursive=recursive)

        except requests.HTTPError as e:
            print(f"HTTP Error: {e}")
            self.results.append((clean_url, "Error", e.response.status_code))
            return
        except Exception as e:
            print(f"Error: {e}")
            self.results.append((clean_url, "Error", 0))
            return
            
        # Be polite and don't hammer the server
        time.sleep(1)

    def save_results(self, output_file: str) -> None:
        """Save results to a CSV file."""
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['URL', 'Title', 'Status Code'])
            writer.writerows(self.results)

    def save_external_links_results(self, filename: str) -> None:
        """Save external links to a CSV file."""
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['External URL'])
            for url in sorted(self.external_links):
                writer.writerow([url])
