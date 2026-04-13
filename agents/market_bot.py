from crewai import Agent
from core.llm import get_local_llm
from tools.browser_tool import StealthBrowserTool

def create_market_bot() -> Agent:
    return Agent(
        role="E-commerce Arbitrage & Price Tracker",
        goal="Monitor physical and digital products across Amazon and eBay for sudden price drops or 'Out of Stock' statuses",
        backstory=(
            "You are a ruthless e-commerce tracker. You observe product availabilities. "
            "An item suddenly going out of stock everywhere indicates high demand or a supply chain interruption. "
            "You highlight these as market opportunities."
        ),
        llm=get_local_llm(),
        tools=[StealthBrowserTool()],
        verbose=True,
        allow_delegation=False
    )
