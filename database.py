import sqlite3
from datetime import datetime

class PontoDB:
    def __init__(self, db_name="ponto.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.criar_tabela()

    def criar_tabela(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT,
                hora TEXT,
                tipo TEXT,
                tempo_trabalhado TEXT
            )
        """)
        self.conn.commit()

    def registrar_entrada(self):
        agora = datetime.now()
        data = agora.strftime('%Y-%m-%d')
        hora = agora.strftime('%H:%M:%S')

        self.cursor.execute(
            "SELECT * FROM registros WHERE data=? AND tipo='entrada'",
            (data,)
        )
        if self.cursor.fetchone():
            return False, "Entrada já registrada hoje."

        self.cursor.execute(
            "INSERT INTO registros (data, hora, tipo) VALUES (?, ?, 'entrada')",
            (data, hora)
        )
        self.conn.commit()
        return True, f"Entrada registrada às {hora}"

    def registrar_saida(self):
        agora = datetime.now()
        data = agora.strftime('%Y-%m-%d')
        hora_saida = agora.strftime('%H:%M:%S')

        self.cursor.execute(
            "SELECT * FROM registros WHERE data=? AND tipo='entrada'",
            (data,)
        )
        entrada = self.cursor.fetchone()

        if not entrada:
            return False, "Nenhuma entrada registrada hoje."

        hora_entrada = datetime.strptime(entrada[2], '%H:%M:%S')
        hora_saida_dt = datetime.strptime(hora_saida, '%H:%M:%S')

        tempo = hora_saida_dt - hora_entrada
        horas = tempo.seconds // 3600
        minutos = (tempo.seconds % 3600) // 60
        tempo_str = f"{horas}h {minutos}m"

        self.cursor.execute(
            "INSERT INTO registros (data, hora, tipo, tempo_trabalhado) VALUES (?, ?, 'saida', ?)",
            (data, hora_saida, tempo_str)
        )
        self.conn.commit()
        return True, f"Saída registrada. Tempo trabalhado: {tempo_str}"

    def listar(self):
        self.cursor.execute(
            "SELECT data, hora, tipo, COALESCE(tempo_trabalhado,'N/A') FROM registros"
        )
        return self.cursor.fetchall()
