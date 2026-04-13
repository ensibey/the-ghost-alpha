from crewai import LLM
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_local_llm():
    """
    Returns an LLM instance configured for the environment (Ollama locally, Groq in cloud).
    """
    # If a Groq API Key is provided, use Groq (Perfect for cloud/GitHub Actions)
    if GROQ_API_KEY:
        print("[LLM] Using Groq (Cloud Mode)")
        return ChatGroq(
            api_key=GROQ_API_KEY,
            model_name="llama-3.3-70b-versatile"
        )
        
    # Default to Local Ollama
    print(f"[LLM] Using Local Ollama: {OLLAMA_MODEL}")
    return LLM(
        model=f"ollama/{OLLAMA_MODEL}",
        base_url=OLLAMA_BASE_URL
    )
