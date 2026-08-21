# CrewOS

> **AI-Powered Planning & Programmer Progress Tracker**
> Sistem Agentic AI untuk membantu manajer memantau aktivitas developer dan menyusun rencana kerja proyek melalui satu antarmuka percakapan.

**CrewOS Agent** adalah sistem **multi-agent berbasis AI** yang dirancang untuk membantu perusahaan pengembang web, aplikasi, dan produk digital dalam:

* Menganalisis aktivitas dan riwayat kontribusi programmer melalui GitHub.
* Menyimpan dan mengelola profil kontribusi developer.
* Menampilkan statistik developer melalui percakapan dengan AI.
* Membantu menyusun rencana kerja proyek dari kebutuhan berbahasa bebas.
* Menerapkan **Human-in-the-Loop (HITL)** sebelum rencana kerja disimpan ke database.

> **Repository internal:** `multi-agent-commit-intelligence`
> **Nama produk:** **CrewOS Agent**

---

## ✨ Fitur Utama

### 🤖 1. Agentic Orchestration

CrewOS Agent menggunakan satu **Agentic Orchestrator** sebagai pusat koordinasi.

Orchestrator menerima permintaan pengguna, memahami kebutuhan, kemudian menentukan agen spesialis yang sesuai.

```text
User
  │
  ▼
Agentic Orchestrator
  │
  ├──► Data & Analyst Agent
  │       ├── GitHub REST API
  │       └── PostgreSQL
  │
  └──► Planning Agent
          ├── Membuat Draft Rencana
          ├── Human-in-the-Loop
          └── PostgreSQL
```

---

### 👨‍💻 2. Analisis Aktivitas Developer

Sistem dapat mengambil data commit nyata dari GitHub REST API dan menyimpannya ke PostgreSQL.

Kemampuan yang tersedia:

* Mengambil riwayat commit developer.
* Menyimpan commit per developer.
* Menyimpan profil developer.
* Menampilkan statistik kontribusi melalui chat.
* Melakukan kueri informasi developer tanpa dashboard manual.

Contoh pertanyaan:

```text
Tampilkan statistik kontribusi developer.
```

```text
Siapa developer yang memiliki aktivitas commit paling banyak?
```

---

### 📋 3. AI Project Planning

Pengguna dapat memberikan kebutuhan proyek menggunakan bahasa bebas.

Contoh:

```text
Saya ingin membuat aplikasi manajemen proyek
dengan fitur login, manajemen tugas, dashboard,
dan notifikasi.
```

Planning Agent kemudian membantu membuat draft rencana kerja.

Alur:

```text
Project Requirement
        │
        ▼
Planning Agent
        │
        ▼
Generate Work Plan Draft
        │
        ▼
Human Approval
    ┌───┴───┐
   Tidak    Ya
    │       │
    ▼       ▼
 Perbaiki  Simpan ke
  Draft    PostgreSQL
```

---

### 🧑‍💼 4. Human-in-the-Loop

CrewOS Agent tidak langsung menyimpan rencana yang dihasilkan AI.

Sistem menggunakan mekanisme **Human-in-the-Loop (HITL)**:

1. User memberikan kebutuhan proyek.
2. Planning Agent membuat draft rencana.
3. Draft ditampilkan kepada user.
4. User memberikan persetujuan eksplisit.
5. Hanya setelah persetujuan, rencana disimpan ke database.

Hal ini memastikan keputusan akhir tetap berada pada manusia.

---

### 🛡️ 5. Guardrails

Sistem memiliki beberapa mekanisme perlindungan di tingkat kode:

* Sanitasi input pengguna.
* Pembersihan teks rencana sebelum disimpan.
* Validasi repository GitHub.
* Penanganan error tanpa menampilkan traceback mentah kepada pengguna.

---

# 🏗️ Arsitektur Sistem

CrewOS Agent menggunakan pola **Hub-and-Spoke Architecture**.

