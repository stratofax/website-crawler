#!/usr/bin/env python3

import sys
import argparse
import logging
from datetime import datetime
from src.website_crawler import WebsiteCrawler


def setup_logging(verbose: bool):
    """Configure logging based on verbosity level."""
    # Set up logging
    root_logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        '%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Set log level based on verbosity
    if verbose:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)


def main():
    """Main function to run the crawler."""
    parser = argparse.ArgumentParser(
        description="Crawl a website and generate a CSV report"
    )
    parser.add_argument(
        "domain",
        help="Domain to crawl (e.g., example.com)"
    )
    parser.add_argument(
        "-e", "--external-links",
        action="store_true",
        help="Check for external links on the domain"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Recursively crawl internal links"
    )
    parser.add_argument(
        "-p", "--pages",
        action="store_true",
        help="Only crawl web pages (HTML, PHP, etc.) and skip other file types"
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    try:
        crawler = WebsiteCrawler(args.domain)
        timestamp = datetime.now().strftime("%Y-%m-%dT%H%M")

        if args.external_links:
            crawler.crawl(
                collect_external=True,
                recursive=args.recursive,
                pages_only=args.pages
            )
            # Only save external links when -e flag is used
            ext_links_root = "_external_links.csv"
            external_links_file = f"{args.domain}_{timestamp}{ext_links_root}"
            crawler.save_external_links_results(external_links_file)
            logging.info(f"External links saved to {external_links_file}")
        else:
            crawler.crawl(recursive=args.recursive, pages_only=args.pages)
            output_file = f"{args.domain}_{timestamp}.csv"
            crawler.save_results(output_file)
            logging.info(f"Crawling complete! Results saved to {output_file}")

        logging.info(f"Total pages crawled: {len(crawler.visited_urls)}")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        sys.exit(1)


# pragma: no cover
if __name__ == "__main__":
    main()
