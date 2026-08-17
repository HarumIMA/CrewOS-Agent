# root/a2a/service_planning.py
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from guardrails.guardrails import sanitize_input, clean_plan_text, handle_service_error
from a2a.planner import planner_specialist
from planning.planning import insert_rencana, query_rencana  

app = FastAPI(title="Planning AI - Independent Microservice")

LAST_DRAFT_CACHE = {}

class PlanProcessRequest(BaseModel):
    prompt_rencana: str
    session_id: Optional[str] = "default_user_session"

class PlanSaveRequest(BaseModel):
    teks_tujuan: str
    urutan: Optional[int] = 1

class PlanQueryRequest(BaseModel):
    rencana_id: Optional[int] = None


@app.post("/api/v1/planning/process")
async def process_plan_endpoint(req: PlanProcessRequest):
    global LAST_DRAFT_CACHE
    session_key = req.session_id or "default_user_session"
    # GUARDRAIL 1: Clean & Sanitize Input User dari karakter berbahaya
    clean_prompt = sanitize_input(req.prompt_rencana)
    prompt_lower = clean_prompt.lower()

    if prompt_lower in ["iya", "ya", "simpan", "setuju", "ok", "fix simpan"]:
        draft_terakhir = LAST_DRAFT_CACHE.get(session_key)
        
        if draft_terakhir:
            # guardvile sebelum plan di save ke database
            draft_bersih = clean_plan_text(draft_terakhir)
            res_db = insert_rencana(teks_tujuan=draft_bersih, urutan=1)
            if res_db.get("status") == "success":
                LAST_DRAFT_CACHE.pop(session_key, None)
                return {
                    "status": "success", 
                    "result": f"✅ **Rencana berhasil disimpan ke database (ID: {res_db['data']['id']})!**\n\nIsi rencana:\n{draft_terakhir}"
                }
            return {"status": "error", "message": f"Gagal menyimpan ke DB: {res_db.get('message')}"}
        else:
            return {
                "status": "success", 
                "result": "Belum ada draf rencana yang dibuat. Silakan jelaskan rencana yang ingin Anda buat terlebih dahulu."
            }

    if prompt_lower in ["tidak", "batal", "gak jadi"]:
        LAST_DRAFT_CACHE.pop(session_key, None)
        return {"status": "success", "result": "Baik, draf rencana dibatalkan dan tidak disimpan."}

    try:
        response = planner_specialist.run(req.prompt_rencana, session_id=session_key)
        result_text = response.content if hasattr(response, 'content') else str(response)
        
        LAST_DRAFT_CACHE[session_key] = result_text
        return {"status": "success", "result": result_text}
    except Exception as e:
        # GUARDRAIL 4: Catch & Standardize Error Handling
        return handle_service_error(e, "Gagal memproses rencana")


@app.post("/api/v1/planning/save")
async def save_plan_endpoint(req: PlanSaveRequest):
    try:
        teks_input_clean = sanitize_input(req.teks_tujuan)
        teks_db_clean = clean_plan_text(teks_input_clean)
        res = insert_rencana(teks_tujuan=teks_db_clean, urutan=req.urutan)
        return res
    except Exception as e:
        # GUARDRAIL 4: Error Handling
        return handle_service_error(e, "Gagal menyimpan rencana")


@app.post("/api/v1/planning/query")
async def query_plan_endpoint(req: PlanQueryRequest):
    try:
        res = query_rencana(rencana_id=req.rencana_id)
        return res
    except Exception as e:
        # GUARDRAIL 4: Error Handling
        return handle_service_error(e, "Gagal mengambil rencana")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)