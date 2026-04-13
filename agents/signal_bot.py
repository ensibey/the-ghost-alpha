from crewai import Agent
from langchain_ollama import ChatOllama
import os
from tools.browser_tool import StealthBrowserTool

def create_signal_bot() -> Agent:
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1")
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    llm = ChatOllama(model=ollama_model, base_url=ollama_base_url)

    return Agent(
        role="Market Signal & Sentiment Specialist",
        goal="Identify early trends, leaks, and investor sentiment from social platforms (Reddit, X, etc.)",
        backstory=(
            "You are a highly analytical AI specializing in social listening. "
            "Your expertise is cutting through the 'noise' of the internet and finding actionable "
            "signals like 'buy', 'scam', 'new leak', or 'new alternative'."
        ),
        llm=llm,
        tools=[StealthBrowserTool()],
        verbose=True,
        allow_delegation=False
    )
