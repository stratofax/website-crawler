# Website Crawler

A Python-based website crawler that recursively visits all pages within a specified subdomain and generates a CSV report containing:
- Page URL
- Page Title
- HTTP Status Code

The output file is automatically named using the domain and current timestamp (e.g., `www.example.com_2024-01-23T1430.csv`).

## Requirements
- Python 3.9 or higher
- Poetry (dependency management)

## Installation
1. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Clone this repository and install the package:
```bash
git clone <repository-url>
cd website-crawler
poetry install
```

## Usage
The crawler can be run using Poetry:
```bash
poetry run crawler [-h] [-e] [-v] [-r] [-p] domain
```

### Arguments

- `domain`: Domain to crawl (e.g., example.com)

### Options

- `-h, --help`: Show help message and exit
- `-e, --external-links`: Check for external links on the domain. When enabled, generates a separate CSV file with external links found on each page
- `-v, --verbose`: Enable verbose output. Shows detailed debugging information during crawling
- `-r, --recursive`: Recursively crawl internal links. When disabled (default), only crawls the specified page
- `-p, --pages`: Only crawl web pages (HTML, PHP, etc.) and skip other file types. Recognized page types include files ending in: /, .html, .htm, .php, .asp, .aspx, .jsp, .shtml, .phtml, .xhtml, .jspx, .do, .cfm, and .cgi

### Examples

Basic crawl of a single page:
```bash
poetry run crawler example.com
```

Recursively crawl a domain and collect external links with verbose output:
```bash
poetry run crawler example.com -e -v -r
```

### Output Files

The crawler generates one of two types of CSV files:

1. Standard crawl results (default):
   - Filename format: `domain_YYYY-MM-DDThhmm.csv`
   - Contains: URL, page title, and HTTP status for each crawled page

2. External links report (when using -e flag):
   - Filename format: `domain_YYYY-MM-DDThhmm_external_links.csv`
   - Contains: Source URL and all external links found on that page

## Testing

Run the test suite using Poetry:
```bash
poetry run pytest
```

For test coverage report:
```bash
poetry run pytest --cov=src --cov-report=term-missing
```

The test suite includes:
- Unit tests for the crawler CLI interface
- Unit tests for the website crawler functionality
- Coverage reporting to identify untested code

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
