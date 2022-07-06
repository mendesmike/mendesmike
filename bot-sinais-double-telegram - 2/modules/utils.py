import requests
import pickle
import os

from requests.adapters import HTTPAdapter, Retry
from datetime import datetime

def make_request(self, url, headers, post = None, req_type = "GET"):
        session = requests.Session()
        retry = Retry(
            total=5,
            read=5,
            connect=5,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504, 404, 400],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        session.headers = headers
        if req_type == "GET":
            response = session.get(url)
        elif req_type == "POST":
            response = session.post(url, data=post)
        elif req_type == "PUT":
            response = session.put(url, data=post)
        session.close()
        return response.json()

def group_menu(groups):
    i = 0 
    for group in groups:
        print(f"[{i}] - {group['title']}")
        i += 1
    selected_group = groups[int(input("Selecione o grupo que deseja enviar o sinal: "))]
    return selected_group

def save_sequences():
    seq_amt = input("Quantas sequências deseja adicionar ?: ")
    sequences = []
    for i in range(int(seq_amt)):
        current_sequence = {}
        amt_spins = input("Quantidade de giros: ")
        red_amount = input("Quantidade de vermelhos: ")
        black_amount = input("Quantidade de pretos: ")
        win_signal = input("Resultado: ")

        current_sequence['amt_spins'] = amt_spins
        current_sequence['red_amount'] = red_amount
        current_sequence['black_amount'] = black_amount
        current_sequence['win_signal'] = win_signal
        sequences.append(current_sequence)
        print(f"Sequencia {i+1} adicionada com sucesso!")
    with open('sequences.txt', 'ab') as f:
        pickle.dump(sequences, f)
    f.close()
    return True

def load_sequences():
    sequences = []
    with open('sequences.txt', 'rb') as sequence_file:
        sequences.append(pickle.load(sequence_file))
    sequence_file.close()
    return sequences

def clear_terminal():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def save_points(wins, loses, gales):
    data = {}
    data['wins'] = wins
    data['loses'] = loses
    data['gales'] = gales
    with open('points.txt', 'ab') as f:
        pickle.dump(data, f)
    f.close()

def load_points():
    points = []
    with open('points.txt', 'rb') as point_file:
        points.append(pickle.load(point_file))
    point_file.close()
    return points

def schedule_points():
    scheds = []
    amt_sched = input("Quantos pontos deseja agendar ?: ")
    for i in range(int(amt_sched)):
        hour = input("Digite o horário que deseja agendar o sinal (Ex: 10:30): ")
        hour_minute = datetime.strptime(hour, '%H:%M')
        scheds.append(hour_minute)
        print(f"Agendado placar para {hour_minute} com sucesso!")
    
    with open('placar.txt', 'ab') as f:
        pickle.dump(scheds, f)
    f.close()

def load_sched():
    scheds = []
    with open('placar.txt', 'rb') as sched_file:
        scheds.append(pickle.load(sched_file))
    sched_file.close()
    return scheds














