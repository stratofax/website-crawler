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

To run this project, you need to have Python 3.10 or higher installed on your system. We recommend using [Poetry](https://python-poetry.org/) for dependency management and virtual environment management.

### Mac

On macOS, the default system Python, 3.9, installed via the Xcode Command Line Tools, might cause issues with Poetry installation due to limitations in creating virtual environments. It's recommended to install and use a more recent version of Python managed by [Homebrew](https://brew.sh/):

1.  **Install Homebrew (if not already installed):**
    Follow the instructions on the [Homebrew website](https://brew.sh/).

2.  **Install Python via Homebrew:**
    ```bash
    brew install python
    ```

3.  **Configure your shell (e.g., zsh) to prioritize Homebrew Python:**
    Add the following line to your shell configuration file (`~/.zshrc` for zsh, `~/.bash_profile` or `~/.bashrc` for bash). This ensures the Homebrew-installed Python is used instead of the system Python.

    ```bash
    # For zsh (~/.zshrc) or bash (~/.bash_profile)
    # Make sure /opt/homebrew/bin (Apple Silicon) or /usr/local/bin (Intel) is at the start of your PATH
    export PATH="/opt/homebrew/bin:$PATH"
    ```
    *Note: The exact path (`/opt/homebrew/bin` or `/usr/local/bin`) depends on your Mac's architecture (Apple Silicon or Intel) and your Homebrew installation.*

    Apply the changes by running `source ~/.zshrc` (or your respective config file) or by opening a new terminal window. Verify the correct Python is being used with `which python3` (it should point to the Homebrew path) and `python3 --version`.

### General Installation Steps

1.  **Install Poetry:**
    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

2.  **Clone this repository into the current directory, and install the package:**
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
