# root/guardrails/guardrails.py
import re
from typing import Dict, Any

def sanitize_input(text: str) -> str:
    """Guardrail 1: Validasi & Pembersihan Masukan Input dari User."""
    if not text:
        return ""
    # Potong jika terlalu panjang untuk mencegah Prompt Injection / Token Bloat
    text = text[:1000]
    # Saring karakter liar berbahaya yang berpotensi merusak SQL / Prompt Context
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", text)
    return text.strip()

def clean_plan_text(teks: str) -> str:
    """Guardrail 2: Penyaringan Konten Teks Rencana sebelum disimpan ke Database."""
    if not teks:
        return ""
    # Menghapus kalimat konfirmasi UI standar agar teks di database bersih
    pola_saringan = r"\n*Apakah Anda ingin menyimpan rencana ini ke database\?.*$"
    teks_bersih = re.sub(pola_saringan, "", teks, flags=re.IGNORECASE | re.DOTALL)
    return teks_bersih.strip()

def validate_github_repo(repo_owner: str, repo_name: str) -> bool:
    """Guardrail 3: Validasi format Repository GitHub."""
    pattern = r"^[a-zA-Z0-9_\-]+$"
    return bool(re.match(pattern, repo_owner)) and bool(re.match(pattern, repo_name))

def handle_service_error(e: Exception, context_msg: str) -> Dict[str, Any]:
    """Guardrail 4: Standardisasi Penanganan Failures (Failure Handling)."""
    error_str = str(e)
    # Jangan melempar error traceback mentah ke user/UI
    return {
        "status": "error",
        "message": f"❌ Batasan Sistem ({context_msg}): {error_str[:150]}"
    }