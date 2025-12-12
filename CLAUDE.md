# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python-based website crawler that recursively visits pages within a specified subdomain and generates CSV reports. The crawler can collect page metadata (title, status code) and optionally track external links.

## Development Commands

### Setup
```bash
poetry install
```

### Running the Crawler
```bash
# Basic single-page crawl
poetry run crawler example.com

# Recursive crawl with external links and verbose output
poetry run crawler example.com -e -v -r

# Only crawl web pages (skip PDFs, images, etc.)
poetry run crawler example.com -r -p
```

### Testing
```bash
# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=src --cov-report=term-missing

# Run a single test file
poetry run pytest tests/test_website_crawler.py

# Run a specific test
poetry run pytest tests/test_website_crawler.py::test_crawl_page
```

### Code Formatting
```bash
poetry run autopep8 --in-place --recursive src/ tests/
```

## Architecture

### Core Components

**src/crawler.py** - CLI entry point
- Argument parsing and logging configuration
- Coordinates the crawl operation and output file generation
- Filename format: `domain_YYYY-MM-DDThhmm.csv` (or `_external_links.csv` when using `-e`)

**src/website_crawler.py** - Core crawling logic
- `WebsiteCrawler` class handles all crawling operations
- Uses requests + BeautifulSoup4 for HTTP and HTML parsing
- Maintains visited URLs set to prevent duplicate crawls
- URL processing normalizes URLs by removing query params, fragments, and trailing slashes

### Crawl Modes

**Non-recursive (default)**: Crawls only the base URL, does not follow internal links

**Recursive (`-r`)**: Follows all internal links recursively until entire subdomain is crawled

**Pages-only (`-p`)**: Skips non-page file types (PDFs, images, etc.). Page types defined in `PAGE_EXTENSIONS` constant include: html, php, asp, jsp, and several others

**External links (`-e`)**: Collects external links found on pages (does not crawl them)

### Key Implementation Details

- URL normalization removes query parameters, fragments, and trailing slashes to prevent duplicate visits
- 1-second delay between requests (`time.sleep(1)`) to be polite to servers
- Custom User-Agent header identifies the crawler
- Error handling captures HTTP errors and network exceptions, recording them in results with status code 0
- Uses requests.Session for connection pooling across requests
- `_crawl_page()` is the internal recursive method used by `crawl()` to visit pages

## Testing

Test suite uses pytest with responses library for HTTP mocking. Test coverage is ~99%. Tests cover:
- URL processing and normalization
- Recursive vs non-recursive crawling
- External link collection
- Error handling (HTTP errors, network errors, malformed HTML)
- Pages-only filtering
- CSV output generation

## macOS Python Setup

The project requires Python 3.9+. On macOS, use Homebrew Python instead of system Python to avoid Poetry virtual environment issues:

```bash
brew install python
export PATH="/opt/homebrew/bin:$PATH"  # Apple Silicon
# or export PATH="/usr/local/bin:$PATH"  # Intel
```
