#!/usr/bin/env python3

import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Set, List, Tuple
import time
import logging

logger = logging.getLogger(__name__)

class URLProcessingError(Exception):
    """Custom exception for URL processing errors"""
    pass

class CrawlingError(Exception):
    """Custom exception for crawling errors"""
    pass

class WebsiteCrawler:
    def __init__(self, domain: str):
        self.domain = domain
        self.base_url = f"https://{domain}"
        # Normalize the base URL
        self.base_url, _ = self.process_url(self.base_url)
        self.visited_urls: Set[str] = set()
        self.results: List[Tuple[str, str, int]] = []
        self.external_links: Set[str] = set()
        self.session = requests.Session()
        # Set a user agent to be more polite
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; WebsiteCrawler/1.0; +https://github.com/stratofax/website-crawler)'
        })

    def process_url(self, url: str) -> Tuple[str, bool]:
        """
        Process and validate a URL.
        Returns: (cleaned_url, is_internal)
        Raises: URLProcessingError if URL is invalid
        """
        if not url:
            raise URLProcessingError("Empty URL")
            
        try:
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise URLProcessingError("Invalid URL format")
                
            # Clean URL by removing fragments, query parameters, and trailing slashes
            path = parsed_url.path
            if not path or path == '/':
                path = ''
            else:
                path = path.rstrip('/')
                
            clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{path}"
            is_internal = self.domain in parsed_url.netloc
            
            if parsed_url.scheme not in ('http', 'https'):
                raise URLProcessingError("Unsupported protocol")
                
            return clean_url, is_internal
            
        except Exception as e:
            raise URLProcessingError(f"URL processing error: {str(e)}")

    def crawl(self, collect_external: bool = False, recursive: bool = False) -> None:
        """
        Crawl the website starting from the base URL.
        
        In non-recursive mode:
        - Crawls the base URL and follows internal links found on that page
        - Does not follow links found on subsequent pages
        
        In recursive mode:
        - Crawls the base URL and follows all internal links recursively
        - Continues until all reachable internal pages are visited
        
        Args:
            collect_external: If True, record (but don't crawl) external links found
            recursive: If True, recursively follow internal links on all visited pages
        """
        logger.info(f"Starting crawl of {self.base_url}")
        logger.info(f"Mode: {'Recursive' if recursive else 'Single-level'} crawl, {'collecting' if collect_external else 'ignoring'} external links")
        self._crawl_page(self.base_url, collect_external, recursive)
        logger.info(f"Crawl complete. Visited {len(self.visited_urls)} pages")
        if collect_external:
            logger.info(f"Found {len(self.external_links)} unique external links")

    def _crawl_page(self, url: str, collect_external: bool, recursive: bool) -> None:
        """Internal method to crawl a single page and process its links."""
        try:
            clean_url, is_internal = self.process_url(url)
            if not is_internal or clean_url in self.visited_urls:
                return

            self.visited_urls.add(clean_url)
            logger.debug(f"Crawling {clean_url}")

            response = self.session.get(clean_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Process page title
            title = soup.title.string.strip() if soup.title else "No title"
            self.results.append((clean_url, title, response.status_code))

            # Process links
            for link in soup.find_all('a', href=True):
                next_url = urljoin(url, link['href'])
                try:
                    next_clean_url, next_is_internal = self.process_url(next_url)
                    
                    if next_is_internal and recursive:
                        if next_clean_url not in self.visited_urls:
                            self._crawl_page(next_clean_url, collect_external, recursive)
                    elif not next_is_internal and collect_external:
                        self.external_links.add(next_clean_url)
                        
                except URLProcessingError:
                    continue

        except requests.HTTPError as e:
            logger.error(f"HTTP Error crawling {url}: {str(e)}")
            self.results.append((url, "Error", e.response.status_code))
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            self.results.append((url, "Error", 0))
        
        time.sleep(1)  # Be polite

    def save_results(self, output_file: str) -> None:
        """Save results to a CSV file."""
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['URL', 'Title', 'Status Code'])
            writer.writerows(self.results)
        logger.info(f"Results saved to {output_file}")

    def save_external_links_results(self, filename: str) -> None:
        """Save external links to a CSV file."""
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['External URL'])
            for url in sorted(self.external_links):
                writer.writerow([url])
        logger.info(f"External links saved to {filename}")

    def check_external_links(self):
        """
        Crawl the website and collect external links from all pages.
        Recursively follows internal links to find external links on subpages.
        """
        logger.info("Starting recursive crawl to find external links...")
        self.crawl_page(self.base_url, collect_external=True, recursive=True)
        logger.info(f"Found {len(self.external_links)} unique external links across {len(self.visited_urls)} pages")

    def crawl_page(self, url: str, collect_external: bool = False, recursive: bool = False) -> None:
        """
        Crawl a page and its links.
        
        Args:
            url: The URL to crawl
            collect_external: If True, collect external links instead of crawling them
            recursive: If True, follow internal links recursively
        """
        # Skip if we've already visited this URL
        clean_url = self.process_url(url)[0]
        if not clean_url or clean_url in self.visited_urls:
            return

        # Add URL to visited set
        self.visited_urls.add(clean_url)
        logger.debug(f"Crawling {clean_url}")

        try:
            # Get page content
            response = self.session.get(clean_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            title = soup.title.string.strip() if soup.title else "No title"
            logger.debug(f"Title: {title}")
            self.results.append((clean_url, title, response.status_code))

            # Find all links
            for link in soup.find_all('a', href=True):
                href = link['href']
                next_url = urljoin(url, href)
                logger.debug(f"Found link: {href} -> {next_url}")

                # Skip non-HTTP links
                if not next_url.startswith(('http://', 'https://')):
                    logger.debug(f"Skipping non-HTTP link: {href}")
                    continue

                if self.process_url(next_url)[1]:
                    if recursive and self.process_url(next_url)[0] not in self.visited_urls:
                        self.crawl_page(next_url, collect_external=collect_external, recursive=recursive)
                elif collect_external:
                    logger.info(f"Found external link: {next_url}")
                    self.external_links.add(next_url)

        except requests.HTTPError as e:
            logger.error(f"HTTP Error crawling {url}: {str(e)}")
            self.results.append((clean_url, "Error", e.response.status_code))
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            self.results.append((clean_url, "Error", 0))
            
        # Be polite and don't hammer the server
        time.sleep(1)
