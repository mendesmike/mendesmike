from modules import BlazeBot

import asyncio
import pickle
import json
import time

event_loop = asyncio.get_event_loop()
blaze_handler = BlazeBot()
current_sequence = None

def load_sequences(file_name='sequences.txt'):
    sequences = []
    with open('sequences.txt', 'rb') as sequence_file:
        sequences.append(pickle.load(sequence_file))
    sequence_file.close()
    return sequences

def add_sequences_handler():
    seq_amt = input("How many sequences do you want to load?: ")
    sequences = []
    for i in range(int(seq_amt)):
        current_sequence = {}
        start_seq = input("Warnning sequence (Ex: 12112) 1 - Red, 2 - Black: ")
        end_seq = input("Confirmation sequence (Ex: 121121) 1 - Red, 2 - Black: ")
        win_result = input("Win result (Ex: 1211212) 1 - Red, 2 - Black: ")
        current_sequence['start'] = start_seq
        current_sequence['end'] = end_seq
        current_sequence['win_result'] = win_result
        sequences.append(current_sequence)
        print(f"Sequence {current_sequence['win_result']} loaded")
        
    with open('sequences.txt', 'ab') as f:
        pickle.dump(sequences, f)
    f.close()
    return True

def load_sequences_handler():
    sequences = []
    with open('sequences.txt', 'rb') as sequence_file:
        sequences.append(pickle.load(sequence_file))
    sequence_file.close()
    return sequences

def analyze_sequences(spins_data, sequences):
    for sequence in sequences[0]:
        print(f"Analizando sequencia: {sequence['win_result']}")
        current_sequence_analyse = sequence['start']
        current_sequence_roullete = ""
        for spin in spins_data[:len(sequence['start'])]:
            current_sequence_roullete += str(spin['color'])
        
        if current_sequence_analyse == current_sequence_roullete:
            print(f"Sequence Analisys {current_sequence_analyse} found")
            current_sequence_roullete = ""
            return True
        else:
            print(f"Sequence Analisys {current_sequence_analyse} not found")
        current_sequence_roullete = ""
    return False

def confirm_sequences(spins_data, sequences):
    for sequence in sequences[0]:
        print(f"Analizando sequencia: {sequence['win_result']}")
        current_sequence_analyse = sequence['end']
        current_sequence_roullete = ""
        for spin in spins_data[:len(sequence['end'])]:
            current_sequence_roullete += str(spin['color'])

        if current_sequence_analyse == current_sequence_roullete:
            print(f"Sequence Confirmation {current_sequence_analyse} found")
            current_sequence_roullete = ""
            return True
        else:
            print(f"Sequence Confirmation {current_sequence_analyse} not found")
        current_sequence_roullete = ""
    return False

def win_sequences(spins_data, sequences):
    for sequence in sequences[0]:
        print(f"Analizando sequencia: {sequence['win_result']}")
        current_sequence_analyse = sequence['win_result']
        current_sequence_roullete = ""
        for spin in spins_data[:len(sequence['win_result'])]:
            current_sequence_roullete += str(spin['color'])

        if current_sequence_analyse == current_sequence_roullete:
            print(f"Sequence Result {current_sequence_analyse} found")
            current_sequence_roullete = ""
            return True
        else:
            print(f"Sequence Result {current_sequence_analyse} not found")
        current_sequence_roullete = ""
    return False

in_analisys = False
in_confirmation = False
in_win = False
add_sequences_handler()
sequences = load_sequences_handler()
while True:
    time.sleep(1)
    print("Waiting for roullete...")
    roullet_data = blaze_handler.get_roullete_data()
    if roullet_data['status'] == 'waiting':
        print("Roullete Liberated!")
        roulette_spins = blaze_handler.get_roulette_spins()
        print(f"Roullete spins: {len(roulette_spins)}")
        if not in_analisys and not in_confirmation and not in_win:
            if analyze_sequences(roulette_spins, sequences):
                in_analisys = True
                in_confirmation = False
                in_win = False
                print("Analisys sequence found")
                time.sleep(16)
            else:
                in_analisys = False
                in_confirmation = False
                in_win = False
                time.sleep(16)
        elif not in_confirmation and in_analisys:
            if confirm_sequences(roulette_spins, sequences):
                in_confirmation = True
                in_analisys = False
                in_win = False
                print("Confirm sequence found")
                time.sleep(16)
            else:
                in_analisys = False
                in_confirmation = False
                in_win = False
                time.sleep(16)
        elif not in_win and not in_analisys and in_confirmation:
            if win_sequences(roulette_spins, sequences):
                in_win = True
                in_analisys = False
                in_confirmation = False
                print("Win sequence found")
                time.sleep(16)
            else:
                in_analisys = False
                in_confirmation = False
                in_win = False
                time.sleep(16)
        else:
            in_analisys = False
            in_confirmation = False
            in_win = False
    else:
        print("Roullete is not ready yet!")
        time.sleep(1)


        
        



spin = blaze_handler.get_roulette_spins()
