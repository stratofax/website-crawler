import pytest
from website_crawler import WebsiteCrawler
from urllib.parse import urlparse

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
