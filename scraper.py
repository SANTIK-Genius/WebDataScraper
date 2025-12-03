#!/usr/bin/env python3
"""

Usage:
    python scraper.py --config config_example.json
"""

import argparse
import csv
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup, Tag


class WebScraper:
	def __init__(self, config: Dict[str, Any]) -> None:
		self.start_url: str = config["start_url"]
		self.item_selector: str = config["item_selector"]
		self.fields: Dict[str, Dict[str, Any]] = config["fields"]
		self.pagination: Dict[str, Any] = config.get("pagination", {})
		self.delay: float = float(config.get("delay_seconds", 1.0))

	def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
		"""Fetch a single page and return BeautifulSoup tree."""
		try:
			resp = requests.get(url, timeout=10)
			resp.raise_for_status()
		except requests.RequestException as exc:
			print(f"[ERROR] Failed to fetch {url}: {exc}")
			return None

		return BeautifulSoup(resp.text, "html.parser")

	def extract_field(self, item: Tag, field_cfg: Dict[str, Any]) -> Any:
		selector = field_cfg["selector"]
		attr = field_cfg.get("attr")  # if None -> text
		multiple: bool = bool(field_cfg.get("multiple", False))

		if multiple:
			elements = item.select(selector)
			if attr:
				values = [el.get(attr, "").strip() for el in elements]
			else:
				values = [el.get_text(strip=True) for el in elements]
			return values

		element = item.select_one(selector)
		if not element:
			return ""
		if attr:
			return element.get(attr, "").strip()
		return element.get_text(strip=True)

	def scrape(self) -> List[Dict[str, Any]]:
		"""Scrape all pages according to config."""
		results: List[Dict[str, Any]] = []

		current_url = self.start_url
		page_index = 1
		max_pages = int(self.pagination.get("max_pages", 0)) or None
		next_selector = self.pagination.get("next_page_selector")

		while current_url:
			print(f"[INFO] Fetching page {page_index}: {current_url}")
			soup = self.fetch_page(current_url)
			if soup is None:
				break

			items = soup.select(self.item_selector)
			print(f"[INFO] Found {len(items)} items on page {page_index}")

			for item in items:
				row: Dict[str, Any] = {}
				for field_name, field_cfg in self.fields.items():
					row[field_name] = self.extract_field(item, field_cfg)
				results.append(row)

			# Pagination
			if max_pages is not None and page_index >= max_pages:
				break

			if not next_selector:
				break

			next_link = soup.select_one(next_selector)
			if not next_link or not next_link.get("href"):
				break

			href = next_link.get("href")
			if href.startswith("http://") or href.startswith("https://"):
				current_url = href
			else:
				# build absolute URL
				if current_url.endswith("/") and href.startswith("/"):
					current_url = current_url.rstrip("/") + href
				elif href.startswith("/"):
					# get base (scheme + host)
					from urllib.parse import urlparse, urlunparse

					parsed = urlparse(current_url)
					base = urlunparse((parsed.scheme, parsed.netloc, "", "", "", ""))
					current_url = base + href
				else:
					if current_url.endswith("/"):
						current_url = current_url + href
					else:
						current_url = current_url.rsplit("/", 1)[0] + "/" + href

			page_index += 1
			time.sleep(self.delay)

		print(f"[INFO] Total items scraped: {len(results)}")
		return results


def save_as_json(rows: List[Dict[str, Any]], path: Path) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	with path.open("w", encoding="utf-8") as f:
		json.dump(rows, f, ensure_ascii=False, indent=2)
	print(f"[INFO] Saved JSON: {path}")


def save_as_csv(rows: List[Dict[str, Any]], path: Path) -> None:
	if not rows:
		print("[WARN] No data to save as CSV.")
		return
	path.parent.mkdir(parents=True, exist_ok=True)
	fieldnames = list(rows[0].keys())
	with path.open("w", encoding="utf-8", newline="") as f:
		writer = csv.DictWriter(f, fieldnames=fieldnames)
		writer.writeheader()
		for row in rows:
			# convert lists to comma-separated strings
			row_to_write = {
				k: ", ".join(v) if isinstance(v, list) else v for k, v in row.items()
			}
			writer.writerow(row_to_write)
	print(f"[INFO] Saved CSV: {path}")


def load_config(path: Path) -> Dict[str, Any]:
	with path.open("r", encoding="utf-8") as f:
		return json.load(f)


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Configurable web scraper for portfolio projects."
	)
	parser.add_argument(
		"--config",
		"-c",
		type=str,
		required=True,
		help="Path to JSON config file.",
	)
	parser.add_argument(
		"--output-base",
		"-o",
		type=str,
		default="output/data",
		help="Base path for output files (without extension).",
	)
	return parser.parse_args()


def main() -> None:
	args = parse_args()
	config_path = Path(args.config)
	config = load_config(config_path)

	scraper = WebScraper(config)
	rows = scraper.scrape()

	output_base = Path(args.output_base)
	save_as_json(rows, output_base.with_suffix(".json"))
	save_as_csv(rows, output_base.with_suffix(".csv"))


if __name__ == "__main__":
	main()
