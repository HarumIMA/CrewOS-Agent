# root/main.py
import os
import httpx
from dotenv import load_dotenv
from agno.agent import Agent
from agno.os import AgentOS
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import FileResponse, RedirectResponse
from agno.models.groq import Groq
# IMPOR GUARDRAILS
from guardrails.guardrails import sanitize_input, validate_github_repo
load_dotenv()

os.makedirs("tmp", exist_ok=True)
SPECIALIST_BASE_URL = os.getenv("SPECIALIST_URL", "http://localhost:8001")
PLANNING_BASE_URL = os.getenv("PLANNING_URL", "http://localhost:8002")

async def tarik_data_github(repo_owner: str, repo_name: str, limit: int = 3) -> str:
    """Gunakan fungsi ini jika user ingin mengambil atau memperbarui data commit GitHub."""
    try:
        url = f"{SPECIALIST_BASE_URL}/api/v1/github/sync"
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {"repo_owner": repo_owner, "repo_name": repo_name, "limit": limit}
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                return data.get("result", "") if data.get("status") == "success" else f"Error: {data.get('message')}"
            return f"Error HTTP: {response.status_code}"
    except Exception as e:
        return f"Gagal terhubung ke GitHub backend: {str(e)}"

async def cek_database_perusahaan(days: int = 365, author_query: str = None) -> str:
    """Gunakan fungsi ini untuk melihat daftar developer/pegawai, posisi (Frontend/Backend/DLL), skill, atau statistik commit dari database perusahaan."""
    try:
        # GUARDRAIL 1: Clean input string
        clean_author = sanitize_input(author_query) if author_query else None
        url = f"{SPECIALIST_BASE_URL}/api/v1/database/query"
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {"days": days, "author_query": clean_author}
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                return data.get("result", "") if data.get("status") == "success" else f"Error: {data.get('message')}"
            return f"Error HTTP: {response.status_code}"
    except Exception as e:
        return f"Gagal terhubung ke Database backend: {str(e)}"

async def kelola_perencanaan_proyek(topik_atau_aksi: str) -> str:
    """Gunakan fungsi ini untuk memproses perencanaan proyek (membuat draf, merevisi, atau menyimpan ke DB). 
    Pastikan memasukkan konteks developer/tim jika ada."""
    try:
        # GUARDRAIL 1: Clean Input Text dari prompt injection/karakter aneh
        clean_input = sanitize_input(topik_atau_aksi)
        url = f"{PLANNING_BASE_URL}/api/v1/planning/process"
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "prompt_rencana": clean_input,
                "session_id": "active_user_session" 
            }
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                return data.get("result", "") if data.get("status") == "success" else f"Error: {data.get('message')}"
            return f"Error HTTP: {response.status_code}"
    except Exception as e:
        return f"Gagal terhubung ke Planning backend: {str(e)}"

async def baca_rencana_proyek(rencana_id: int = None) -> str:
    """Gunakan fungsi ini untuk melihat/membaca rencana yang sudah tersimpan berdasarkan ID atau melihat semua rencana."""
    try:
        url = f"{PLANNING_BASE_URL}/api/v1/planning/query"
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {"rencana_id": rencana_id}
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    d = data.get("data")
                    if not d:
                        return "Data rencana tidak ditemukan."
                    if isinstance(d, dict):
                        return f"📋 **Detail Rencana ID {d.get('id')}**:\n- **Urutan:** {d.get('urutan')}\n- **Dibuat:** {d.get('created_at')}\n\n**Isi Rencana:**\n{d.get('teks_tujuan')}"
                    return str(d)
                return f"Informasi: {data.get('message')}"
            return f"Error HTTP: {response.status_code}"
    except Exception as e:
        return f"Gagal mengambil rencana: {str(e)}"

manager_agent = Agent(
    id="company-orchestrator-manager",
    name="Company AI Assistant",
    model=Groq(
        id="qwen/qwen3.6-27b",  
        api_key=os.getenv("GROK_API_KEY")
    ),
    description="Asisten eksekutif pusat pengelola perusahaan.",
    tools=[tarik_data_github, cek_database_perusahaan, kelola_perencanaan_proyek,baca_rencana_proyek],
    read_chat_history=True,
    markdown=True,
    instructions=[
        "ROLE: Orchestrator Utama Perusahaan.",
        "ATURAN ROUTING TOOL:",
        "1. Jika user ingin MEMBACA / MENGAMBIL rencana yang tersimpan (misal: 'lihat rencana id 10', 'cek rencana 1'), PANGGIL `baca_rencana_proyek(rencana_id=...)`.",
        "2. Jika user ingin MEMBUAT, MEREVISI, atau MENYIMPAN draf rencana baru ('iya', 'simpan', 'tidak'), PANGGIL `kelola_perencanaan_proyek`.",
        "3. Untuk topik GitHub panggil `tarik_data_github`.",
        "4. Untuk statistik/database perusahaan panggil `cek_database_perusahaan`."
        "5.Jika user bertanya tentang PEGAWAI, DEVELOPER, TIM, SKILL, POSISI/ROLE (misal: frontend, backend, devops), ATAU STATISTIK COMMIT, WAJIB PANGGIL `cek_database_perusahaan`"
        "6. Jika user meminta untuk MEMBUAT RENCANA PROYEK BARU (misal: 'buatkan rencana pengembangan web sekolah'):",
        "   a. PERTAMA: Panggil `cek_database_perusahaan()` untuk mengambil daftar developer, role (Frontend, Backend, dll), dan skill mereka saat ini.",
        "   b. KEDUA: Setelah mendapatkan data tim developer, panggil `kelola_perencanaan_proyek(topik_atau_aksi=...)` dengan prompt yang menggabungkan permintaan user DAN data developer yang didapatkan. Contoh isi prompt: 'Buatkan rencana proyek [Topik User]. Tim yang tersedia: [Data Developer dari DB]. Alokasikan tugas spesifik ke nama developer yang sesuai rolenya.'"
    ]
)

app = AgentOS(agents=[manager_agent]).get_app()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/app")

@app.get("/app", include_in_schema=False)
async def serve_frontend():
    return FileResponse("frontend/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
