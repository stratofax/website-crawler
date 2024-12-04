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
Run the crawler with:
```bash
poetry run python crawler.py [domain]
```

Example:
```bash
poetry run python crawler.py www.example.com
```

This will create a CSV file named with the domain and current timestamp (e.g., `www.example.com_2024-01-23T1430.csv`).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
