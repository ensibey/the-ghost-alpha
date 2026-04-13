from crewai import Agent
from core.llm import get_local_llm
from tools.browser_tool import StealthBrowserTool

def create_dev_bot() -> Agent:
    return Agent(
        role="Open Source Technology Tracker",
        goal="Discover suddenly trending GitHub repositories or HuggingFace models before they become mainstream",
        backstory=(
            "You are an AI embedded in the developer ecosystem. You know that whatever developers "
            "are starring, forking, or experimenting with today will become the market standard 3 months later. "
            "You look for rapid growth indicators on tech platforms."
        ),
        llm=get_local_llm(),
        tools=[StealthBrowserTool()],
        verbose=True,
        allow_delegation=False
    )
