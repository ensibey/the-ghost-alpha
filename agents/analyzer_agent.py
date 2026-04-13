from crewai import Agent
from core.llm import get_local_llm

def create_analyzer_agent() -> Agent:
    return Agent(
        role="Intelligence Filter Agent",
        goal="Bypass noise and identify true market opportunities, trends, or arbitrage situations.",
        backstory=(
            "You are a highly analytical filter intelligence. Other bots bring you raw, noisy data. "
            "Your only job is to analyze this data and extract actionable opportunities. "
            "If the data is noise or useless, you reject it."
        ),
        llm=get_local_llm(),
        verbose=True,
        allow_delegation=False
    )
