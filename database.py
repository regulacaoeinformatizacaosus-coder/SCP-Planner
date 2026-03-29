import sqlite3

DB_NAME = "gcp_v3_pro.db"

def conectar_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn, conn.cursor()

def iniciar_db():
    conn, cursor = conectar_db()
    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            cor TEXT DEFAULT '#1f538d'
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            data_criacao TEXT NOT NULL,
            data_vencimento TEXT, 
            priority INTEGER DEFAULT 1,
            status TEXT DEFAULT 'Pendente',
            categoria_id INTEGER,
            notificado INTEGER DEFAULT 0,
            alert_interval INTEGER DEFAULT 0,
            last_alerted_at TEXT,
            FOREIGN KEY (categoria_id) REFERENCES categorias (id) ON DELETE SET NULL
        )
    """)
    
    # Tenta adicionar a coluna 'cor' caso o banco já exista sem ela
    try: cursor.execute("ALTER TABLE categorias ADD COLUMN cor TEXT DEFAULT '#1f538d'")
    except: pass

    cursor.execute("INSERT OR IGNORE INTO categorias (nome, cor) VALUES (?, ?)", ("Geral", "#1f538d"))
    conn.commit()
    conn.close()