"""
App de Ponto (Kivy) - arquivo único: main.py
Funcionalidades:
- Registrar entrada/saída
- Histórico com listagem
- Exportar CSV e PDF (ReportLab)
- Salvamento em CSV local

Como usar (desktop):
- pip install kivy reportlab
- python main.py

Para gerar APK (Android): usar Buildozer (Linux/WSL). Ex.: buildozer init -> ajustar spec -> buildozer android debug

OBS: Em Android pode ser necessário ajustar permissões de escrita e dependências (reportlab pode aumentar tamanho do APK).
"""

import datetime
import csv
import os
from io import BytesIO

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas as pdf_canvas
    REPORTLAB_AVAILABLE = True
    
except Exception:
    REPORTLAB_AVAILABLE = False

ARQUIVO_PONTO = 'registros_ponto.csv'

KV = r"""
ScreenManager:
    MainScreen:
    HistoryScreen:
    SettingsScreen:

<MainScreen>:
    name: 'main'
    
    BoxLayout:
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(12)

        Label:
            text: 'App de Ponto'
            font_size: '24sp'
            size_hint_y: None
            height: dp(40)

        BoxLayout:
            size_hint_y: None
            height: dp(60)
            spacing: dp(10)

            Button:
                text: 'Registrar Entrada'
                on_press: root.registrar_entrada()

            Button:
                text: 'Registrar Saída'
                on_press: root.registrar_saida()

        BoxLayout:
            size_hint_y: None
            height: dp(60)
            spacing: dp(10)

            Button:
                text: 'Ver Histórico'
                on_press: app.root.transition.direction = 'left'; app.root.current = 'history'

            Button:
                text: 'Exportar CSV'
                on_press: root.exportar_csv()

        BoxLayout:
            size_hint_y: None
            height: dp(60)
            spacing: dp(10)

            Button:
                text: 'Exportar PDF'
                on_press: root.exportar_pdf()

            Button:
                text: 'Configurações'
                on_press: app.root.transition.direction = 'left'; app.root.current = 'settings'

        Label:
            id: lbl_status
            text: root.status_text
            size_hint_y: None
            height: dp(120)
            text_size: self.width - dp(20), None
            halign: 'left'
            valign: 'top'

<HistoryItem@BoxLayout>:
    data: ''
    tipo: ''
    hora: ''
    tempo: ''
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(40)
    padding: dp(6)

    Label:
        text: root.data
        
    Label:
        text: root.tipo
        
    Label:
        text: root.hora
        
    Label:
        text: root.tempo

<HistoryScreen>:
    name: 'history'
    
    BoxLayout:
        orientation: 'vertical'
        padding: dp(12)
        spacing: dp(8)

        BoxLayout:
            size_hint_y: None
            height: dp(48)
            spacing: dp(8)

            Button:
                text: 'Voltar'
                on_press: app.root.transition.direction = 'right'; app.root.current = 'main'
                
            Button:
                text: 'Limpar Histórico'
                on_press: root.limpar_historico()
                
            Button:
                text: 'Atualizar'
                on_press: root.carregar_lista()

        ScrollView:
            GridLayout:
                id: grid
                cols: 1
                size_hint_y: None
                row_default_height: dp(40)
                height: self.minimum_height
                spacing: dp(4)
                padding: dp(4)

<SettingsScreen>:
    name: 'settings'
    
    BoxLayout:
        orientation: 'vertical'
        padding: dp(12)
        spacing: dp(8)

        BoxLayout:
            size_hint_y: None
            height: dp(48)

            Button:
                text: 'Voltar'
                on_press: app.root.transition.direction = 'right'; app.root.current = 'main'

        Label:
            text: 'Configurações (simples)\n- Arquivo: ' + root.arquivo
            halign: 'left'
            valign: 'top'

        Button:
            text: 'Abrir pasta do app'
            on_press: root.abrir_pasta_app()

"""