```text
                         ┌─────────────────────┐
                         │        USER         │
                         │      (Manager)      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                      ┌──────────────────────────┐
                      │   FRONTEND CHAT UI       │
                      │ frontend/index.html      │
                      └────────────┬─────────────┘
                                   │
                                   ▼
              ┌─────────────────────────────────────┐
              │       AGENTIC ORCHESTRATOR          │
              │                                     │
              │ main.py                             │
              │ Agno Agent / AgentOS                │
              │ Port: 8000                          │
              └───────────────┬─────────────────────┘
                              │
                 ┌────────────┴─────────────┐
                 │                          │
                 ▼                          ▼
     ┌──────────────────────┐    ┌──────────────────────┐
     │ DATA & ANALYST AGENT │    │    PLANNING AGENT    │
     │                      │    │                      │
     │ a2a/service.py       │    │ a2a/service_         │
     │ Port: 8001           │    │ planning.py          │
     │                      │    │ Port: 8002           │
     └──────────┬───────────┘    └──────────┬───────────┘
                │                           │
                ▼                           ▼
        ┌───────────────┐          ┌─────────────────┐
        │ GitHub API    │          │ Human-in-the-   │
        └───────┬───────┘          │ Loop Approval   │
                │                  └────────┬────────┘
                ▼                           │
        ┌───────────────┐                  ▼
        │ PostgreSQL    │          ┌─────────────────┐
        │               │          │ PostgreSQL      │
        │ Developer     │          │ Project Plans   │
        │ Commits       │          └─────────────────┘
        └───────────────┘
```

Ketiga komponen backend berjalan sebagai proses independen dan berkomunikasi melalui REST API menggunakan pendekatan A2A.

---

# 🧠 Multi-Agent Architecture

## 1. Agentic Orchestrator

**File:**

```text
main.py
```

Tanggung jawab:

* Menerima permintaan pengguna.
* Memahami intent pengguna.
* Menentukan agen spesialis yang relevan.
* Mengirim permintaan ke microservice yang sesuai.
* Mengembalikan respons kepada pengguna.

Model:

```text
qwen/qwen3.6-27b
```

Provider:

```text
Groq
```

---

## 2. Data & Analyst Agent

**File:**

```text
a2a/service.py
a2a/specialist.py
```

Tanggung jawab:

* Mengambil commit dari GitHub.
* Menyimpan data developer.
* Menyimpan riwayat commit.
* Menjawab pertanyaan tentang kontribusi developer.
* Menampilkan statistik berdasarkan data PostgreSQL.

Model:

```text
llama-3.3-70b-versatile
```

---

## 3. Planning Agent

**File:**

```text
a2a/service_planning.py
a2a/planner.py
```

Tanggung jawab:

* Menerima kebutuhan proyek.
* Membuat draft rencana kerja.
* Menunggu persetujuan manusia.
* Menyimpan rencana setelah persetujuan eksplisit.

Model:

```text
llama-3.3-70b-versatile
```

---

# 🔄 Alur Komunikasi A2A

```text
                 User Request
                      │
                      ▼
             Agentic Orchestrator
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
   Data Request?            Planning Request?
          │                       │
          ▼                       ▼
   Data & Analyst Agent       Planning Agent
          │                       │
          ▼                       ▼
   GitHub / PostgreSQL       HITL Approval
          │                       │
          └───────────┬───────────┘
                      │
                      ▼
                   Response
                      │
                      ▼
                     User
```

---

# 🧩 MCP dan Tools

CrewOS Agent memiliki folder `mcp/` yang berisi tool untuk integrasi data.

```text
mcp/
├── github_fetcher.py
├── dev_tool.py
└── query_tool.py
```

### Tools yang tersedia

| Tool                | Fungsi                                              |
| ------------------- | --------------------------------------------------- |
| `github_fetcher.py` | Mengambil commit dari GitHub REST API               |
| `dev_tool.py`       | Menyimpan profil developer dan commit ke PostgreSQL |
| `query_tool.py`     | Mengambil statistik developer dari PostgreSQL       |

> **Catatan:** Implementasi pada proyek ini menggunakan tools berbasis *function-calling* native Agno. Folder `mcp/` belum mengimplementasikan protokol MCP client-server formal.

---

# 🛠️ Tech Stack

