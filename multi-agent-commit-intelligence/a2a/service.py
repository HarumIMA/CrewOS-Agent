# root/a2a/service.py

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from guardrails.guardrails import validate_github_repo, sanitize_input, handle_service_error
from a2a.specialist import gemini_specialist
from mcp.github_fetcher import fetch_repo_commits_raw
from mcp.dev_tool import save_analyzed_developer_data
from mcp.query_tool import query_developer_stats

app = FastAPI(title="Company AI - Backend Specialist Service")


# --- SCHEMAS (Request Payloads) ---
class GitHubSyncRequest(BaseModel):
    repo_owner: str
    repo_name: str
    limit: int = 10

class DatabaseQueryRequest(BaseModel):
    days: int = 365
    author_query: Optional[str] = None


# --- HELPER / BACKGROUND TASKS ---
def process_github_sync_in_background(commits: list):
    """Fungsi Python murni yang berjalan terpisah di background tanpa menahan response HTTP."""
    saved_count = 0
    for c in commits:
        res = save_analyzed_developer_data(
            repo_owner=c.get("repo_owner", ""),
            repo_name=c.get("repo_name", ""),
            commit_sha=c.get("commit_sha", ""),
            author_name=c.get("author_name", ""),
            author_email=c.get("author_email", ""),
            commit_message=c.get("commit_message", ""),
            committed_at=c.get("committed_at", ""),
            detected_skills=["General Dev"],
            estimated_role="Software Engineer",
            summary_ai=f"Commit: {c.get('commit_message', '')}"
        )
        if "Berhasil" in res:
            saved_count += 1
 
    print(f"✅ [BACKGROUND TASK] Selesai menyimpan {saved_count} commit & cache diperbarui.")


# --- ENDPOINTS ---
@app.post("/api/v1/github/sync")
async def sync_github_endpoint(req: GitHubSyncRequest, background_tasks: BackgroundTasks):
    """Endpoint merespon seketika, eksekusi penyimpanan dilakukan di background."""
    try:
        
        commits = fetch_repo_commits_raw(req.repo_owner, req.repo_name, limit=req.limit)
        if not commits or "error" in commits[0]:
            # Ambil pesan error asli dari github_fetcher agar tahu penyebabnya (token salah/limit habis)
            error_detail = commits[0].get("error") if commits else "Unknown error"
            return {"status": "error", "message": f"Gagal mengambil repo. Detail: {error_detail}"}
        background_tasks.add_task(process_github_sync_in_background, commits)

        msg = f"Berhasil mengambil {len(commits)} commit terbaru dari repository {req.repo_owner}/{req.repo_name}. Proses ekstraksi sedang berjalan di background."
        return {
            "status": "success", 
            "result": msg,
            "message": msg
        }
    except Exception as e:
        # GUARDRAIL 4: Error Handling
        return handle_service_error(e, "Gagal sinkronisasi GitHub")


@app.post("/api/v1/database/query")
async def query_database_endpoint(req: DatabaseQueryRequest):
    try:
        # GUARDRAIL 1: Clean & Sanitize Query Author jika ada
        clean_author = sanitize_input(req.author_query) if req.author_query else None
        # LOGIKA CERDAS CACHE vs QUERY SPESIFIK:
        print(f"🔍 Melakukan Query Langsung ke Database (Author: {req.author_query}, Days: {req.days})")
        db_result = query_developer_stats(author_name_or_email=clean_author, days=req.days)
        
        prompt_summary = (
            f"Berikut adalah data asli dari database:\n\n{db_result}\n\n"
            f"Instruksi: Tampilkan seluruh daftar nama developer beserta role dan skill-nya satu per satu sesuai data di atas. "
            f"Jangan hanya memberikan angka agregat/total singkat."
        )
        
        response = gemini_specialist.run(prompt_summary)
        summary_text = response.content if hasattr(response, 'content') else str(response)

        return {"status": "success", "result": summary_text}
    except Exception as e:
        # GUARDRAIL 4: Error Handling
        return handle_service_error(e, "Gagal query database")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)