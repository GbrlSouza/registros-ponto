import datetime
import csv
import os

# Arquivo para armazenar os registros
ARQUIVO_PONTO = 'registros_ponto.csv'

# Função para registrar entrada
def registrar_entrada():
    agora = datetime.datetime.now()
    data = agora.strftime('%Y-%m-%d')
    hora = agora.strftime('%H:%M:%S')
    
    # Verifica se já existe entrada para hoje
    registros = carregar_registros()
    for reg in registros:
        if reg['data'] == data and reg['tipo'] == 'entrada':
            print("Entrada já registrada para hoje.")
            return
    
    # Adiciona nova entrada
    novo_registro = {'data': data, 'hora': hora, 'tipo': 'entrada'}
    registros.append(novo_registro)
    salvar_registros(registros)
    print(f"Entrada registrada: {data} às {hora}")

# Função para registrar saída
def registrar_saida():
    agora = datetime.datetime.now()
    data = agora.strftime('%Y-%m-%d')
    hora = agora.strftime('%H:%M:%S')
    
    # Verifica se há entrada para hoje
    registros = carregar_registros()
    entrada_hoje = None
    for reg in registros:
        if reg['data'] == data and reg['tipo'] == 'entrada':
            entrada_hoje = reg
            break
    
    if not entrada_hoje:
        print("Nenhuma entrada registrada para hoje. Registre a entrada primeiro.")
        return
    
    # Calcula tempo trabalhado
    entrada_time = datetime.datetime.strptime(entrada_hoje['hora'], '%H:%M:%S')
    saida_time = datetime.datetime.strptime(hora, '%H:%M:%S')
    tempo_trabalhado = saida_time - entrada_time
    horas = tempo_trabalhado.seconds // 3600
    minutos = (tempo_trabalhado.seconds % 3600) // 60
    
    # Adiciona saída
    novo_registro = {'data': data, 'hora': hora, 'tipo': 'saida', 'tempo_trabalhado': f"{horas}h {minutos}m"}
    registros.append(novo_registro)
    salvar_registros(registros)
    print(f"Saída registrada: {data} às {hora}. Tempo trabalhado: {horas}h {minutos}m")

# Função para ver registros
def ver_registros():
    registros = carregar_registros()
    if not registros:
        print("Nenhum registro encontrado.")
        return
    
    print("Registros de ponto:")
    for reg in registros:
        print(f"{reg['data']} - {reg['tipo']} às {reg['hora']} - Tempo: {reg.get('tempo_trabalhado', 'N/A')}")

# Função para carregar registros do arquivo
def carregar_registros():
    if not os.path.exists(ARQUIVO_PONTO):
        return []
    with open(ARQUIVO_PONTO, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        return list(reader)

# Função para salvar registros no arquivo
def salvar_registros(registros):
    with open(ARQUIVO_PONTO, mode='w', newline='') as file:
        fieldnames = ['data', 'hora', 'tipo', 'tempo_trabalhado']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for reg in registros:
            writer.writerow(reg)

# Menu principal
def menu():
    while True:
        print("\n--- App de Ponto ---")
        print("1. Registrar Entrada")
        print("2. Registrar Saída")
        print("3. Ver Registros")
        print("4. Sair")
        opcao = input("Escolha uma opção: ")
        
        if opcao == '1':
            registrar_entrada()
        elif opcao == '2':
            registrar_saida()
        elif opcao == '3':
            ver_registros()
        elif opcao == '4':
            print("Saindo...")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    menu()
