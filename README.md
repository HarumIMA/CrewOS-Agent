CrewOS Agent

Planning and Progress Tracker AI — Tugas Agentic AI

Repositori kode: multi-agent-commit-intelligence (nama internal pada kode; nama produk pada laporan dan presentasi adalah CrewOS Agent).

Disusun oleh: ima · AI Engineer — Spesialis Agentic AI

1. Ringkasan

CrewOS Agent adalah asisten multi-agent yang (1) menganalisis aktivitas commit GitHub sebuah tim untuk memetakan profil dan riwayat kontribusi tiap developer, serta (2) membantu menyusun dan menyimpan rencana kerja proyek dari kebutuhan berbahasa bebas — semuanya melalui satu antarmuka chat. Sistem dibangun di atas framework Agno (AgentOS) dengan pola Hub-and-Spoke: satu orkestrator agentic memutuskan agen spesialis mana yang perlu dipanggil untuk setiap permintaan pengguna.

Dokumen ini adalah ringkasan teknis untuk memudahkan peninjauan cepat. Penjelasan lengkap beserta diagram arsitektur, alur kerja, dan pembahasan tiap komponen wajib tugas tersedia pada Laporan Proyek (CrewOS_Agent_Laporan_Proyek.docx) dan materi presentasi yang menyertai pengumpulan ini.

2. Fitur yang Sudah Berjalan (bukan rencana, sudah ada di kode)
Orkestrasi agentic dengan Agno (manager_agent) yang merutekan permintaan pengguna ke agen spesialis yang sesuai.
Penarikan commit sungguhan dari GitHub REST API dan penyimpanannya ke PostgreSQL, per developer.
Kueri profil dan statistik developer melalui percakapan chat (bukan dashboard klik-klik).
Penyusunan draf rencana kerja proyek dari requirement berbahasa bebas oleh Planning Agent.
Mekanisme human-in-the-loop: rencana baru benar-benar tersimpan ke basis data hanya setelah pengguna memberi persetujuan eksplisit.
Guardrail di tingkat kode: sanitasi input, pembersihan teks rencana sebelum disimpan, dan penanganan error yang tidak membocorkan traceback mentah.
3. Arsitektur Singkat
User (Manajer) → Frontend (frontend/index.html)
              → Agentic Orchestrator — main.py (Agno Agent "Company AI Assistant"), port 8000
                    ├── A2A (HTTP) → Data & Analyst Agent — a2a/service.py, port 8001
                    │                 (agent: gemini_specialist, model: Groq Llama-3.3-70B)
                    │                 → GitHub REST API, PostgreSQL (developer_profiles, github_commits)
                    └── A2A (HTTP) → Planning Agent — a2a/service_planning.py, port 8002
                                      (agent: planner_specialist, model: Groq Llama-3.3-70B)
                                      → Human-in-the-Loop (persetujuan Ya/Tidak)
                                      → PostgreSQL (tabel: rencana)

Ketiga proses berjalan independen dan berkoordinasi lewat REST API (A2A), bukan berbagi memori dalam satu proses. Diagram lengkap tersedia pada file arsitektur_tersemat.png dan pada Laporan Proyek bagian 5.

4. Tumpukan Teknologi
Lapisan	Teknologi
Framework agen	Agno 2.8.7 (AgentOS)
Model bahasa	Groq — qwen/qwen3.6-27b (orchestrator), llama-3.3-70b-versatile (kedua agen spesialis)
Backend API	FastAPI + Uvicorn
Basis data	PostgreSQL (via connection pooler Supabase, psycopg2)
Sumber data eksternal	GitHub REST API
Frontend	HTML + Tailwind CSS (antarmuka chat)
5. Cara Menjalankan

Prasyarat: Python 3.10+, akses ke basis data PostgreSQL, token GitHub, dan API key Groq.

Clone/pull repositori, lalu install dependensi:
   pip install -r requirements.txt
