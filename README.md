# WebDataScraper 🕸️

## Overview

WebDataScraper is a configurable Python web scraper designed for portfolio and real-world automation tasks.  
It can extract structured data from websites using CSS selectors, follow pagination links, and export results to JSON and CSV.

This project demonstrates:

- Python scripting and automation  
- Web scraping with `requests` and `BeautifulSoup`  
- Config-driven architecture (no hard-coded site logic)  
- Clean code structure and CLI interface  
- Data export to JSON and CSV  

> **Important:** Always respect website terms of service and robots.txt.  
> The included example uses [quotes.toscrape.com](https://quotes.toscrape.com/), a site created specifically for scraping practice.

---

## Features

- 🧩 Config-based scraping (no code changes needed for new sites)  
- 📄 CSS selector support for flexible extraction  
- 📑 Pagination via "next page" links  
- 🕒 Optional delay between requests (be a good net citizen)  
- 💾 Export to both JSON and CSV  
- 🖥️ Simple CLI with `--config` and `--output-base` options  

---

## Installation

```bash
git clone https://github.com/SANTIK-Genius/WebDataScraper.git
cd WebDataScraper

pip install -r requirements.txt
```

---

## Usage

```bash
python scraper.py --config config_example.json --output-base output/quotes
```

This will:

- Fetch several pages from `quotes.toscrape.com`  
- Extract quote text, author and tags  
- Save:  
  - `output/quotes.json`  
  - `output/quotes.csv`  

---

## Configuration

The scraper is powered by a JSON config file. Example:

```json
{
  "start_url": "https://quotes.toscrape.com/",
  "item_selector": "div.quote",
  "fields": {
    "text": { "selector": "span.text" },
    "author": { "selector": "small.author" },
    "tags": { "selector": "div.tags a.tag", "multiple": true }
  },
  "pagination": {
    "next_page_selector": "li.next a",
    "max_pages": 5
  },
  "delay_seconds": 1.0
}
```

- `start_url` – first page to scrape  
- `item_selector` – CSS selector for each item block  
- `fields` – which data to extract from each item  
- `pagination.next_page_selector` – selector for the “next page” link  
- `pagination.max_pages` – safety limit for the number of pages  
- `delay_seconds` – delay between requests in seconds  

---

## Project Structure

```text
WebDataScraper/
├── scraper.py              # main scraper script
├── config_example.json     # example configuration
├── requirements.txt        # dependencies
└── README.md               # project documentation
```

---

## License

MIT (or your preferred license)
