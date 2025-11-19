import datetime
import csv
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

ARQUIVO_PONTO = 'registros_ponto.csv'

class PontoApp(App):

    def build(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        btn_entrada = Button(text="Registrar Entrada", size_hint_y=None, height=60)
        btn_entrada.bind(on_press=lambda x: self.registrar_entrada())

        btn_saida = Button(text="Registrar Saída", size_hint_y=None, height=60)
        btn_saida.bind(on_press=lambda x: self.registrar_saida())

        btn_ver = Button(text="Ver Registros", size_hint_y=None, height=60)
        btn_ver.bind(on_press=lambda x: self.ver_registros())

        self.label_status = Label(text="", size_hint_y=None, height=60)

        layout.add_widget(btn_entrada)
        layout.add_widget(btn_saida)
        layout.add_widget(btn_ver)
        layout.add_widget(self.label_status)

        return layout

    def registrar_entrada(self):
        agora = datetime.datetime.now()
        
        data = agora.strftime('%Y-%m-%d')
        hora = agora.strftime('%H:%M:%S')

        registros = self.carregar_registros()
        
        for reg in registros:
            if reg['data'] == data and reg['tipo'] == 'entrada':
                self.label_status.text = "Entrada já registrada hoje."
                return

        novo = {'data': data, 'hora': hora, 'tipo': 'entrada', 'tempo_trabalhado': ''}
        registros.append(novo)
        self.salvar_registros(registros)
        self.label_status.text = f"Entrada registrada: {hora}"

    def registrar_saida(self):
        agora = datetime.datetime.now()
        data = agora.strftime('%Y-%m-%d')
        hora = agora.strftime('%H:%M:%S')

        registros = self.carregar_registros()
        entrada_hoje = next((r for r in registros if r['data'] == data and r['tipo'] == 'entrada'), None)

        if not entrada_hoje:
            self.label_status.text = "Registre a entrada primeiro."
            return

        entrada_time = datetime.datetime.strptime(entrada_hoje['hora'], '%H:%M:%S')
        saida_time = datetime.datetime.strptime(hora, '%H:%M:%S')
        tempo = saida_time - entrada_time

        horas = tempo.seconds // 3600
        minutos = (tempo.seconds % 3600) // 60

        novo = {
            'data': data,
            'hora': hora,
            'tipo': 'saida',
            'tempo_trabalhado': f"{horas}h {minutos}m"
        }
        
        registros.append(novo)
        self.salvar_registros(registros)
        self.label_status.text = f"Saída registrada: {horas}h {minutos}m"

    def ver_registros(self):
        registros = self.carregar_registros()
        
        if not registros:
            self.label_status.text = "Nenhum registro."
            return

        texto = "\n".join([f"{r['data']} - {r['tipo']} às {r['hora']} - {r.get('tempo_trabalhado','')}" for r in registros])
        self.label_status.text = texto

    def carregar_registros(self):
        if not os.path.exists(ARQUIVO_PONTO):
            return []
            
        with open(ARQUIVO_PONTO, 'r') as file:
            return list(csv.DictReader(file))

    def salvar_registros(self, registros):
        with open(ARQUIVO_PONTO, 'w', newline='') as file:
            campos = ['data', 'hora', 'tipo', 'tempo_trabalhado']
            writer = csv.DictWriter(file, fieldnames=campos)
            writer.writeheader()
            writer.writerows(registros)

if __name__ == "__main__":
    PontoApp().run()