Salin envexample.md menjadi .env dan isi tiga variabel berikut:
   GROK_API_KEY=   # API key Groq — dipakai oleh seluruh agen
   DB_URL=         # connection string PostgreSQL
   GITHUB_TOKEN=   # personal access token GitHub
Jalankan tiga proses pada terminal terpisah (urutan tidak wajib, tapi Orchestrator butuh dua service lain untuk fitur penuh):
   python a2a/service.py            # Data & Analyst Agent  → port 8001
   python a2a/service_planning.py   # Planning Agent         → port 8002
   python main.py                   # Agentic Orchestrator   → port 8000
Buka http://localhost:8000/app — antarmuka chat yang sudah terhubung ke kedua agen spesialis.
6. Struktur Folder
main.py                    Agentic Orchestrator (Agno Agent + AgentOS), frontend server
a2a/service.py              Microservice Data & Analyst Agent (port 8001)
a2a/specialist.py           Definisi agent gemini_specialist
a2a/service_planning.py     Microservice Planning Agent (port 8002)
a2a/planner.py               Definisi agent planner_specialist
guardrails/guardrails.py    sanitize_input, clean_plan_text, validate_github_repo, handle_service_error
mcp/github_fetcher.py       Pengambilan commit dari GitHub REST API
mcp/dev_tool.py             Penyimpanan profil developer & commit ke PostgreSQL
mcp/query_tool.py           Kueri statistik developer dari PostgreSQL
planning/planning.py        insert_rencana, query_rencana (CRUD tabel rencana)
frontend/index.html         Antarmuka chat
7. Pemenuhan Komponen Wajib Tugas
Komponen	Status pada kode	Catatan
Agno	Terimplementasi	manager_agent, gemini_specialist, planner_specialist — tiga Agent Agno dengan tools masing-masing
A2A	Terimplementasi (gaya A2A)	Koordinasi antar tiga microservice FastAPI independen via REST API/HTTP, bukan implementasi protokol A2A formal Google
MCP	Sebagian	Folder mcp/ berisi tools function-calling native Agno, bukan protokol client–server MCP formal — paket mcp tidak ada di requirements.txt
Guardrails	Terimplementasi, satu fungsi dorman	sanitize_input, clean_plan_text, handle_service_error aktif dipakai; validate_github_repo sudah ditulis tapi belum pernah dipanggil di alur manapun
Human-in-the-Loop	Terimplementasi	Penyimpanan rencana ke database ditahan sampai pengguna membalas persetujuan eksplisit (cache sesi LAST_DRAFT_CACHE)

Tabel ini disusun agar dapat langsung dicocokkan dengan rubrik penilaian. Detail dan bukti (cuplikan kode, tangkapan layar sistem berjalan) ada pada Laporan Proyek.

8. Keterbatasan yang Diketahui & Peta Jalan
Kolom detected_skills dan estimated_role pada data developer saat ini masih nilai tetap ("General Dev" / "Software Engineer"), belum hasil analisis AI terhadap isi commit.
Ringkasan commit (summary_ai) saat ini adalah penggabungan string sederhana, bukan hasil peringkasan oleh model bahasa pada tahap penyimpanan data.
Belum ada deteksi risiko keterlambatan proyek maupun integrasi data HR perusahaan.
Branding pada antarmuka frontend (frontend/index.html) masih menampilkan nama lama ("DevTeam Activity Monitor", "Gemini Orchestrator · NVIDIA Specialist") yang belum disesuaikan dengan nama produk CrewOS Agent maupun penyedia model yang sebenarnya dipakai (Groq).

Bagian-bagian di atas dicantumkan secara terbuka agar batas antara kemampuan yang sudah berjalan dan yang masih menjadi rencana pengembangan tetap jelas bagi penilai.

9. Berkas Pendukung untuk Penilaian
CrewOS_Agent_Laporan_Proyek.docx — laporan proyek lengkap (5–8 halaman A4)
Materi presentasi (.pptx)
arsitektur_tersemat.png — diagram arsitektur sistem
hitl_nyata.png — diagram alur human-in-the-loop
