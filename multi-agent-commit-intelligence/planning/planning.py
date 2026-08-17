from typing import List, Dict, Any, Optional
from mcp.database import get_db_connection, release_db_connection

def insert_rencana(teks_tujuan: str, urutan: int = 1) -> Dict[str, Any]:
    """
    HANYA panggil fungsi ini JIKA USER konfirmasi setuju 
    (contoh: 'ya simpan', 'ok simpan', 'setuju', 'fix simpan') lalu simpan ke database.
    
    Args:
        teks_tujuan (str): Teks isi rencana / deskripsi tujuan.
        urutan (int): Urutan langkah/rencana (default 1).
    """
    sql = """
        INSERT INTO rencana (urutan, teks_tujuan)
        VALUES (%s, %s)
        RETURNING id, urutan, teks_tujuan, created_at;
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (urutan, teks_tujuan))
        row = cursor.fetchone()
        conn.commit()
        cursor.close()

        return {
            "status": "success",
            "message": "✅ Rencana berhasil disimpan.",
            "data": {
                "id": row[0],
                "urutan": row[1],
                "teks_tujuan": row[2],
                "created_at": str(row[3])
            }
        }
    except Exception as e:
        if conn:
            conn.rollback()
        return {
            "status": "error",
            "message": f"❌ Gagal menyimpan rencana: {str(e)}"
        }
    finally:
        if conn:
            release_db_connection(conn)


def query_rencana(rencana_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Mengambil data rencana dari database.
    
    Args:
        rencana_id (int, optional): Jika diisi, mengambil 1 rencana spesifik berdasarkan ID.
                                     Jika None, mengambil semua daftar rencana diurutkan berdasarkan kolom 'urutan'.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if rencana_id:
            sql = "SELECT id, urutan, teks_tujuan, created_at FROM rencana WHERE id = %s;"
            cursor.execute(sql, (rencana_id,))
            row = cursor.fetchone()
            cursor.close()

            if not row:
                return {"status": "error", "message": f"Rencana dengan ID {rencana_id} tidak ditemukan.", "data": None}

            return {
                "status": "success",
                "data": {
                    "id": row[0],
                    "urutan": row[1],
                    "teks_tujuan": row[2],
                    "created_at": str(row[3])
                }
            }
        else:
            sql = "SELECT id, urutan, teks_tujuan, created_at FROM rencana ORDER BY urutan ASC, id ASC;"
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()

            daftar_rencana = [
                {
                    "id": r[0],
                    "urutan": r[1],
                    "teks_tujuan": r[2],
                    "created_at": str(r[3])
                }
                for r in rows
            ]

            return {
                "status": "success",
                "count": len(daftar_rencana),
                "data": daftar_rencana
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Gagal mengambil data rencana: {str(e)}"
        }
    finally:
        if conn:
            release_db_connection(conn)