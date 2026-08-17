# root/ a2a/specialist.py
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agno.models.groq import Groq
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
from mcp.github_fetcher import fetch_repo_commits_raw
from mcp.dev_tool import save_analyzed_developer_data
from mcp.query_tool import query_developer_stats

load_dotenv()

# Agent Specialist di backend untuk mengolah data
gemini_specialist = Agent(
    id="gemini-specialist",
    name="Backend Data Processor Specialist",
    model=Groq(
        id="llama-3.3-70b-versatile",
        api_key=os.getenv("GROK_API_KEY")
    ),
    tools=[fetch_repo_commits_raw, save_analyzed_developer_data, query_developer_stats],
    read_chat_history=True,
    instructions=[
        "ROLE: Analis Data Backend & Developer.",
        "ATURAN RESPON:",
        "1. Jawab pertanyaan user berdasarkan data statistik / list developer yang diberikan dalam prompt.",
        "2. Jika user menanyakan tentang role tertentu (misal: 'Frontend Developer'), filter dan sebutkan nama developer yang memiliki role/skill tersebut dari data.",
        "3. Jawab dalam bahasa Indonesia yang singkat, padat, dan jelas.",
        "4. Jika data benar-benar kosong, sampaikan bahwa belum ada data developer yang terdaftar di database."
    ]
)
