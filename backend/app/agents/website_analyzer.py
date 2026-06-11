import asyncio
import json
from datetime import datetime, timezone
from typing import Optional
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.schemas import CompanyProfile

logger = get_logger(__name__)


async def fetch_website_content(url: str) -> str:
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=settings.PLAYWRIGHT_HEADLESS)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            content = await page.evaluate("() => document.body.innerText")
            await browser.close()
            return content[:8000]
    except Exception as e:
        logger.warning(f"Playwright failed for {url}: {e}, falling back to httpx")
        import httpx
        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer"]):
                tag.decompose()
            return soup.get_text(separator=" ", strip=True)[:8000]


ANALYZE_SYSTEM_PROMPT = """You are a B2B sales intelligence expert. Analyze website content and extract structured business information.

Respond ONLY with a valid JSON object matching this schema:
{
  "company_name": "string",
  "industry": "string",
  "services": ["list of services"],
  "products": ["list of products"],
  "target_customers": ["list of target customer segments"],
  "pain_points": ["list of pain points this company solves"]
}

Be specific, concise, and accurate. If a field cannot be determined, use an empty list or "Unknown"."""


class WebsiteAnalyzerAgent:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def analyze(self, url: str) -> CompanyProfile:
        logger.info(f"Analyzing website: {url}")

        content = await fetch_website_content(url)

        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": ANALYZE_SYSTEM_PROMPT},
                {"role": "user", "content": f"Website URL: {url}\n\nContent:\n{content}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=1500,
        )

        raw = response.choices[0].message.content
        data = json.loads(raw)

        return CompanyProfile(
            company_name=data.get("company_name", "Unknown"),
            industry=data.get("industry", "Unknown"),
            services=data.get("services", []),
            products=data.get("products", []),
            target_customers=data.get("target_customers", []),
            pain_points=data.get("pain_points", []),
        )