| Layer               | Technology                 |
| ------------------- | -------------------------- |
| Agent Framework     | Agno 2.8.7 / AgentOS       |
| Orchestrator Model  | `qwen/qwen3.6-27b`         |
| Specialist Model    | `llama-3.3-70b-versatile`  |
| LLM Provider        | Groq                       |
| Backend             | FastAPI                    |
| ASGI Server         | Uvicorn                    |
| Database            | PostgreSQL                 |
| Database Connection | Supabase Connection Pooler |
| Database Library    | psycopg2                   |
| External Data       | GitHub REST API            |
| Frontend            | HTML + Tailwind CSS        |

---

# 📂 Project Structure

```text
multi-agent-commit-intelligence/
│
├── main.py
│   └── Agentic Orchestrator
│       └── Agno Agent + AgentOS + Frontend Server
│
├── a2a/
│   │
│   ├── service.py
│   │   └── Data & Analyst Agent Microservice
│   │       └── Port 8001
│   │
│   ├── specialist.py
│   │   └── Definition of gemini_specialist
│   │
│   ├── service_planning.py
│   │   └── Planning Agent Microservice
│   │       └── Port 8002
│   │
│   └── planner.py
│       └── Definition of planner_specialist
│
├── mcp/
│   ├── github_fetcher.py
│   ├── dev_tool.py
│   └── query_tool.py
│
├── planning/
│   └── planning.py
│       ├── insert_rencana
│       └── query_rencana
│
├── guardrails/
│   └── guardrails.py
│       ├── sanitize_input
│       ├── clean_plan_text
│       ├── validate_github_repo
│       └── handle_service_error
│
└── frontend/
    └── index.html
        └── Chat User Interface
```

---

# 🚀 Installation

## Prerequisites

Pastikan telah tersedia:

* Python 3.10 atau lebih baru.
* PostgreSQL database.
* GitHub Personal Access Token.
* Groq API Key.

---

## 1. Clone Repository

```bash
git clone <repository-url>
cd multi-agent-commit-intelligence
```

---

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Configure Environment Variables

Salin:

```text
envexample.md
```

Menjadi:

```text
.env
```

Kemudian isi konfigurasi:

```env
GROK_API_KEY=
DB_URL=
GITHUB_TOKEN=
```

Keterangan:

| Variable       | Description                                                   |
| -------------- | ------------------------------------------------------------- |
| `GROK_API_KEY` | API key untuk layanan model Groq yang digunakan seluruh agent |
| `DB_URL`       | PostgreSQL connection string                                  |
| `GITHUB_TOKEN` | GitHub Personal Access Token                                  |

> Pastikan `.env` tidak dimasukkan ke repository publik.

---

# ▶️ Running the Application

CrewOS Agent membutuhkan **tiga proses backend** yang berjalan secara independen.

Buka tiga terminal.

### Terminal 1 — Data & Analyst Agent

```bash
python a2a/service.py
```

Service berjalan pada:

```text
http://localhost:8001
```

---

### Terminal 2 — Planning Agent

```bash
python a2a/service_planning.py
```

Service berjalan pada:

```text
http://localhost:8002
```

---

### Terminal 3 — Agentic Orchestrator

```bash
python main.py
```

Service utama berjalan pada:

```text
http://localhost:8000
```

---

## Open the Application

Buka browser:

```text
http://localhost:8000/app
```

Anda akan melihat antarmuka chat yang terhubung dengan kedua agen spesialis.

---

# 💬 Contoh Penggunaan

## Contoh 1 — Analisis Developer

```text
Tampilkan statistik developer.
```

Sistem akan:

```text
User
  ↓
Orchestrator
  ↓
Data & Analyst Agent
  ↓
PostgreSQL
  ↓
Developer Statistics
  ↓
User
```

---

## Contoh 2 — Membuat Rencana Proyek

Input:

```text
Buatkan rencana kerja untuk aplikasi manajemen proyek
dengan fitur login, dashboard, manajemen task, dan notifikasi.
```

Sistem menghasilkan draft.

```text
Planning Agent
      ↓
Project Plan Draft
      ↓
"Apakah Anda menyetujui rencana ini?"
      ↓
     YES
      ↓
PostgreSQL
```

---

