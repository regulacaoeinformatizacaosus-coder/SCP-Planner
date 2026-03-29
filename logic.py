from database import conectar_db
from datetime import datetime

class Categoria:
    @staticmethod
    def adicionar(nome, cor="#1f538d"):
        conn, cursor = conectar_db()
        try:
            cursor.execute("INSERT INTO categorias (nome, cor) VALUES (?, ?)", (nome, cor))
            conn.commit()
            return cursor.lastrowid
        except: return None
        finally: conn.close()

    @staticmethod
    def atualizar(categoria_id, nome, cor):
        conn, cursor = conectar_db()
        cursor.execute("UPDATE categorias SET nome = ?, cor = ? WHERE id = ?", (nome, cor, categoria_id))
        conn.commit()
        conn.close()

    @staticmethod
    def listar():
        conn, cursor = conectar_db()
        cursor.execute("SELECT * FROM categorias ORDER BY nome")
        res = cursor.fetchall()
        conn.close()
        return res

    @staticmethod
    def obter_por_id(categoria_id):
        conn, cursor = conectar_db()
        cursor.execute("SELECT * FROM categorias WHERE id = ?", (categoria_id,))
        res = cursor.fetchone()
        conn.close()
        return res

class Tarefa:
    @staticmethod
    def adicionar(titulo, data_vencimento=None, categoria_id=1, priority=1, alert_interval=0):
        conn, cursor = conectar_db()
        data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(data_vencimento, datetime):
            data_vencimento = data_vencimento.strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO tarefas (titulo, data_criacao, data_vencimento, priority, categoria_id, alert_interval) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (titulo, data_criacao, data_vencimento, priority, categoria_id, alert_interval))
        conn.commit()
        conn.close()

    @staticmethod
    def listar_pendentes_por_categoria(categoria_id):
        conn, cursor = conectar_db()
        cursor.execute("""
            SELECT t.*, c.nome as categoria_nome FROM tarefas t
            JOIN categorias c ON t.categoria_id = c.id
            WHERE t.status = 'Pendente' AND t.categoria_id = ?
            ORDER BY t.data_vencimento ASC, t.priority DESC
        """, (categoria_id,))
        tarefas = cursor.fetchall()
        conn.close()
        return tarefas

    @staticmethod
    def listar_todas_pendentes():
        conn, cursor = conectar_db()
        cursor.execute("""
            SELECT t.*, c.nome as categoria_nome FROM tarefas t
            JOIN categorias c ON t.categoria_id = c.id
            WHERE t.status = 'Pendente'
            ORDER BY t.data_vencimento ASC, t.priority DESC
        """)
        tarefas = cursor.fetchall()
        conn.close()
        return tarefas

    @staticmethod
    def obter_por_id(tarefa_id):
        conn, cursor = conectar_db()
        cursor.execute("SELECT t.*, c.nome as categoria_nome FROM tarefas t JOIN categorias c ON t.categoria_id = c.id WHERE t.id = ?", (tarefa_id,))
        tarefa = cursor.fetchone()
        conn.close()
        return tarefa

    @staticmethod
    def atualizar(tarefa_id, titulo, data_vencimento, priority, categoria_id, alert_interval):
        conn, cursor = conectar_db()
        if isinstance(data_vencimento, datetime):
            data_vencimento = data_vencimento.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            UPDATE tarefas SET titulo = ?, data_vencimento = ?, priority = ?, categoria_id = ?, alert_interval = ?
            WHERE id = ?
        """, (titulo, data_vencimento, priority, categoria_id, alert_interval, tarefa_id))
        conn.commit()
        conn.close()

    @staticmethod
    def concluir(tarefa_id):
        conn, cursor = conectar_db()
        cursor.execute("UPDATE tarefas SET status = 'Concluida' WHERE id = ?", (tarefa_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def excluir(tarefa_id):
        conn, cursor = conectar_db()
        cursor.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def registrar_alerta_enviado(tarefa_id, horario_str):
        conn, cursor = conectar_db()
        cursor.execute("UPDATE tarefas SET notificado = 1, last_alerted_at = ? WHERE id = ?", (horario_str, tarefa_id))
        conn.commit()
        conn.close()