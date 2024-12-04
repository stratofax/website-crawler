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
import logging

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
    
    # Test crawling with recursive=True
    crawler.crawl_page(crawler.base_url, recursive=True)
    
    # Check results
    assert len(crawler.visited_urls) == 3
    assert "https://example.com" in crawler.visited_urls
    assert "https://example.com/page1" in crawler.visited_urls
    assert "https://example.com/page2" in crawler.visited_urls

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
    assert crawler.results[0] == ("https://example.com", "Error", 404)

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
    
    # Test crawling with recursive=True
    crawler.crawl_page(crawler.base_url, recursive=True)
    
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

@responses.activate
def test_is_external_url():
    """Test checking if a URL is external"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)

    # Test internal links
    assert not crawler.is_external_url("https://example.com")
    assert not crawler.is_external_url("https://example.com/page")
    assert not crawler.is_external_url("https://sub.example.com")

    # Test external links
    assert crawler.is_external_url("https://other-domain.com")
    assert crawler.is_external_url("https://example.org")

    # Test invalid URLs
    assert not crawler.is_external_url(None)
    assert not crawler.is_external_url("")
    assert not crawler.is_external_url("not-a-url")

@responses.activate
def test_check_external_links():
    """Test collecting external links from a page"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)
    
    # Mock the response with some external and internal links
    html_content = """
    <html>
        <body>
            <a href="https://external1.com">External 1</a>
            <a href="https://external2.com">External 2</a>
            <a href="/internal">Internal</a>
            <a href="https://example.com/page">Internal 2</a>
        </body>
    </html>
    """
    
    responses.add(
        responses.GET,
        "https://example.com",
        body=html_content,
        status=200
    )
    
    # Test crawling
    crawler.check_external_links()
    
    # Check results
    assert len(crawler.external_links) == 2
    assert "https://external1.com" in crawler.external_links
    assert "https://external2.com" in crawler.external_links

@responses.activate
def test_recursive_external_links_collection():
    """Test collecting external links from multiple pages"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)

    # Mock responses for main page and subpages
    responses.add(
        responses.GET,
        "https://example.com",
        body="""
        <html>
            <head><title>Main Page</title></head>
            <body>
                <a href="https://example.com/page1">Page 1</a>
                <a href="https://external1.com">External 1</a>
                <a href="mailto:info@example.com">Email</a>
            </body>
        </html>
        """,
        status=200
    )

    responses.add(
        responses.GET,
        "https://example.com/page1",
        body="""
        <html>
            <head><title>Page 1</title></head>
            <body>
                <a href="https://external2.com">External 2</a>
                <a href="tel:+1234567890">Phone</a>
                <a href="javascript:void(0)">JS Link</a>
            </body>
        </html>
        """,
        status=200
    )

    # Test recursive external links collection
    crawler.check_external_links()

    # Check results
    assert len(crawler.external_links) == 2
    assert "https://external1.com" in crawler.external_links
    assert "https://external2.com" in crawler.external_links
    assert len(crawler.visited_urls) == 2

@responses.activate
def test_save_external_links_results(tmp_path):
    """Test saving external links to a CSV file"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)
    
    # Add some external links
    crawler.external_links.add("https://external1.com")
    crawler.external_links.add("https://external2.com")
    
    # Save results
    output_file = tmp_path / "external_links.csv"
    crawler.save_external_links_results(str(output_file))
    
    # Check file contents
    with open(output_file) as f:
        lines = f.readlines()
        assert len(lines) == 3  # Header + 2 links
        assert lines[0].strip() == "External URL"
        assert "https://external1.com" in [line.strip() for line in lines]
        assert "https://external2.com" in [line.strip() for line in lines]

def test_skip_non_http_links(caplog):
    """Test that non-HTTP links are properly skipped and logged"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)

    # Enable debug logging for the test
    caplog.set_level(logging.DEBUG)

    # Mock response with various non-HTTP links
    html_content = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <a href="mailto:info@example.com">Email</a>
            <a href="tel:+1234567890">Phone</a>
            <a href="javascript:void(0)">JS Link</a>
        </body>
    </html>
    """
    
    responses.add(
        responses.GET,
        'https://example.com',
        body=html_content,
        status=200,
        content_type='text/html'
    )

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            'https://example.com',
            body=html_content,
            status=200,
            content_type='text/html'
        )
        crawler.crawl()

        # Check that appropriate messages were logged
        assert 'Skipping non-HTTP link: mailto:info@example.com' in caplog.text
        assert 'Skipping non-HTTP link: tel:+1234567890' in caplog.text
        assert 'Skipping non-HTTP link: javascript:void(0)' in caplog.text

def test_url_utility_methods():
    """Test URL utility methods with invalid inputs"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)

    # Test clean_url with invalid URL
    assert crawler.clean_url(None) is None
    assert crawler.clean_url('') is None
    assert crawler.clean_url('not-a-url') is None

    # Test is_internal_url with invalid URL
    assert not crawler.is_internal_url(None)
    assert not crawler.is_internal_url('')
    assert not crawler.is_internal_url('not-a-url')

    # Test is_external_url with invalid URL
    assert not crawler.is_external_url(None)
    assert not crawler.is_external_url('')
    assert not crawler.is_external_url('not-a-url')
