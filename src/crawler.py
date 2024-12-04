#!/usr/bin/env python3

import sys
from datetime import datetime
from src.website_crawler import WebsiteCrawler

def main():
    if len(sys.argv) != 2:
        print("Usage: python crawler.py domain")
        print("Example: python crawler.py www.example.com")
        sys.exit(1)

    domain = sys.argv[1]
    # Generate filename with domain and timestamp
    timestamp = datetime.now().strftime("%Y-%m-%dT%H%M")
    output_file = f"{domain}_{timestamp}.csv"

    crawler = WebsiteCrawler(domain)
    crawler.crawl_page(crawler.base_url)
    crawler.save_results(output_file)
    print(f"\nCrawling complete! Results saved to {output_file}")
    print(f"Total pages crawled: {len(crawler.visited_urls)}")

if __name__ == "__main__":
    main()
