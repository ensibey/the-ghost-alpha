import time
import random
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from bs4 import BeautifulSoup

class StealthBrowserToolInput(BaseModel):
    """Input parameters for the StealthBrowserTool."""
    url: str = Field(..., description="The exact URL of the website to scrape and analyze.")

class StealthBrowserTool(BaseTool):
    name: str = "Stealth Browser Scraper"
    description: str = "A tool to navigate to a URL using a stealth browser, scroll like a human, and extract the page text content, bypassing basic bot protections."
    args_schema: Type[BaseModel] = StealthBrowserToolInput

    def _run(self, url: str) -> str:
        """Executes the stealth scraping logic."""
        text_content = ""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                # Create context with common realistic user agent to mimic a real device
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={"width": 1920, "height": 1080},
                )
                page = context.new_page()
                
                # Apply stealth
                Stealth().apply_stealth_sync(page)
                
                print(f"[*] Browsing to {url} ...")
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                # Mimic human scrolling
                for _ in range(3):
                    time.sleep(random.uniform(1.0, 2.5))
                    page.mouse.wheel(0, random.randint(300, 800))
                
                # Final wait for dynamic content to load
                time.sleep(random.uniform(2.0, 4.0))
                
                html_content = page.content()
                browser.close()
                
                # Parse with BeautifulSoup for clean text
                soup = BeautifulSoup(html_content, "html.parser")
                
                # Remove script, style, header, footer, etc to reduce noise
                for element in soup(["script", "style", "noscript", "header", "footer", "nav"]):
                    element.decompose()
                
                text_content = soup.get_text(separator='\n', strip=True)
                
                # Limit length to avoid blowing up LLM context (approx 4000 words max)
                text_content = text_content[:10000]
                
        except Exception as e:
            return f"Error scraping {url}: {str(e)}"
            
        return text_content
