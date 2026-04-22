from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
import time
import re


class WebScraper:
    def __init__(self):
        self.setup_logging()
        self.setup_driver()

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def _get_meta(self, soup, name=None, property=None):
        """Helper to safely extract a meta tag's content."""
        if name:
            tag = soup.find("meta", {"name": name})
        elif property:
            tag = soup.find("meta", {"property": property})
        else:
            return ""
        return tag.get("content", "").strip() if tag else ""

    def scrape_website(self, url: str, wait_time: int = 5) -> dict:
        try:
            self.logger.info(f"Scraping URL: {url}")
            self.driver.get(url)
            time.sleep(wait_time)

            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            # ── Metadata ──────────────────────────────────────────────────────
            metadata = {
                "description": (
                    self._get_meta(soup, name="description")
                    or self._get_meta(soup, property="og:description")
                ),
                "keywords": self._get_meta(soup, name="keywords"),
                "author": self._get_meta(soup, name="author"),
                "canonical": (
                    soup.find("link", {"rel": "canonical"}).get("href", "")
                    if soup.find("link", {"rel": "canonical"})
                    else ""
                ),
                "og_title": self._get_meta(soup, property="og:title"),
                "og_image": self._get_meta(soup, property="og:image"),
                "robots": self._get_meta(soup, name="robots"),
            }

            # ── Links ─────────────────────────────────────────────────────────
            links = []
            seen_hrefs = set()
            for a in soup.find_all("a", href=True):
                href = a.get("href", "").strip()
                if not href or href.startswith("#") or href.startswith("javascript"):
                    continue
                href = urljoin(url, href)  # handles /, relative, and absolute correctly
                if href not in seen_hrefs:
                    seen_hrefs.add(href)
                    links.append({
                        "text": a.get_text(strip=True)[:120] or "(no text)",
                        "url": href,
                    })

            # ── Images ────────────────────────────────────────────────────────
            images = []
            seen_srcs = set()
            for img in soup.find_all("img"):
                src = img.get("src", "").strip()
                if not src:
                    continue
                src = urljoin(url, src)  # handles /, relative, and absolute correctly
                if src not in seen_srcs:
                    seen_srcs.add(src)
                    images.append({
                        "src": src,
                        "alt": img.get("alt", "").strip(),
                    })

            # ── Headers ───────────────────────────────────────────────────────
            headers = []
            for h in soup.find_all(["h1", "h2", "h3", "h4"]):
                text = h.get_text(strip=True)
                if text:
                    headers.append({"level": h.name.upper(), "text": text[:200]})

            # ── Clean text content ────────────────────────────────────────────
            for tag in soup(["script", "style", "noscript", "iframe"]):
                tag.decompose()
            raw_text = soup.get_text(separator=" ", strip=True)
            clean_text = re.sub(r"\s{2,}", " ", raw_text).strip()

            return {
                "url": url,
                "title": soup.title.string.strip() if soup.title else "",
                "metadata": metadata,
                "text_content": clean_text,
                "links": links,
                "images": images,
                "headers": headers,
            }

        except Exception as e:
            self.logger.error(f"Error scraping {url}: {str(e)}")
            return None

    def __del__(self):
        try:
            self.driver.quit()
        except Exception:
            pass