# 🧑‍⚖️ Human-in-the-Loop Workflow

```text
┌─────────────────────┐
│ User Requirement    │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ Planning Agent      │
│ Generates Draft     │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ Human Review        │
└──────────┬──────────┘
           │
      ┌────┴────┐
      ▼         ▼
    Reject    Approve
      │         │
      ▼         ▼
 Revise      Save to
 Plan       Database
```

---

# 🛡️ Security & Guardrails

CrewOS Agent menerapkan:

* Input sanitization.
* Plan text cleaning.
* Error handling.
* Pencegahan kebocoran traceback mentah.
* Validasi repository GitHub.

Salah satu fungsi validasi repository telah tersedia di kode, namun belum dipanggil pada alur aplikasi utama.

---

# 📊 Pemenuhan Komponen Agentic AI

| Komponen              | Status            | Implementasi                                                       |
| --------------------- | ----------------- | ------------------------------------------------------------------ |
| **Agno**              | ✅ Terimplementasi | Tiga Agent Agno dengan tools masing-masing                         |
| **Multi-Agent**       | ✅ Terimplementasi | Orchestrator + Data Agent + Planning Agent                         |
| **A2A**               | ✅ Gaya A2A        | Microservice independen berkomunikasi melalui HTTP/REST            |
| **MCP**               | ⚠️ Sebagian       | Tools function-calling native Agno, belum MCP client-server formal |
| **Guardrails**        | ✅ Terimplementasi | Sanitasi, cleaning, error handling                                 |
| **Human-in-the-Loop** | ✅ Terimplementasi | Persetujuan eksplisit sebelum penyimpanan rencana                  |

---

# ⚠️ Current Limitations

Beberapa kemampuan berikut masih menjadi area pengembangan:

### 1. Skill Detection

Saat ini:

```text
detected_skills = "General Dev"
estimated_role = "Software Engineer"
```

Nilainya masih bersifat tetap dan belum dihasilkan dari analisis AI terhadap isi commit.

### 2. AI Commit Summary

`summary_ai` masih berupa penggabungan string sederhana dan belum menggunakan LLM untuk melakukan peringkasan commit.

### 3. Project Risk Detection

Belum tersedia fitur:

* Deteksi risiko keterlambatan proyek.
* Prediksi keterlambatan task.
* Analisis bottleneck tim.

### 4. HR Integration

Belum tersedia integrasi dengan:

* Data HR.
* Profil skill resmi karyawan.
* Riwayat proyek perusahaan.

### 5. Frontend Branding

Beberapa teks pada frontend masih menggunakan branding lama dan perlu disesuaikan sepenuhnya dengan identitas **CrewOS Agent**.

---

# 🗺️ Roadmap

```text
Current Version
     │
     ├── GitHub Commit Collection
     ├── Developer Statistics
     ├── AI Project Planning
     ├── Human-in-the-Loop
     └── Multi-Agent Orchestration
              │
              ▼
Future Development
     │
     ├── AI-based Skill Detection
     ├── AI Commit Summarization
     ├── Developer Skill Profiling
     ├── Task Assignment Recommendation
     ├── Project Delay Risk Detection
     ├── HR System Integration
     └── Advanced Project Progress Intelligence
```

---

# 📖 Documentation

Dokumentasi pendukung:

* `CrewOS_Agent_Laporan_Proyek.docx`
* Materi Presentasi (`.pptx`)
* `arsitektur_tersemat.png`
* `hitl_nyata.png`

Dokumentasi lengkap mencakup:

* Diagram arsitektur.
* Alur komunikasi agent.
* Penjelasan komponen Agno.
* Implementasi A2A.
* Tools dan integrasi data.
* Guardrails.
* Human-in-the-Loop.
* Bukti implementasi sistem.

---

# 👩‍💻 Author

**ima**
AI Engineer — Spesialis Agentic AI

---

## 📄 License

Proyek ini dikembangkan untuk keperluan pembelajaran, pengembangan, dan implementasi sistem Agentic AI.

---

<div align="center">

**CrewOS Agent**

*From Passive Project Monitoring to Intelligent Agentic Assistance.*

</div>
