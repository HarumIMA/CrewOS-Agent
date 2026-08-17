import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ GEMINI_API_KEY tidak ditemukan di file .env!")
else:
    print(f"🔑 Menggunakan API Key: {api_key[:10]}...")
    url = f"https://generativelanguage.googleapis.com/v1beta/openai/models"
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            models = response.json().get("data", [])
            print("\n✅ Model yang TERSEDIA di akun kamu:")
            for m in models:
                print(f"  - {m['id']}")
        else:
            print(f"\n❌ Error ({response.status_code}):", response.text)
    except Exception as e:
        print("\n❌ Terjadi kesalahan koneksi:", e)