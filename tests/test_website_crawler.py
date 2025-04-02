import pytest
from src.website_crawler import WebsiteCrawler, URLProcessingError
from urllib.parse import urlparse
import responses
import tempfile
import os
import csv
from unittest.mock import patch, MagicMock
from requests.exceptions import RequestException
import requests


@pytest.fixture
def crawler_instance():
    """Fixture to create a WebsiteCrawler instance for testing."""
    crawler = WebsiteCrawler("example.com")
    return crawler


def test_init():
    """Test WebsiteCrawler initialization"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)
    assert crawler.domain == domain
    assert crawler.base_url == f"https://{domain}"
    assert len(crawler.visited_urls) == 0
    assert len(crawler.results) == 0
    assert len(crawler.external_links) == 0

def test_process_url():
    """Test URL processing with various inputs"""
    crawler = WebsiteCrawler("example.com")
    
    # Test valid internal URL
    url, is_internal = crawler.process_url("https://example.com/page")
    assert url == "https://example.com/page"
    assert is_internal is True
    
    # Test valid external URL
    url, is_internal = crawler.process_url("https://external.com/page")
    assert url == "https://external.com/page"
    assert is_internal is False
    
    # Test URL cleaning (remove query params and fragments)
    url, _ = crawler.process_url("https://example.com/page?param=1#section")
    assert url == "https://example.com/page"

def test_process_url_errors():
    """Test URL processing error cases"""
    crawler = WebsiteCrawler("example.com")
    
    # Test empty URL
    with pytest.raises(URLProcessingError, match="Empty URL"):
        crawler.process_url("")
    
    # Test invalid protocol
    with pytest.raises(URLProcessingError, match="Unsupported protocol"):
        crawler.process_url("ftp://example.com")
    
    # Test malformed URL
    with pytest.raises(URLProcessingError, match="Invalid URL format"):
        crawler.process_url("not-a-url")
    
    # Test URL without scheme
    with pytest.raises(URLProcessingError, match="Invalid URL format"):
        crawler.process_url("example.com/page")

@responses.activate
def test_crawl_page():
    """Test crawling a single page"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)
    
    # Mock response with some links
    html_content = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <a href="https://example.com/page1">Page 1</a>
            <a href="https://example.com/page2">Page 2</a>
            <a href="https://external.com">External</a>
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
    
    # Crawl the page
    crawler.crawl()
    
    # Check results
    assert len(crawler.visited_urls) == 1
    assert len(crawler.results) == 1
    assert crawler.results[0][0] == 'https://example.com'
    assert crawler.results[0][1] == 'Test Page'
    assert crawler.results[0][2] == 200

@responses.activate
def test_recursive_crawl():
    """Test recursive crawling of pages"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)
    
    # Mock responses for multiple pages
    responses.add(
        responses.GET,
        'https://example.com',
        body="""
        <html>
            <head><title>Home</title></head>
            <body>
                <a href="https://example.com/page1">Page 1</a>
                <a href="https://external.com">External</a>
            </body>
        </html>
        """,
        status=200
    )
    
    responses.add(
        responses.GET,
        'https://example.com/page1',
        body="""
        <html>
            <head><title>Page 1</title></head>
            <body>
                <a href="https://example.com/page2">Page 2</a>
            </body>
        </html>
        """,
        status=200
    )
    
    responses.add(
        responses.GET,
        'https://example.com/page2',
        body="""
        <html>
            <head><title>Page 2</title></head>
            <body>
                <a href="https://example.com">Home</a>
            </body>
        </html>
        """,
        status=200
    )
    
    # Test recursive crawl
    crawler.crawl(recursive=True)
    
    # Check that all pages were visited
    assert len(crawler.visited_urls) == 3
    assert 'https://example.com' in crawler.visited_urls
    assert 'https://example.com/page1' in crawler.visited_urls
    assert 'https://example.com/page2' in crawler.visited_urls
    
    # Check that titles were collected
    titles = [r[1] for r in crawler.results]
    assert 'Home' in titles
    assert 'Page 1' in titles
    assert 'Page 2' in titles

@responses.activate
def test_external_links_collection():
    """Test collection of external links"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)
    
    # Mock response with external links
    responses.add(
        responses.GET,
        'https://example.com',
        body="""
        <html>
            <head><title>Test Page</title></head>
            <body>
                <a href="https://external1.com">External 1</a>
                <a href="https://external2.com">External 2</a>
                <a href="https://example.com/internal">Internal</a>
            </body>
        </html>
        """,
        status=200
    )
    
    # Crawl with external link collection
    crawler.crawl(collect_external=True)
    
    # Check external links were collected
    assert len(crawler.external_links) == 2
    assert 'https://external1.com' in crawler.external_links
    assert 'https://external2.com' in crawler.external_links

