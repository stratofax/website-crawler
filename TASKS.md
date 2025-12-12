# To Do: website crawler

## Features

- [ ] Add default output directory
- [ ] Add option to specify output directory
- [ ] Save output directory settings to config file
- [ ] Add option to specify output file name
- [ ] Add option to log all links (internal and external)
- [ ] Make page extensions configurable via config file or command line option

## Testing

- [x] 100% test coverage

## Refactor

- [x] Remove duplicate `crawl_page()` method (lines 220-274)
  - This is dead code superseded by `_crawl_page()`
  - Only used by `check_external_links()` which is itself unused in production
  - Does NOT support `pages_only` filtering
  - Inefficiently calls `process_url()` twice per link
- [x] Remove unused `check_external_links()` method (lines 211-218)
  - Only called in tests, never used in production CLI
  - Functionality replaced by `crawl(collect_external=True, recursive=True)`
- [x] Update test suite to use `crawl()` instead of legacy methods
  - Replace `test_check_external_links()` to use the modern API

### High Priority

- [ ] Extract magic number for sleep delay to a class constant
  - Location: src/website_crawler.py:192
  - Reason: Hardcoded `time.sleep(1)` makes the delay difficult to configure for testing or different use cases
  - Suggested improvement: Add `REQUEST_DELAY = 1.0` as a class constant or make it configurable via constructor

- [ ] Add timeout parameter to HTTP requests
  - Location: src/website_crawler.py:162
  - Reason: `self.session.get(clean_url)` has no timeout, which can cause the crawler to hang indefinitely
  - Suggested improvement: Add `timeout=30` parameter and make it configurable

- [ ] Add retry logic with exponential backoff for failed requests
  - Location: src/website_crawler.py:162-190
  - Reason: Temporary network failures or rate limiting can cause crawls to fail unnecessarily
  - Suggested improvement: Implement retry mechanism with configurable max retries (e.g., 3) and exponential backoff

- [ ] Improve error handling for HTTP errors
  - Location: src/website_crawler.py:185-190
  - Reason: HTTP errors append to results with status codes, but network errors use status code 0, which is inconsistent
  - Suggested improvement: Distinguish between different error types (404, 500, timeout, network) more clearly in results

### Medium Priority

- [ ] Extract User-Agent string to a class constant
  - Location: src/website_crawler.py:52
  - Reason: Hardcoded User-Agent string is difficult to update and not easily configurable
  - Suggested improvement: Add `USER_AGENT` as a class constant or configuration parameter

- [ ] Add type hints to all method return values
  - Location: src/website_crawler.py:120, 147, 194, 202
  - Reason: Methods like `crawl()`, `_crawl_page()`, `save_results()`, and `save_external_links_results()` are missing return type hints
  - Suggested improvement: Add `-> None` to all void methods for consistency

- [ ] Extract duplicate CSV encoding parameter
  - Location: src/website_crawler.py:196, 204
  - Reason: `encoding='utf-8'` is used in `save_results()` but missing in `save_external_links_results()`
  - Suggested improvement: Add `encoding='utf-8'` to `save_external_links_results()` for consistency

- [ ] Refactor duplicate file output logic into helper method
  - Location: src/crawler.py:73-76 and 79-81
  - Reason: Similar code for constructing filenames and logging appears twice
  - Suggested improvement: Extract common filename generation pattern into a helper function

- [ ] Consolidate logging setup in crawler.py
  - Location: src/crawler.py:10-26
  - Reason: `setup_logging()` configures root logger but could be more robust
  - Suggested improvement: Check if handlers already exist before adding to avoid duplicate handlers in testing

- [ ] Simplify URL cleaning logic
  - Location: src/website_crawler.py:69-76
  - Reason: Path normalization logic is somewhat convoluted with multiple conditionals
  - Suggested improvement: Simplify using `path.rstrip('/') if path and path != '/' else ''`

- [ ] Add logging for skipped URLs in pages_only mode
  - Location: src/website_crawler.py:154-157
  - Reason: Non-page URLs are silently skipped when pages_only=True, making debugging difficult
  - Suggested improvement: Already has debug logging, but could add counter of skipped URLs to final summary

### Low Priority

- [ ] Make PAGE_EXTENSIONS configurable
  - Location: src/website_crawler.py:14-29
  - Reason: Currently hardcoded as a module constant, limiting flexibility
  - Suggested improvement: Allow passing custom extensions via constructor or configuration file (as mentioned in TASKS.md Features)

- [ ] Rename `is_page()` to `is_web_page()` for clarity
  - Location: src/website_crawler.py:87
  - Reason: More descriptive name that clearly indicates it checks for web pages vs. other file types
  - Suggested improvement: Rename method and update all references

- [ ] Improve CSV header naming consistency
  - Location: src/website_crawler.py:198, 206
  - Reason: Headers use different styles: 'URL' vs 'External URL' (could be 'URL' and 'Title' or 'Page URL' and 'External URL')
  - Suggested improvement: Use consistent naming convention (e.g., 'Page URL', 'Page Title', 'Status Code' and 'External URL')

- [ ] Add docstrings to exception classes
  - Location: src/website_crawler.py:31-37
  - Reason: Custom exception classes lack detailed documentation
  - Suggested improvement: Add docstrings explaining when each exception should be raised

- [ ] Consider using pathlib for file operations
  - Location: src/website_crawler.py:196, 204
  - Reason: Using traditional `open()` instead of more modern pathlib approach
  - Suggested improvement: Could use `Path(output_file).write_text()` pattern for more modern Python style

- [ ] Add validation for domain parameter
  - Location: src/website_crawler.py:40-44
  - Reason: No validation that domain is a valid hostname format
  - Suggested improvement: Add basic validation to catch common mistakes (e.g., including protocol, empty string)

- [ ] Extract duplicate test fixtures
  - Location: tests/test_website_crawler.py:14-17 and tests/test_crawler.py:11-17
  - Reason: Similar fixtures could be consolidated in conftest.py
  - Suggested improvement: Move common fixtures to conftest.py for reuse
