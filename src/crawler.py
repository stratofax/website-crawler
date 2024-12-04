#!/usr/bin/env python3

import sys
import argparse
import logging
from datetime import datetime
from src.website_crawler import WebsiteCrawler

def setup_logging(verbose: bool):
    """Configure logging based on verbosity level."""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def main():
    """Main function to run the crawler"""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Crawl a website and generate a report')
    parser.add_argument('domain', help='Domain to crawl (e.g., example.com)')
    parser.add_argument('-e', '--external-links', action='store_true', help='Check for external links on the domain')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    # Parse arguments
    try:
        args = parser.parse_args()
    except SystemExit:
        return
    
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.debug("Debug logging enabled")
    
    # Create crawler instance
    crawler = WebsiteCrawler(args.domain)
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y-%m-%dT%H%M")
    
    if args.external_links:
        # Check external links and save results
        crawler.check_external_links()
        output_file = f"{args.domain}_{timestamp}_external_links.csv"
        crawler.save_external_links_results(output_file)
    else:
        # Regular crawl
        crawler.crawl_page(crawler.base_url)
        output_file = f"{args.domain}_{timestamp}.csv"
        crawler.save_results(output_file)
    
    print(f"\nCrawling complete! Results saved to {output_file}")
    print(f"Total pages crawled: {len(crawler.visited_urls)}")

if __name__ == "__main__":
    main()