@responses.activate
def test_crawl_page_with_error(caplog):
    """Test crawling a page that returns an error"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)
    
    # Mock response with error
    responses.add(
        responses.GET,
        'https://example.com',
        status=404
    )
    
    # Crawl the page and check error was logged
    crawler.crawl()
    assert "HTTP Error crawling https://example.com: 404" in caplog.text

@responses.activate
def test_crawl_page_with_network_error(caplog):
    """Test crawling a page that has network errors"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)
    
    # Mock a network error
    responses.add(
        responses.GET,
        'https://example.com',
        body=RequestException("Network error")
    )
    
    # Crawl the page and check error was logged
    crawler.crawl()
    assert "Error crawling https://example.com" in caplog.text

@responses.activate
def test_crawl_page_with_invalid_html():
    """Test crawling a page with invalid HTML"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)
    
    # Mock response with invalid HTML
    responses.add(
        responses.GET,
        'https://example.com',
        body="<html><head>No title</head><body>Invalid HTML",
        status=200
    )
    
    # Crawl the page
    crawler.crawl()
    
    # Check that page was processed despite invalid HTML
    assert len(crawler.results) == 1
    assert crawler.results[0][1] == "No title"  # Default title for pages without title tag

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
            
            # Check header and content
            assert rows[0] == ["URL", "Title", "Status Code"]
            assert len(rows) == 4  # Header + 3 results
            assert rows[1] == ["https://example.com", "Home Page", "200"]
            
    finally:
        os.unlink(output_file)

@responses.activate
def test_crawl_page_with_missing_title():
    """Test crawling a page without a title tag"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)
    
    # Mock response with HTML missing title tag
    responses.add(
        responses.GET,
        'https://example.com',
        body="<html><body>No title tag here</body></html>",
        status=200
    )
    
    # Crawl the page
    crawler.crawl()
    
    # Check that page was processed with default title
    assert len(crawler.results) == 1
    assert crawler.results[0][1] == "No title"

@responses.activate
def test_crawl_page_with_relative_links():
    """Test handling of relative links"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)
    
    # Mock response with relative links
    responses.add(
        responses.GET,
        'https://example.com',
        body="""
        <html>
            <head><title>Test Page</title></head>
            <body>
                <a href="/page1">Relative Link 1</a>
                <a href="page2">Relative Link 2</a>
                <a href="../page3">Relative Link 3</a>
            </body>
        </html>
        """,
        status=200
    )
    
    # Mock responses for relative links
    responses.add(
        responses.GET,
        'https://example.com/page1',
        body="<html><head><title>Page 1</title></head></html>",
        status=200
    )
    
    responses.add(
        responses.GET,
        'https://example.com/page2',
        body="<html><head><title>Page 2</title></head></html>",
        status=200
    )
    
    responses.add(
        responses.GET,
        'https://example.com/page3',
        body="<html><head><title>Page 3</title></head></html>",
        status=200
    )
    
    # Test recursive crawl with relative links
    crawler.crawl(recursive=True)
    
    # Check that relative links were properly resolved and crawled
    assert len(crawler.visited_urls) == 4
    assert 'https://example.com' in crawler.visited_urls
    assert 'https://example.com/page1' in crawler.visited_urls
    assert 'https://example.com/page2' in crawler.visited_urls
    assert 'https://example.com/page3' in crawler.visited_urls

@responses.activate
def test_crawl_page_with_malformed_links():
    """Test handling of malformed links"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)
    
    # Mock response with malformed links
    responses.add(
        responses.GET,
        'https://example.com',
        body="""
        <html>
            <head><title>Test Page</title></head>
            <body>
                <a href="javascript:void(0)">JavaScript Link</a>
                <a href="mailto:test@example.com">Email Link</a>
                <a href="#">Hash Link</a>
                <a href="">Empty Link</a>
                <a>No Href</a>
            </body>
        </html>
        """,
        status=200
    )
    
    # Crawl the page
    crawler.crawl()
    
    # Check that the page was processed without errors
    assert len(crawler.visited_urls) == 1
    assert len(crawler.results) == 1
    assert crawler.results[0][0] == 'https://example.com'

