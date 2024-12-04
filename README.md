# Website Crawler

A Python-based website crawler that recursively visits all pages within a specified subdomain and generates a CSV report containing:
- Page URL
- Page Title
- HTTP Status Code

The output file is automatically named using the domain and current timestamp (e.g., `www.example.com_2024-01-23T1430.csv`).

## Requirements
- Python 3.9 or higher
- Poetry (dependency management)

## Setup
1. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

## Usage
```bash
poetry run python src/crawler.py [-h] [-e] [-v] domain
```

### Arguments

- `domain`: Domain to crawl (e.g., example.com)

### Options

- `-h, --help`: Show help message and exit
- `-e, --external-links`: Check for external links on the domain. This will recursively crawl all internal pages and collect links to external domains.
- `-v, --verbose`: Enable verbose output. Shows detailed debugging information during crawling.

### Examples

Basic crawl of a domain:
```bash
poetry run python src/crawler.py example.com
```

Collect external links with verbose output:
```bash
poetry run python src/crawler.py example.com -e -v
```

The output file is automatically named using the domain and current timestamp (e.g., `example.com_2024-01-23T1430.csv`).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
