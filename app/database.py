import sqlite3
import datetime
from app.config import DB_NAME

def create_tables():
    """Membuat tabel database jika belum ada."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS airdrops (
        id INTEGER PRIMARY KEY,
        project_name TEXT,
        description TEXT,
        registration_link TEXT,
        forward_date DATETIME,
        source_channel TEXT,
        status TEXT DEFAULT 'registered',
        notes TEXT,
        original_message_id INTEGER,
        message_text TEXT,
        source_link TEXT
    )
    ''')
    
    # Periksa apakah kolom source_link sudah ada, jika belum tambahkan
    cursor.execute("PRAGMA table_info(airdrops)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'source_link' not in columns:
        cursor.execute('ALTER TABLE airdrops ADD COLUMN source_link TEXT')
    
    conn.commit()
    conn.close()

def add_airdrop(project_name, description, registration_link, forward_date, 
               source_channel, original_message_id, message_text, source_link=""):
    """Menambahkan airdrop baru ke database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO airdrops (project_name, description, registration_link, forward_date, 
                         source_channel, original_message_id, message_text, source_link)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (project_name, description, registration_link, forward_date, 
         source_channel, original_message_id, message_text, source_link))
    
    airdrop_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return airdrop_id

def get_all_airdrops():
    """Mendapatkan semua airdrop dari database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM airdrops ORDER BY forward_date DESC')
    result = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return result

def get_airdrop_by_id(airdrop_id):
    """Mendapatkan airdrop berdasarkan ID."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM airdrops WHERE id = ?', (airdrop_id,))
    result = cursor.fetchone()
    
    conn.close()
    return dict(result) if result else None

def search_airdrops(keyword):
    """Mencari airdrop berdasarkan kata kunci."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT * FROM airdrops 
    WHERE project_name LIKE ? OR description LIKE ? OR message_text LIKE ?
    ORDER BY forward_date DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
    
    result = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return result

def update_airdrop_status(airdrop_id, status):
    """Mengubah status airdrop."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE airdrops SET status = ? WHERE id = ?', (status, airdrop_id))
    conn.commit()
    
    conn.close()
    return cursor.rowcount > 0

def add_notes(airdrop_id, notes):
    """Menambahkan catatan ke airdrop."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE airdrops SET notes = ? WHERE id = ?', (notes, airdrop_id))
    conn.commit()
    
    conn.close()
    return cursor.rowcount > 0

def delete_airdrop(airdrop_id):
    """Menghapus airdrop dari database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM airdrops WHERE id = ?', (airdrop_id,))
    conn.commit()
    
    conn.close()
    return cursor.rowcount > 0 