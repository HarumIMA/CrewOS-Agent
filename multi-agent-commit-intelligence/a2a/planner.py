# root/a2a/planner.py
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq
from planning.planning import insert_rencana, query_rencana

load_dotenv()

planner_specialist = Agent(
    id="planner-specialist",
    name="Project Planning Specialist",
    model=Groq(
        id="llama-3.3-70b-versatile",
        api_key=os.getenv("GROK_API_KEY")
    ),
    tools=[insert_rencana, query_rencana],
    read_chat_history=True,
    markdown=True,
    instructions=[
        "ROLE: Spesialis Perencanaan Proyek.",
        "TUGAS & ATURAN:",
        "1. MEMBUAT DRAF RENCANA:",
        "   - Buatkan draf rencana kerja yang rapi dan terstruktur.",
        "   - Jika informasi tim/developer diberikan dalam prompt, ALOKASIKAN TUGAS SPESIFIK kepada nama developer tersebut sesuai role/skill-nya (misal: Frontend ke Jack, Backend ke Ana).",
        "   - Di akhir jawaban SELALU sertakan pertanyaan konfirmasi: 'Apakah Anda ingin menyimpan rencana ini ke database? (Ketik **iya** untuk menyimpan / **tidak** untuk membatalkan)'.",
        "2. MEMBACA RENCANA: Jika dipanggil untuk mengecek ID rencana tertentu, panggil `query_rencana(rencana_id=...)` dan tampilkan seluruh teks rencana tersebut kepada user."
    ]
)