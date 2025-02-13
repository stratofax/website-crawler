#!/usr/bin/env python3

import sys
import argparse
import logging
from datetime import datetime
from .website_crawler import WebsiteCrawler

def setup_logging(verbose: bool):
    """Configure logging based on verbosity level."""
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Force remove all handlers to ensure basicConfig works
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Ensure root logger level is set
    logging.getLogger().setLevel(log_level)

def main():
    """Main function to run the crawler"""
    parser = argparse.ArgumentParser(description='Crawl a website and generate a report')
    parser.add_argument('domain', help='Domain to crawl (e.g., example.com)')
    parser.add_argument('-e', '--external-links', action='store_true', help='Check for external links on the domain')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-r', '--recursive', action='store_true', help='Recursively crawl internal links')
    parser.add_argument('-p', '--pages', action='store_true', help='Only crawl web pages (HTML, PHP, etc.) and skip other file types')
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Create crawler instance and run
    crawler = WebsiteCrawler(args.domain)
    timestamp = datetime.now().strftime("%Y-%m-%dT%H%M")
    
    try:
        if args.external_links:
            crawler.crawl(collect_external=True, recursive=args.recursive, pages_only=args.pages)
            output_file = f"{args.domain}_{timestamp}_external_links.csv"
            crawler.save_external_links_results(output_file)
        else:
            crawler.crawl(recursive=args.recursive, pages_only=args.pages)
            output_file = f"{args.domain}_{timestamp}.csv"
            crawler.save_results(output_file)
        
        logger.info(f"Crawling complete! Results saved to {output_file}")
        logger.info(f"Total pages crawled: {len(crawler.visited_urls)}")
    
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
