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
    def adicionar(titulo, data_vencimento=None, categoria_id=1, priority=1, alert_interval=0,
                  prestador='', tipo_pagamento='', financiamento='', mes_referencia=None, observacao=''):
        conn, cursor = conectar_db()
        data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(data_vencimento, datetime):
            data_vencimento = data_vencimento.strftime("%Y-%m-%d %H:%M:%S")
        mes_referencia = mes_referencia or (data_vencimento or data_criacao)[:7]

        cursor.execute("""
            INSERT INTO tarefas (titulo, data_criacao, data_vencimento, priority, categoria_id, alert_interval,
                                                                 mes_referencia, prestador, tipo_pagamento, financiamento, observacao)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (titulo, data_criacao, data_vencimento, priority, categoria_id, alert_interval,
                            mes_referencia, prestador, tipo_pagamento, financiamento, observacao))
        conn.commit()
        conn.close()

    @staticmethod
    def listar_por_mes(mes_referencia, categoria_id=None):
        conn, cursor = conectar_db()
        consulta = """
            SELECT t.*, c.nome as categoria_nome FROM tarefas t
            JOIN categorias c ON t.categoria_id = c.id
            WHERE t.mes_referencia = ?
        """
        parametros = [mes_referencia]
        if categoria_id is not None:
            consulta += " AND t.categoria_id = ?"
            parametros.append(categoria_id)
        consulta += " ORDER BY t.status DESC, t.data_vencimento ASC, t.priority DESC"
        cursor.execute(consulta, parametros)
        tarefas = cursor.fetchall()
        conn.close()
        return tarefas

    @staticmethod
    def listar_por_categoria(categoria_id):
        conn, cursor = conectar_db()
        cursor.execute("""
            SELECT t.*, c.nome as categoria_nome FROM tarefas t
            JOIN categorias c ON t.categoria_id = c.id
            WHERE t.categoria_id = ?
            ORDER BY t.status DESC, t.data_vencimento ASC, t.priority DESC
        """, (categoria_id,))
        tarefas = cursor.fetchall()
        conn.close()
        return tarefas

    @staticmethod
    def listar_todas_pendentes(mes_referencia=None):
        conn, cursor = conectar_db()
        consulta = """
            SELECT t.*, c.nome as categoria_nome FROM tarefas t
            JOIN categorias c ON t.categoria_id = c.id
            WHERE t.status = 'Pendente'
            ORDER BY t.data_vencimento ASC, t.priority DESC
        """
        if mes_referencia:
            consulta = consulta.replace("WHERE t.status", "WHERE t.mes_referencia = ? AND t.status")
            cursor.execute(consulta, (mes_referencia,))
        else:
            cursor.execute(consulta)
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
    def atualizar(tarefa_id, titulo, data_vencimento, priority, categoria_id, alert_interval,
                  prestador, tipo_pagamento, financiamento, mes_referencia, observacao):
        conn, cursor = conectar_db()
        if isinstance(data_vencimento, datetime):
            data_vencimento = data_vencimento.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
                        UPDATE tarefas SET titulo = ?, data_vencimento = ?, priority = ?, categoria_id = ?, alert_interval = ?,
                                prestador = ?, tipo_pagamento = ?, financiamento = ?, mes_referencia = ?
                                , observacao = ?
            WHERE id = ?
                """, (titulo, data_vencimento, priority, categoria_id, alert_interval, prestador,
                            tipo_pagamento, financiamento, mes_referencia, observacao, tarefa_id))
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

    @staticmethod
    def reabrir(tarefa_id):
        conn, cursor = conectar_db()
        cursor.execute("UPDATE tarefas SET status = 'Pendente' WHERE id = ?", (tarefa_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def copiar_mes_anterior(mes_atual):
        conn, cursor = conectar_db()
        ano, mes = map(int, mes_atual.split('-'))
        mes_anterior = f"{ano - 1:04d}-12" if mes == 1 else f"{ano:04d}-{mes - 1:02d}"
        cursor.execute("""
            INSERT INTO tarefas (titulo, data_criacao, data_vencimento, priority, categoria_id, alert_interval,
                mes_referencia, prestador, tipo_pagamento, financiamento, observacao)
            SELECT titulo, ?, CASE WHEN data_vencimento IS NULL THEN NULL ELSE ? || substr(data_vencimento, 8) END,
                priority, categoria_id, alert_interval, ?, prestador,
                tipo_pagamento, financiamento, observacao
            FROM tarefas AS origem
            WHERE mes_referencia = ?
              AND NOT EXISTS (
                  SELECT 1 FROM tarefas AS destino
                  WHERE destino.mes_referencia = ?
                    AND destino.titulo = origem.titulo
                    AND destino.prestador = origem.prestador
              )
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), mes_atual, mes_atual,
              mes_anterior, mes_atual))
        total = cursor.rowcount
        conn.commit()
        conn.close()
        return total