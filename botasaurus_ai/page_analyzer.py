"""
Page Analyzer
=============

Analyzes web pages using vision models and HTML parsing.
"""

from typing import Optional, Dict, Any, List
import re
import json


class PageAnalyzer:
    """Analyzes page structure for scraper generation"""

    def __init__(self, llm_client, use_vision: bool = True):
        self.llm_client = llm_client
        self.use_vision = use_vision

    async def analyze(
        self,
        url: Optional[str] = None,
        screenshot: Optional[bytes] = None,
        html: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a web page to understand its structure.

        Returns analysis with:
        - Main content areas
        - Data patterns
        - Recommended selectors
        - Page type classification
        """
        analysis = {}

        # If URL provided but no HTML/screenshot, fetch them
        if url and not (html or screenshot):
            try:
                screenshot, html = await self._fetch_page(url)
            except:
                pass  # Continue with whatever we have

        # HTML analysis (fast, always do this)
        if html:
            html_analysis = self._analyze_html(html)
            analysis.update(html_analysis)

        # Vision analysis (slower, more accurate)
        if self.use_vision and screenshot:
            try:
                vision_analysis = await self._analyze_with_vision(screenshot, html)
                # Merge vision analysis, giving it priority
                for key, value in vision_analysis.items():
                    if key not in analysis or vision_analysis[key]:
                        analysis[key] = value
            except Exception as e:
                # Vision analysis failed, use HTML analysis only
                pass

        # Ensure all required fields exist
        analysis.setdefault("page_type", "unknown")
        analysis.setdefault("main_content", [])
        analysis.setdefault("data_patterns", [])
        analysis.setdefault("recommended_selectors", [])
        analysis.setdefault("complexity", "medium")

        return analysis

    async def _fetch_page(self, url: str) -> tuple:
        """Fetch page screenshot and HTML using Playwright"""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise ImportError("Playwright not installed. Run: pip install playwright")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until='networkidle')

            # Take screenshot
            screenshot = await page.screenshot(full_page=True)

            # Get HTML
            html = await page.content()

            await browser.close()

            return screenshot, html

    def _analyze_html(self, html: str) -> Dict[str, Any]:
        """Analyze HTML structure without external dependencies"""
        # Simple HTML analysis without BeautifulSoup
        analysis = {}

        # Classify page type
        analysis["page_type"] = self._classify_page_type(html)

        # Find main content areas
        analysis["main_content"] = self._find_main_content(html)

        # Suggest selectors
        analysis["recommended_selectors"] = self._suggest_selectors(html)

        # Assess complexity
        analysis["complexity"] = self._assess_complexity(html)

        return analysis

    async def _analyze_with_vision(
        self,
        screenshot: bytes,
        html: Optional[str]
    ) -> Dict[str, Any]:
        """Analyze page using vision model"""

        prompt = """Analyze this webpage screenshot and provide structured analysis.

Identify:
1. Page type (e-commerce, blog, search-results, profile, listing, form, etc.)
2. Main content areas (header, nav, main, sidebar, footer locations)
3. Data patterns (product cards, list items, tables, forms)
4. Page complexity (low/medium/high based on dynamic elements)
5. Recommended scraping approach (@browser or @request)

Return JSON format:
{
  "page_type": "...",
  "main_content": ["header", "main content", "sidebar"],
  "data_patterns": ["product cards in grid", "price elements"],
  "complexity": "low|medium|high",
  "recommended_approach": "@browser|@request",
  "key_elements": ["element descriptions"]
}"""

        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]

        try:
            response = self.llm_client.complete_with_vision(
                messages=messages,
                images=[screenshot],
                temperature=0.3,
                max_tokens=500
            )

            # Try to parse JSON response
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```"):
                response = re.sub(r'```(?:json)?\n?', '', response)
                response = response.strip('`').strip()

            return json.loads(response)
        except json.JSONDecodeError:
            # If JSON parsing fails, return basic structure
            return {
                "page_type": "unknown",
                "complexity": "medium",
                "vision_analysis_failed": True
            }
        except Exception as e:
            return {}

    def _classify_page_type(self, html: str) -> str:
        """Classify page type from HTML"""
        html_lower = html.lower()

        # E-commerce indicators
        if any(term in html_lower for term in ['product', 'cart', 'price', 'add to cart', 'buy now']):
            return "e-commerce"

        # Search results
        if any(term in html_lower for term in ['search results', 'results for', 'showing', 'found']):
            return "search-results"

        # Article/blog
        if any(term in html_lower for term in ['<article', 'blog', 'post', 'author']):
            return "article"

        # Profile page
        if any(term in html_lower for term in ['profile', 'about', 'bio', 'followers']):
            return "profile"

        # Listing/directory
        if html_lower.count('class="card"') > 5 or html_lower.count('class="item"') > 5:
            return "listing"

        # Form
        if html_lower.count('<form') > 0 and html_lower.count('<input') > 5:
            return "form"

        return "general"

    def _find_main_content(self, html: str) -> List[str]:
        """Find main content areas"""
        areas = []

        # Look for common content containers
        patterns = [
            r'<main[^>]*>',
            r'<article[^>]*>',
            r'id=["\']content["\']',
            r'class=["\'][^"\']*content[^"\']*["\']',
            r'class=["\'][^"\']*main[^"\']*["\']',
        ]

        for pattern in patterns:
            if re.search(pattern, html, re.IGNORECASE):
                # Extract selector from pattern
                if 'id=' in pattern:
                    areas.append('#content')
                elif 'main' in pattern.lower():
                    areas.append('main')
                elif 'article' in pattern.lower():
                    areas.append('article')
                elif 'content' in pattern.lower():
                    areas.append('.content')

        return list(set(areas))[:5]  # Top 5 unique

    def _suggest_selectors(self, html: str) -> List[Dict[str, str]]:
        """Suggest selectors for common data types"""
        selectors = []

        # Titles/headings
        if '<h1' in html:
            selectors.append({"type": "title", "selector": "h1"})

        # Prices
        price_patterns = ['.price', '[class*="price"]', '[data-price]']
        for pattern in price_patterns:
            if pattern.replace('[', '').replace(']', '').replace('*=', '') in html.lower():
                selectors.append({"type": "price", "selector": pattern})
                break

        # Images
        if '<img' in html:
            selectors.append({"type": "image", "selector": "img[src]"})

        # Links
        if '<a href' in html:
            selectors.append({"type": "link", "selector": "a[href]"})

        # Descriptions/paragraphs
        if '<p' in html:
            selectors.append({"type": "text", "selector": "p"})

        return selectors[:10]

    def _assess_complexity(self, html: str) -> str:
        """Assess page complexity"""
        # Count interactive elements
        interactive_count = (
            html.lower().count('<button') +
            html.lower().count('<input') +
            html.lower().count('<select')
        )

        # Count scripts
        script_count = html.lower().count('<script')

        # Check for common JS frameworks
        has_react = 'react' in html.lower()
        has_vue = 'vue' in html.lower()
        has_angular = 'angular' in html.lower()

        if script_count > 20 or has_react or has_vue or has_angular:
            return "high"
        elif script_count > 5 or interactive_count > 10:
            return "medium"
        return "low"