@responses.activate
def test_skip_already_visited():
    """Test that pages aren't crawled multiple times"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)
    
    # Mock response with a link to self
    responses.add(
        responses.GET,
        'https://example.com',
        body="""
        <html>
            <head><title>Test Page</title></head>
            <body>
                <a href="https://example.com">Self Link</a>
                <a href="https://example.com/">Root with slash</a>
            </body>
        </html>
        """,
        status=200
    )
    
    # Crawl the page
    crawler.crawl(recursive=True)
    
    # Check that the page was only crawled once
    assert len(crawler.visited_urls) == 1
    assert len(crawler.results) == 1

def test_save_external_links():
    """Test saving external links to a CSV file"""
    crawler = WebsiteCrawler("example.com")
    crawler.external_links = {
        "https://external1.com",
        "https://external2.com"
    }
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
        output_file = tmp_file.name
    
    try:
        # Save external links
        crawler.save_external_links_results(output_file)
        
        # Read and verify the CSV content
        with open(output_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            # Check content
            assert rows[0] == ["External URL"]
            assert len(rows) == 3  # Header + 2 external links
            urls = {rows[1][0], rows[2][0]}
            assert urls == crawler.external_links
            
    finally:
        os.unlink(output_file)

@responses.activate
def test_check_external_links():
    """Test the check_external_links method"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)

    # Mock response with external links
    responses.add(
        responses.GET,
        'https://example.com',
        body="""
        <html>
            <head><title>Test Page</title></head>
            <body>
                <a href="https://external1.com">External 1</a>
                <a href="https://example.com/page1">Internal 1</a>
            </body>
        </html>
        """,
        status=200
    )

    responses.add(
        responses.GET,
        'https://example.com/page1',
        body="""
        <html>
            <head><title>Page 1</title></head>
            <body>
                <a href="https://external2.com">External 2</a>
            </body>
        </html>
        """,
        status=200
    )

    # Test check_external_links
    crawler.check_external_links()

    assert len(crawler.external_links) == 2
    assert len(crawler.visited_urls) == 2

@responses.activate
def test_crawl_page_with_non_http_links():
    """Test handling of non-HTTP links in crawl_page"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)

    # Mock response with non-HTTP links
    responses.add(
        responses.GET,
        'https://example.com',
        body="""
        <html>
            <head><title>Test Page</title></head>
            <body>
                <a href="mailto:test@example.com">Email</a>
                <a href="tel:+1234567890">Phone</a>
                <a href="javascript:void(0)">JavaScript</a>
                <a href="ftp://example.com/file">FTP</a>
            </body>
        </html>
        """,
        status=200
    )

    # Test crawl_page
    crawler.crawl_page('https://example.com')

    assert len(crawler.visited_urls) == 1
    assert len(crawler.results) == 1
    assert crawler.results[0][1] == "Test Page"

@responses.activate
def test_crawl_page_with_none_url():
    """Test crawl_page with None URL from process_url"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)

    # Mock process_url to return None
    def mock_process_url(url):
        if url == "https://example.com/invalid":
            return None, False
        return url, True

    crawler.process_url = mock_process_url

    # Test crawl_page with None URL
    crawler.crawl_page("https://example.com/invalid")

    assert len(crawler.visited_urls) == 0
    assert len(crawler.results) == 0

@responses.activate
def test_crawl_page_recursive_already_visited():
    """Test recursive crawl_page with already visited URLs"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)

    # Add a URL to visited_urls
    crawler.visited_urls.add("https://example.com/page1")

    # Mock response with link to already visited page
    responses.add(
        responses.GET,
        'https://example.com',
        body="""
        <html>
            <head><title>Test Page</title></head>
            <body>
                <a href="https://example.com/page1">Already Visited</a>
            </body>
        </html>
        """,
        status=200
    )

    # Test crawl_page
    crawler.crawl_page('https://example.com', recursive=True)

    assert len(crawler.visited_urls) == 2
    assert "https://example.com/page1" in crawler.visited_urls

@responses.activate
def test_crawl_page_with_invalid_url_processing():
    """Test crawl_page with invalid URL that fails processing"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)

    # Mock process_url to raise an exception
    def mock_process_url(url):
        if url == "https://example.com/invalid":
            raise URLProcessingError("Invalid URL")
        return url, True

    crawler.process_url = mock_process_url

    # Test crawl_page with invalid URL
    try:
        crawler.crawl_page("https://example.com/invalid")
    except URLProcessingError:
        pass

    assert len(crawler.visited_urls) == 0
    assert len(crawler.results) == 0

@responses.activate
def test_crawl_page_with_general_exception():
    """Test crawl_page with a general exception during processing"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)

    # Mock requests.get to raise a general exception
    def mock_get(url, **kwargs):
        raise Exception("General error")

    crawler.session.get = mock_get

    # Test crawl_page with URL that will cause an error
    crawler.crawl_page("https://example.com")

    assert len(crawler.visited_urls) == 1
    assert len(crawler.results) == 1
    assert crawler.results[0][1] == "Error"
    assert crawler.results[0][2] == 0

@responses.activate
def test_crawl_page_with_connection_error():
    """Test crawl_page with a connection error"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)

    # Mock requests.get to raise a connection error
    def mock_get(url, **kwargs):
        raise requests.exceptions.ConnectionError("Connection failed")

    crawler.session.get = mock_get

    # Test crawl_page with URL that will cause a connection error
    crawler.crawl_page("https://example.com")

    assert len(crawler.visited_urls) == 1
    assert len(crawler.results) == 1
    assert crawler.results[0][1] == "Error"
    assert crawler.results[0][2] == 0

