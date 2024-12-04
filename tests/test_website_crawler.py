import pytest
from src.website_crawler import WebsiteCrawler
from urllib.parse import urlparse
import responses
import tempfile
import os
import csv
import time
from unittest.mock import patch
from requests.exceptions import RequestException

def test_init():
    """Test WebsiteCrawler initialization"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)
    assert crawler.domain == domain
    assert crawler.base_url == f"https://{domain}"
    assert len(crawler.visited_urls) == 0
    assert len(crawler.results) == 0

def test_clean_url():
    """Test URL cleaning functionality"""
    crawler = WebsiteCrawler("example.com")
    test_cases = [
        ("https://example.com/page", "https://example.com/page"),
        ("https://example.com/page?param=value", "https://example.com/page"),
        ("https://example.com/page#section", "https://example.com/page"),
        ("https://example.com/page?param=value#section", "https://example.com/page"),
    ]
    
    for input_url, expected_url in test_cases:
        assert crawler.clean_url(input_url) == expected_url

def test_is_valid_url():
    """Test URL validation"""
    crawler = WebsiteCrawler("example.com")
    valid_urls = [
        "https://example.com",
        "https://example.com/",
        "https://example.com/page",
        "https://example.com/page?param=value",
        "http://example.com",  # Both HTTP and HTTPS are valid
    ]
    invalid_urls = [
        "https://other-domain.com",
        "https://subdomain.example.com",
        "invalid-url",
        "ftp://example.com",  # Other protocols are invalid
    ]
    
    for url in valid_urls:
        assert crawler.is_valid_url(url) is True, f"Expected {url} to be valid"
    
    for url in invalid_urls:
        assert crawler.is_valid_url(url) is False, f"Expected {url} to be invalid"

def test_is_valid_url_with_invalid_input():
    """Test URL validation with invalid URL formats"""
    crawler = WebsiteCrawler("example.com")
    invalid_inputs = [
        None,  # None type
        "",    # Empty string
        "://invalid-url",  # Malformed URL
        "http://",  # Missing domain
        "http:///path",  # Invalid domain
    ]
    
    for url in invalid_inputs:
        assert crawler.is_valid_url(url) is False, f"Expected {url} to be invalid"

@responses.activate
def test_crawl_page():
    """Test crawling a single page"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)
    
    # Mock the HTML response
    html_content = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <a href="https://example.com/page1">Link 1</a>
            <a href="https://example.com/page2">Link 2</a>
            <a href="https://other-domain.com">External Link</a>
        </body>
    </html>
    """
    
    # Add mock responses
    responses.add(
        responses.GET,
        "https://example.com",
        body=html_content,
        status=200
    )
    
    responses.add(
        responses.GET,
        "https://example.com/page1",
        body="<html><head><title>Page 1</title></head></html>",
        status=200
    )
    
    responses.add(
        responses.GET,
        "https://example.com/page2",
        body="<html><head><title>Page 2</title></head></html>",
        status=200
    )
    
    # Test crawling
    crawler.crawl_page(crawler.base_url)
    
    # Check results
    assert len(crawler.visited_urls) == 3
    assert len(crawler.results) == 3
    
    # Verify URLs were crawled
    crawled_urls = {result[0] for result in crawler.results}
    expected_urls = {
        "https://example.com",
        "https://example.com/page1",
        "https://example.com/page2"
    }
    assert crawled_urls == expected_urls

@responses.activate
def test_crawl_page_with_error():
    """Test crawling a page that returns an error"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)
    
    # Mock a failed response
    responses.add(
        responses.GET,
        "https://example.com",
        status=404
    )
    
    # Test crawling
    crawler.crawl_page(crawler.base_url)
    
    # Check results
    assert len(crawler.visited_urls) == 1
    assert len(crawler.results) == 1
    assert crawler.results[0] == ("https://example.com", "", 404)

@responses.activate
def test_crawl_page_with_request_exception():
    """Test crawling a page that raises a request exception"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)
    
    # Mock a connection error
    responses.add(
        responses.GET,
        "https://example.com",
        body=RequestException("Connection error")
    )
    
    # Test crawling
    crawler.crawl_page(crawler.base_url)
    
    # Check results
    assert len(crawler.visited_urls) == 1
    assert len(crawler.results) == 1
    assert crawler.results[0] == ("https://example.com", "Error", 0)

@responses.activate
def test_crawl_page_respects_delay():
    """Test that crawl_page respects the delay between requests"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)
    
    # Mock responses for two pages
    responses.add(
        responses.GET,
        "https://example.com",
        body="<html><head><title>Page 1</title></head><body><a href='https://example.com/page2'>Link</a></body></html>",
        status=200
    )
    
    responses.add(
        responses.GET,
        "https://example.com/page2",
        body="<html><head><title>Page 2</title></head></html>",
        status=200
    )
    
    # Record start time
    start_time = time.time()
    
    # Test crawling
    crawler.crawl_page(crawler.base_url)
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    
    # Should have visited 2 pages with 1 second delay between them
    assert len(crawler.visited_urls) == 2
    assert elapsed_time >= 1.0  # At least 1 second delay

def test_save_results():
    """Test saving results to a CSV file"""
    crawler = WebsiteCrawler("example.com")
    crawler.results = [
        ("https://example.com", "Home Page", 200),
        ("https://example.com/about", "About Us", 200),
        ("https://example.com/contact", "Contact", 404)
    ]
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
        output_file = tmp_file.name
    
    try:
        # Save results
        crawler.save_results(output_file)
        
        # Read and verify the CSV content
        with open(output_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            # Check header
            assert rows[0] == ['URL', 'Title', 'Status Code']
            
            # Check data rows
            assert len(rows) == 4  # Header + 3 data rows
            assert rows[1] == ['https://example.com', 'Home Page', '200']
            assert rows[2] == ['https://example.com/about', 'About Us', '200']
            assert rows[3] == ['https://example.com/contact', 'Contact', '404']
    
    finally:
        # Clean up
        os.unlink(output_file)
