# root/mcp/query

from mcp.database import get_db_connection, release_db_connection

def query_developer_stats(author_name_or_email: str = None, days: int = 90) -> str:
    
    """
    Membaca statistik atau histori commit dari database.
    
    Args:
        author_name_or_email (str): Nama atau email developer yang ingin dicari (opsional).
        days (int): Rentang waktu dalam hari untuk memfilter data (default dinaikkan ke 90 hari agar data aman).
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if author_name_or_email:
            sql = """
                SELECT c.repo_owner, c.repo_name, c.commit_sha, c.commit_message, c.committed_at, p.estimated_role, p.detected_skills, p.summary_ai
                FROM developer_profiles p
                LEFT JOIN github_commits c ON LOWER(p.author_email) = LOWER(c.author_email)
                WHERE (LOWER(p.author_name) LIKE LOWER(%s) OR LOWER(p.author_email) LIKE LOWER(%s))
                ORDER BY c.committed_at DESC;
            """
            search_param = f"%{author_name_or_email}%"
            cursor.execute(sql, (search_param, search_param))
        else:
            # Query utama untuk menampilkan semua profil pegawai yang ada di database beserta jumlah commit-nya
            sql = """
                SELECT p.author_name, p.author_email, p.estimated_role, p.detected_skills, COUNT(c.id) as total_commits
                FROM developer_profiles p
                LEFT JOIN github_commits c ON LOWER(p.author_email) = LOWER(c.author_email)
                GROUP BY p.author_name, p.author_email, p.estimated_role, p.detected_skills
                ORDER BY total_commits DESC;
            """
            cursor.execute(sql)

        rows = cursor.fetchall()
        cursor.close()

        if not rows:
            return "Belum ada data pegawai di dalam database perusahaan."

        output = []
        if author_name_or_email:
            output.append(f"=== LAPORAN AKTIVITAS DEVELOPER: {author_name_or_email} ===")
            for r in rows:
                output.append(f"• Role: {r[5]} | Skills: {r[6]}")
                output.append(f"  Summary AI: {r[7]}")
                if r[2]:
                    output.append(f"  Commit [{r[2][:7]}]: {r[3]} ({r[0]}/{r[1]})\n")
        else:
            output.append(f"=== DAFTAR PEGAWAI / DEVELOPER PERUSAHAAN ===")
            for idx, r in enumerate(rows, 1):
                skills_str = ", ".join(r[3]) if r[3] else "General Dev"
                output.append(f"{idx}. **{r[0]}** ({r[1]})")
                output.append(f"   - Role: {r[2]}")
                output.append(f"   - Skills: {skills_str}")
                output.append(f"   - Total Commit Tercatat: {r[4]}\n")

        return "\n".join(output)
    except Exception as e:
        return f"❌ Error saat query database: {str(e)}"
    finally:
        # PENTING: Kembalikan koneksi ke pool!
        if conn:
            release_db_connection(conn)