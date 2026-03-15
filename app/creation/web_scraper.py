"""
Web scraper for collecting website content.
Uses crawl4ai for JavaScript-rendered pages.
"""

import logging
import asyncio
import re
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


@dataclass
class ScrapingResult:
    url: str
    pages_scraped: int = 0
    consolidated_text: str = ""
    warnings: list = field(default_factory=list)


def _should_exclude(url: str) -> bool:
    """Check if URL should be excluded from scraping."""
    excludes = ['login', 'admin', 'cart', 'checkout', 'wp-admin', 'feed', 'sitemap',
                '.pdf', '.jpg', '.png', '.gif', '.mp4', '.zip', '.exe']
    url_lower = url.lower()
    return any(ex in url_lower for ex in excludes)


async def scrape_website(url: str, max_pages: int = 15) -> ScrapingResult:
    """Scrape website content using crawl4ai."""
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

        browser_config = BrowserConfig(headless=True)
        run_config = CrawlerRunConfig(
            word_count_threshold=50,
            exclude_external_links=True,
        )

        pages_text = []
        visited = set()
        to_visit = [url]

        async with AsyncWebCrawler(config=browser_config) as crawler:
            while to_visit and len(visited) < max_pages:
                current_url = to_visit.pop(0)
                if current_url in visited or _should_exclude(current_url):
                    continue

                visited.add(current_url)
                try:
                    result = await crawler.arun(url=current_url, config=run_config)
                    if result.success and result.markdown:
                        text = result.markdown[:5000]  # Limit per page
                        pages_text.append(f"## Pagina: {current_url}\n\n{text}")

                        # Extract internal links
                        if result.links:
                            base_domain = urlparse(url).netloc
                            for link in result.links.get("internal", []):
                                href = link.get("href", "")
                                if href and urlparse(href).netloc == base_domain:
                                    if href not in visited:
                                        to_visit.append(href)
                except Exception as e:
                    logger.warning(f"Failed to scrape {current_url}: {e}")

        consolidated = "\n\n---\n\n".join(pages_text)
        return ScrapingResult(
            url=url, pages_scraped=len(pages_text),
            consolidated_text=consolidated
        )

    except ImportError:
        logger.warning("crawl4ai not installed, using simple HTTP scraping")
        return await _simple_scrape(url)
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        return ScrapingResult(url=url, warnings=[f"Erro no scraping: {str(e)}"])


async def _simple_scrape(url: str) -> ScrapingResult:
    """Simple HTTP-based scraping fallback."""
    try:
        import httpx
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            resp = await client.get(url)
            text = resp.text
            # Strip HTML tags (simple)
            clean = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
            clean = re.sub(r'<style[^>]*>.*?</style>', '', clean, flags=re.DOTALL)
            clean = re.sub(r'<[^>]+>', ' ', clean)
            clean = re.sub(r'\s+', ' ', clean).strip()
            return ScrapingResult(url=url, pages_scraped=1, consolidated_text=clean[:10000])
    except Exception as e:
        return ScrapingResult(url=url, warnings=[f"Erro no scraping simples: {str(e)}"])
