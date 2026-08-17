import os
import requests
from dotenv import load_dotenv

# Memuat file .env
load_dotenv()

# Ambil token dari environment variable
token = os.getenv("GITHUB_TOKEN")

print(f"Token yang terbaca: {token[:10]}... (dipotong untuk keamanan)" if token else "❌ GITHUB_TOKEN tidak ditemukan di environment!")


url = "https://api.github.com/user"
headers = {
    "Accept": "vnd.github+json",
    "User-Agent": "Agno-Agent",
    "Authorization": f"Bearer {token}"
}

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ Berhasil! Token valid atas nama akun: {user_data.get('login')}")
    else:
        print(f"❌ Gagal! Respons dari GitHub: {response.text}")
except Exception as e:
    print(f"❌ Terjadi kesalahan koneksi: {str(e)}")