def garantir_arquivo():
    if not os.path.exists(ARQUIVO_PONTO):
        with open(ARQUIVO_PONTO, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['data', 'hora', 'tipo', 'tempo_trabalhado'])
            writer.writeheader()

def carregar_registros():
    garantir_arquivo()
    with open(ARQUIVO_PONTO, 'r', newline='') as f:
        reader = csv.DictReader(f)
        return list(reader)

def salvar_registros(registros):
    with open(ARQUIVO_PONTO, 'w', newline='') as f:
        fieldnames = ['data', 'hora', 'tipo', 'tempo_trabalhado']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for r in registros:
            writer.writerow(r)

def calcular_tempo(entrada_hora_str, saida_hora_str):
    fmt = '%H:%M:%S'
    
    try:
        ent = datetime.datetime.strptime(entrada_hora_str, fmt)
        sai = datetime.datetime.strptime(saida_hora_str, fmt)
        
    except Exception:
        return '0h 0m'

    delta = sai - ent
    
    if delta.days < 0:
        delta = datetime.timedelta(seconds=delta.seconds)
        
    horas = delta.seconds // 3600
    minutos = (delta.seconds % 3600) // 60
    
    return f"{horas}h {minutos}m"

class MainScreen(Screen):
    status_text = StringProperty('Pronto')

    def registrar_entrada(self):
        agora = datetime.datetime.now()
        data = agora.strftime('%Y-%m-%d')
        hora = agora.strftime('%H:%M:%S')

        registros = carregar_registros()
        
        for r in registros:
            if r['data'] == data and r['tipo'] == 'entrada':
                self.status_text = 'Entrada já registrada hoje.'
                return

        novo = {'data': data, 'hora': hora, 'tipo': 'entrada', 'tempo_trabalhado': ''}
        registros.append(novo)
        salvar_registros(registros)
        self.status_text = f'Entrada registrada: {data} às {hora}'

    def registrar_saida(self):
        agora = datetime.datetime.now()
        data = agora.strftime('%Y-%m-%d')
        hora = agora.strftime('%H:%M:%S')

        registros = carregar_registros()
        entrada_hoje = None
        
        for r in reversed(registros):
            if r['data'] == data and r['tipo'] == 'entrada':
                entrada_hoje = r
                break

        if not entrada_hoje:
            self.status_text = 'Nenhuma entrada registrada para hoje. Registre a entrada primeiro.'
            return

        tempo = calcular_tempo(entrada_hoje['hora'], hora)
        novo = {'data': data, 'hora': hora, 'tipo': 'saida', 'tempo_trabalhado': tempo}
        registros.append(novo)
        salvar_registros(registros)
        self.status_text = f'Saída registrada: {data} às {hora} — Tempo: {tempo}'

    def exportar_csv(self):
        garantir_arquivo()
        dest = os.path.abspath(ARQUIVO_PONTO)
        self._popup_info('Exportar CSV', f'Arquivo salvo em:\n{dest}')

    def exportar_pdf(self):
        if not REPORTLAB_AVAILABLE:
            self._popup_info('Exportar PDF', 'ReportLab não está disponível. Instale "reportlab" para exportar PDFs.')
            return

        registros = carregar_registros()
        if not registros:
            self._popup_info('Exportar PDF', 'Nenhum registro a exportar.')
            return

        now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_pdf = f'ponto_{now}.pdf'
        caminho = os.path.abspath(nome_pdf)

        try:
            c = pdf_canvas.Canvas(caminho, pagesize=A4)
            largura, altura = A4
            margem_x = 40
            y = altura - 60

            c.setFont('Helvetica-Bold', 16)
            c.drawString(margem_x, y, 'Relatório de Ponto')
            y -= 30
            c.setFont('Helvetica', 10)
            c.drawString(margem_x, y, f'Gerado em: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            y -= 25

            c.setFont('Helvetica-Bold', 10)
            c.drawString(margem_x, y, 'Data')
            c.drawString(margem_x+100, y, 'Tipo')
            c.drawString(margem_x+180, y, 'Hora')
            c.drawString(margem_x+300, y, 'Tempo')
            y -= 18
            c.setFont('Helvetica', 9)

            for r in registros:
                if y < 80:
                    c.showPage()
                    y = altura - 60
                c.drawString(margem_x, y, r['data'])
                c.drawString(margem_x+100, y, r['tipo'])
                c.drawString(margem_x+180, y, r['hora'])
                c.drawString(margem_x+300, y, r.get('tempo_trabalhado', ''))
                y -= 16

            c.save()
            self._popup_info('Exportar PDF', f'PDF salvo em:\n{caminho}')
            
        except Exception as e:
            self._popup_info('Exportar PDF', f'Erro ao gerar PDF:\n{e}')

    def _popup_info(self, title, message):
        content = BoxLayout(orientation='vertical', padding=8, spacing=8)
        content.add_widget(Label(text=message))
        btn = Button(text='OK', size_hint_y=None, height=40)
        content.add_widget(btn)
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        btn.bind(on_release=popup.dismiss)
        popup.open()

class HistoryScreen(Screen):
    def on_enter(self):
        self.carregar_lista()

    def carregar_lista(self):
        grid = self.ids.grid
        grid.clear_widgets()
        registros = carregar_registros()
        
        if not registros:
            grid.add_widget(Label(text='Nenhum registro encontrado', size_hint_y=None, height=40))
            return

        header = BoxLayout(size_hint_y=None, height=30)
        header.add_widget(Label(text='Data'))
        header.add_widget(Label(text='Tipo'))
        header.add_widget(Label(text='Hora'))
        header.add_widget(Label(text='Tempo'))
        grid.add_widget(header)

        for r in registros:
            item = BoxLayout(size_hint_y=None, height=36)
            item.add_widget(Label(text=r['data']))
            item.add_widget(Label(text=r['tipo']))
            item.add_widget(Label(text=r['hora']))
            item.add_widget(Label(text=r.get('tempo_trabalhado', '')))
            grid.add_widget(item)

    def limpar_historico(self):
        content = BoxLayout(orientation='vertical', spacing=8, padding=8)
        content.add_widget(Label(text='Deseja limpar todo o histórico? Esta ação não pode ser desfeita.'))
        btns = BoxLayout(size_hint_y=None, height=40, spacing=8)
        btn_yes = Button(text='Sim')
        btn_no = Button(text='Não')
        btns.add_widget(btn_yes)
        btns.add_widget(btn_no)
        content.add_widget(btns)
        popup = Popup(title='Confirmar', content=content, size_hint=(0.85, 0.45))

        def confirmar(*a):
            salvar_registros([])
            popup.dismiss()
            self.carregar_lista()

        btn_yes.bind(on_release=confirmar)
        btn_no.bind(on_release=popup.dismiss)
        popup.open()

class SettingsScreen(Screen):
    arquivo = StringProperty(ARQUIVO_PONTO)

    def abrir_pasta_app(self):
        caminho = os.path.abspath('.')
        
        try:
            if os.name == 'nt':
                os.startfile(caminho)
                
            elif os.name == 'posix':
                try:
                    os.system(f'xdg-open "{caminho}"')
                    
                except Exception:
                    os.system(f'open "{caminho}"')
                    
            self._popup('Pasta aberta', caminho)
            
        except Exception as e:
            self._popup('Erro', str(e))

    def _popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()

class PontoApp(App):
    def build(self):
        Window.size = (420, 720)
        Builder.load_string(KV)
        sm = self.root
        
        if not sm:
            sm = ScreenManager()
            
        garantir_arquivo()
        
        return Builder.load_string(KV)

if __name__ == '__main__':
    PontoApp().run()
