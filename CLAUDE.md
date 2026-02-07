# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands

- **Install dependencies:** `poetry install`
- **Run crawler:** `poetry run crawler <domain>` (e.g., `poetry run crawler example.com -e -v -r -p`)
- **Run all tests:** `poetry run pytest`
- **Run tests with coverage:** `poetry run pytest --cov=src --cov-report=term-missing`
- **Run a single test:** `poetry run pytest tests/test_website_crawler.py::test_crawl_page`
- **Format code:** `poetry run autopep8 --in-place --recursive src/ tests/`

## Architecture

This is a Python CLI tool using Poetry for dependency management. It crawls websites and generates CSV reports.

### Two-layer design

- **`src/crawler.py`** — CLI entry point (registered as `crawler` script in pyproject.toml). Handles argument parsing, logging setup, and orchestrates the `WebsiteCrawler`. The `main()` function is the entry point.
- **`src/website_crawler.py`** — Core crawling logic. The `WebsiteCrawler` class manages HTTP sessions, URL processing, recursive page traversal, and CSV output. Contains two crawl code paths:
  - `_crawl_page()` — Primary internal crawl method used by `crawl()`, supports `pages_only` filtering
  - `crawl_page()` — Legacy public method used by `check_external_links()`, does not support `pages_only`

### Key patterns

- HTTP mocking in tests uses the `responses` library (decorator-based: `@responses.activate`)
- URL normalization strips query params, fragments, and trailing slashes
- The crawler enforces a 1-second delay between requests (`time.sleep(1)`)
- Custom exceptions: `URLProcessingError`, `CrawlingError` (defined but unused)

## Testing

Tests are in `tests/` with `conftest.py` adding the project root to `sys.path`. Two test files mirror the two source modules:
- `tests/test_crawler.py` — Tests CLI argument handling and logging setup using `unittest.mock`
- `tests/test_website_crawler.py` — Tests crawling behavior using `responses` library for HTTP mocking