def test_is_page():
    """Test URL page type detection"""
    crawler = WebsiteCrawler("example.com")
    
    # Test URLs ending with '/'
    assert crawler.is_page("https://example.com/") is True
    assert crawler.is_page("https://example.com/path/") is True
    
    # Test URLs with page extensions
    assert crawler.is_page("https://example.com/page.html") is True
    assert crawler.is_page("https://example.com/page.php") is True
    assert crawler.is_page("https://example.com/page.asp") is True
    
    # Test URLs without extensions
    assert crawler.is_page("https://example.com/about") is True
    
    # Test non-page URLs
    assert crawler.is_page("https://example.com/image.jpg") is False
    assert crawler.is_page("https://example.com/doc.pdf") is False
    
    # Test invalid URLs
    assert crawler.is_page("not-a-url") is False

@responses.activate
def test_crawl_pages_only():
    """Test crawling with pages_only flag"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)
    
    # Mock response with various link types
    html_content = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <a href="https://example.com/page1.html">Page 1</a>
            <a href="https://example.com/image.jpg">Image</a>
            <a href="https://example.com/doc.pdf">Document</a>
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
    
    # Add mock response for page1.html
    responses.add(
        responses.GET,
        'https://example.com/page1.html',
        body='<html><head><title>Page 1</title></head><body>Test</body></html>',
        status=200,
        content_type='text/html'
    )
    
    # Crawl with pages_only=True
    crawler.crawl(recursive=True, pages_only=True)
    
    # Should only visit the base URL and page1.html
    assert len(crawler.visited_urls) == 2
    assert 'https://example.com' in crawler.visited_urls
    assert 'https://example.com/page1.html' in crawler.visited_urls
    assert 'https://example.com/image.jpg' not in crawler.visited_urls
    assert 'https://example.com/doc.pdf' not in crawler.visited_urls

@responses.activate
def test_crawl_page_http_error():
    """Test crawling a page that returns specific HTTP error codes"""
    domain = "example.com"
    crawler = WebsiteCrawler(domain)
    
    # Mock a 404 response
    responses.add(
        responses.GET,
        'https://example.com/not-found',
        status=404
    )
    
    # Mock a 500 response
    responses.add(
        responses.GET,
        'https://example.com/server-error',
        status=500
    )
    
    # Test 404 error
    crawler.crawl_page('https://example.com/not-found')
    assert ('https://example.com/not-found', 'Error', 404) in crawler.results
    
    # Test 500 error
    crawler.crawl_page('https://example.com/server-error')
    assert ('https://example.com/server-error', 'Error', 500) in crawler.results

def test_crawl_with_non_page_skipped(crawler_instance):
    """Test that non-page URLs are skipped when pages_only is True."""
    base_url = "http://example.com/page"
    non_page_url = "http://example.com/image.jpg"
    crawler_instance.base_url = base_url
    crawler_instance.domain = "example.com"
    crawler_instance.visited_urls = set()

    # Mock requests.get to return minimal HTML with a link to a non-page
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {'Content-Type': 'text/html'}
    mock_response.text = f'<html><body><a href="{non_page_url}">Non-page</a></body></html>'
    mock_response.url = base_url # Set the final URL after potential redirects

    with patch('requests.get', return_value=mock_response):
        crawler_instance.crawl(pages_only=True, recursive=False)

    # Assert that the base URL was visited, but the non-page URL was not
    assert base_url in crawler_instance.visited_urls
    assert non_page_url not in crawler_instance.visited_urls
    # Check results if needed, e.g., that the non-page URL isn't in results
    assert not any(url == non_page_url for url, _, _ in crawler_instance.results)

def test_is_page_exception(crawler_instance, caplog):
    """Test that is_page handles exceptions gracefully."""
    malformed_url = "http://[::1]:80" # Example that might cause urlparse issues on some systems or is invalid

    # Fix: Patch the urlparse at the correct import location
    with patch('src.website_crawler.urlparse', side_effect=ValueError("Mock parsing error")):
        assert not crawler_instance.is_page(malformed_url)

    # Check that a debug message was logged
    assert "Error checking if URL is page: Mock parsing error" in caplog.text

def test_save_results_empty(crawler_instance, tmp_path):
    """Test saving results when no pages were crawled."""
    # Create a temporary file
    output_file = tmp_path / "results.csv"
    
    # Ensure results is empty
    crawler_instance.results = []
    
    # Save results
    crawler_instance.save_results(output_file)
    
    # Check that the file was created
    assert output_file.exists()
    # Fix: Even with no results, the CSV header is still written
    # So we check that only the header exists (URL,Title,Status Code)
    with open(output_file, 'r') as f:
        content = f.read()
        assert content.strip() == "URL,Title,Status Code"
