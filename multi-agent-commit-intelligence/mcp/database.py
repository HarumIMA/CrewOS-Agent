# root/mcp/database.py
import os
from dotenv import load_dotenv
from psycopg2 import pool

load_dotenv()

# Ambil DSN dari .env
db_url = os.getenv("DATABASE_URL") or os.getenv("DB_URL")

# Inisialisasi pool dengan penanganan fallback
try:
    db_pool = pool.SimpleConnectionPool(
        1, 10,
        dsn=db_url
    )
except Exception as e:
    print(f"⚠️ Warning Connection Pool: {e}")
    db_pool = None

def get_db_connection():
    """Mengambil satu koneksi aktif dari Connection Pool."""
    global db_pool
    if db_pool is None or db_pool.closed:
        db_pool = pool.SimpleConnectionPool(1, 10, dsn=db_url)
    return db_pool.getconn()

def release_db_connection(conn):
    """Mengembalikan koneksi kembali ke Connection Pool."""
    if conn and db_pool and not db_pool.closed:
        db_pool.putconn(conn)

def init_db():
    """Menyiapkan struktur tabel database secara otomatis."""
    create_tables_sql = """
    CREATE TABLE IF NOT EXISTS developer_profiles (
        id SERIAL PRIMARY KEY,
        author_name VARCHAR(100) NOT NULL,
        author_email VARCHAR(150) UNIQUE NOT NULL,
        estimated_role VARCHAR(100) DEFAULT 'Developer',
        detected_skills TEXT[],
        summary_ai TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS github_commits (
        id SERIAL PRIMARY KEY,
        repo_owner VARCHAR(100) NOT NULL,
        repo_name VARCHAR(100) NOT NULL,
        commit_sha VARCHAR(40) NOT NULL,
        author_name VARCHAR(100),
        author_email VARCHAR(150) REFERENCES developer_profiles(author_email) ON DELETE SET NULL,
        commit_message TEXT,
        committed_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT unique_repo_commit UNIQUE (repo_owner, repo_name, commit_sha)
    );
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(create_tables_sql)
        conn.commit()
        cursor.close()
        print("✅ Inisialisasi tabel database berhasil.")
    except Exception as e:
        print(f"❌ Gagal inisialisasi tabel: {str(e)}")
    finally:
        if conn:
            release_db_connection(conn)

# DUA BARIS INI PENTING: Jangan panggil init_db() langsung di top-level script!
if __name__ == "__main__":
    init_db()