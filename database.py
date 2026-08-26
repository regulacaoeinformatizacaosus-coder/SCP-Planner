import sqlite3
import re

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
            mes_referencia TEXT,
            prestador TEXT DEFAULT '',
            tipo_pagamento TEXT DEFAULT '',
            financiamento TEXT DEFAULT '',
            observacao TEXT DEFAULT '',
            FOREIGN KEY (categoria_id) REFERENCES categorias (id) ON DELETE SET NULL
        )
    """)
    
    # Tenta adicionar a coluna 'cor' caso o banco já exista sem ela
    try: cursor.execute("ALTER TABLE categorias ADD COLUMN cor TEXT DEFAULT '#1f538d'")
    except: pass

    for coluna, definicao in [
        ('mes_referencia', "TEXT"),
        ('prestador', "TEXT DEFAULT ''"),
        ('tipo_pagamento', "TEXT DEFAULT ''"),
        ('financiamento', "TEXT DEFAULT ''"),
        ('observacao', "TEXT DEFAULT ''"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE tarefas ADD COLUMN {coluna} {definicao}")
        except sqlite3.OperationalError:
            pass

    cursor.execute("UPDATE tarefas SET mes_referencia = substr(COALESCE(data_vencimento, data_criacao), 1, 7) WHERE mes_referencia IS NULL")

    cursor.execute("SELECT id, titulo, prestador FROM tarefas")
    for tarefa_id, titulo, prestador in cursor.fetchall():
        match = re.match(r"^\s*(FAEC|MAC|OPME)\s*(?:-\s*)?(.*)$", titulo or "", re.IGNORECASE)
        if not match:
            continue
        financiamento = "MUNICIPAL" if match.group(1).upper() == "OPME" else match.group(1).upper()
        tipo = match.group(2).strip()
        if prestador:
            marcador_prestador = f" - {prestador}".upper()
            posicao_prestador = tipo.upper().find(marcador_prestador)
            if posicao_prestador >= 0:
                tipo = tipo[:posicao_prestador].strip()
        cursor.execute(
            "UPDATE tarefas SET financiamento = ?, tipo_pagamento = ? WHERE id = ?",
            (financiamento, tipo, tarefa_id),
        )

    cursor.execute("INSERT OR IGNORE INTO categorias (nome, cor) VALUES (?, ?)", ("Geral", "#1f538d"))
    conn.commit()
    conn.close()