# root/mcp/dev_tool.py

from typing import List
from mcp.database import get_db_connection, release_db_connection

def save_analyzed_developer_data(
    repo_owner: str,
    repo_name: str,
    commit_sha: str,
    author_name: str,
    author_email: str,
    commit_message: str,
    committed_at: str,
    detected_skills: List[str],
    estimated_role: str,
    summary_ai: str
) -> str:
    """ini untuk Menyimpan data hasil analisis developer ke database untuk informasi ke depan."""
    insert_profile_sql = """
        INSERT INTO developer_profiles (author_name, author_email, estimated_role, detected_skills, summary_ai)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (author_email) DO UPDATE 
        SET author_name = EXCLUDED.author_name,
            estimated_role = EXCLUDED.estimated_role,
            detected_skills = EXCLUDED.detected_skills,
            summary_ai = EXCLUDED.summary_ai,
            updated_at = CURRENT_TIMESTAMP;
    """

    insert_commit_sql = """
        INSERT INTO github_commits 
        (repo_owner, repo_name, commit_sha, author_name, author_email, commit_message, committed_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT ON CONSTRAINT unique_repo_commit DO NOTHING;
    """

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute Query 1: Profile
        cursor.execute(insert_profile_sql, (
            author_name, author_email, estimated_role, detected_skills, summary_ai
        ))
        # Execute Query 2: Commit
        cursor.execute(insert_commit_sql, (
            repo_owner, repo_name, commit_sha, author_name, author_email, commit_message, committed_at
        ))

        conn.commit()
        cursor.close()

        return f"✅ Berhasil menyimpan commit [{commit_sha[:7]}] & profil {author_name} ({estimated_role})."
    except Exception as e:
        return f"❌ Gagal menyimpan ke database: {str(e)}"
    finally:
        
        if conn:
            release_db_connection(conn)