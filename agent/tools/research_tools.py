"""Web Research & News Information Tools."""

import logging
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Optional

import httpx

logger = logging.getLogger("research_tools")


def web_search(query: str, max_results: int = 4) -> str:
    """Search the web for up-to-date information, facts, documentation, or links.
    
    Parameters:
    - query: The search term or question to search the web for.
    - max_results: Number of search results to return (default: 4).
    """
    clean_q = query.strip()
    if not clean_q:
        return "Please provide a valid query to search."

    try:
        # First attempt: DuckDuckGo instant answer JSON API
        encoded_q = urllib.parse.quote_plus(clean_q)
        api_url = f"https://api.duckduckgo.com/?q={encoded_q}&format=json&no_html=1&skip_disambig=1"

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

        with httpx.Client(verify=False, timeout=8.0, headers=headers) as client:
            resp = client.get(api_url)
            if resp.status_code == 200:
                data = resp.json()
                abstract = data.get("AbstractText", "")
                heading = data.get("Heading", "")
                related = data.get("RelatedTopics", [])

                results = []
                if abstract:
                    results.append(f"• Summary ({heading}): {abstract}")

                for item in related:
                    if len(results) >= max_results:
                        break
                    if isinstance(item, dict) and "Text" in item and item.get("Text"):
                        text = item["Text"]
                        first_url = item.get("FirstURL", "")
                        url_str = f" ({first_url})" if first_url else ""
                        results.append(f"• {text}{url_str}")

                if results:
                    return f"Web search results for '{clean_q}':\n" + "\n".join(results)

        # Fallback: DuckDuckGo HTML scraping
        html_url = f"https://html.duckduckgo.com/html/?q={encoded_q}"
        with httpx.Client(verify=False, timeout=8.0, headers=headers) as client:
            resp = client.get(html_url)
            if resp.status_code == 200:
                html = resp.text
                snippets = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', html, flags=re.DOTALL)
                titles = re.findall(r'<a class="result__url[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, flags=re.DOTALL)

                results = []
                for i in range(min(len(snippets), max_results)):
                    clean_snip = re.sub(r'<[^>]+>', '', snippets[i]).strip()
                    if clean_snip:
                        results.append(f"• Result {i+1}: {clean_snip}")

                if results:
                    return f"Web search results for '{clean_q}':\n" + "\n".join(results)

        return f"No direct search results found for '{clean_q}'."
    except Exception as e:
        logger.warning(f"Web search error for '{clean_q}': {e}")
        return f"Unable to complete web search for '{clean_q}' due to network/connectivity: {e}"


def fetch_news(topic: str = "general") -> str:
    """Fetch recent news headlines on a topic (e.g. 'technology', 'world', 'business', 'sports', 'India')."""
    clean_topic = topic.strip().lower()
    topic_map = {
        "technology": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-IN&gl=IN&ceid=IN:en",
        "business": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-IN&gl=IN&ceid=IN:en",
        "science": "https://news.google.com/rss/headlines/section/topic/SCIENCE?hl=en-IN&gl=IN&ceid=IN:en",
        "sports": "https://news.google.com/rss/headlines/section/topic/SPORTS?hl=en-IN&gl=IN&ceid=IN:en",
        "general": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    }

    url = topic_map.get(clean_topic)
    if not url:
        encoded = urllib.parse.quote_plus(clean_topic)
        url = f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            root = ET.fromstring(r.read())
            items = root.findall('.//item')[:5]

            if not items:
                return f"No news headlines found for topic '{topic}'."

            lines = [f"Latest news headlines ({topic}):"]
            for i, it in enumerate(items, 1):
                title = it.find('title')
                title_text = title.text if title is not None and title.text else "Headline"
                pub = it.find('pubDate')
                pub_text = f" ({pub.text[:16]})" if pub is not None and pub.text else ""
                lines.append(f"{i}. {title_text}{pub_text}")

            return "\n".join(lines)
    except Exception as e:
        return f"Unable to fetch news for '{topic}': {e}"


def summarize_url(url: str) -> str:
    """Read and extract text from a webpage URL to prepare for summarization."""
    try:
        clean_url = url.strip()
        req = urllib.request.Request(
            clean_url,
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read(150000).decode("utf-8", errors="replace")

        text = re.sub(r"<script.*?</script>", "", raw, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        if len(text) > 3000:
            text = text[:3000] + "... [truncated]"

        return f"Content extracted from {clean_url}:\n\n{text}"
    except Exception as e:
        return f"Error extracting content from URL '{url}': {e}"
