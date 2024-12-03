# Website Crawler

A Python-based website crawler that recursively visits all pages within a specified subdomain and generates a CSV report containing:
- Page URL
- Page Title
- HTTP Status Code

## Requirements
- Python 3.8 or higher
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
Run the crawler with:
```bash
poetry run python crawler.py [domain] [output_file]
```

Example:
```bash
poetry run python crawler.py www.example.com results.csv
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
