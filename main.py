from asyncio import events
from cmath import e
from modules import ( BlazeBot , TelegramBot )

import asyncio
import pickle
import time
import os

current_loop = asyncio.get_event_loop()
signal_msg_id = None
analisys_result = False
telegram_signal = None
blaze_signal = None


def add_sequences_handler():
    seq_amt = input("How many sequences do you want to load?: ")
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

def load_sequences_handler():
    sequences = []
    with open('sequences.txt', 'rb') as sequence_file:
        sequences.append(pickle.load(sequence_file))
    sequence_file.close()
    return sequences

def select_group(groups):
    i = 0 
    for group in groups:
        print(f"[{i}] - {group['title']}")
        i += 1
    group_id = groups[int(input("Selecione o grupo que deseja enviar o sinal: "))]
    print(f"Grupo selecionado: {group_id['title']}")
    return group_id

def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


async def run_bot(telegram_client, blaze_client, sequences, gales):
    global signal_msg_id
    global analisys_result
    global telegram_signal

    print("Buscando Grupos...")
    groups = await telegram_client.get_groups()
    selected_group = select_group(groups)
    await telegram_client.send_message(selected_group, "Iniciando Bot...")
    print("Carregando sequencias...")
    sequences = load_sequences_handler()[0]
    print(f"Sequências carregadas: {len(sequences)}")
    print(f"Quantidade de gales: {gales}")
    print("Buscando Sinais...")
    while True:
        try:
            await asyncio.sleep(1)
            roulette_data = blaze_client.get_roullete_data()
            if roulette_data['status'] == 'waiting':
                print("Roleta Liberada !")
                print(f"Analisando sequencia...")
                roulette_spins = blaze_client.get_roulette_spins()
                if analisys_result == False:
                    for sequence in sequences:
                        spins = roulette_spins[:int(sequence['amt_spins'])]
                        current_spin_sequence = ""
                        for spin in spins:
                            current_spin_sequence += str(spin['color'])
                        red_amt = current_spin_sequence.count('1')
                        black_amt = current_spin_sequence.count('2')
                        last_sq_color = int(roulette_spins[int(sequence['amt_spins'])]['color'])
                        print(f"Sequencia atual da roleta: {current_spin_sequence}")
                        print(f"Ultimo numero da sequencia: {last_sq_color}")
                        print(f"Sequencia esperada Vermelhos: {sequence['red_amount']} Pretos: {sequence['black_amount']}")
                        print(f"Sequencia atual Vermelhos: {red_amt} Pretos: {black_amt}")
                        print("-------------------------------")
                        if last_sq_color == 0 and red_amt == int(sequence['red_amount']) and black_amt == int(sequence['black_amount']):
                            print(f"Sequencia encontrada de {sequence['amt_spins']} encontrada!")
                            print(f"Enviando sinal...")
                            telegram_signal = "🔴" if sequence['win_signal'] == 1 else "⚫️"
                            blaze_signal = 1 if sequence['win_signal'] == 1 else 2
                            await telegram_client.send_message(selected_group, f"Entrada confirmada!\nEntrar no: {telegram_signal} + ⚪️")
                            channel_msgs = await telegram_client.get_channel_messages(selected_group)
                            signal_msg_id = channel_msgs[-1].id
                            analisys_result = True
                            break
                    if analisys_result == True:
                        await asyncio.sleep(17)
                if analisys_result == True:
                    for i in range(gales):
                        if i < 1:
                            print("Pegando o resultado...")
                        else:
                            print(f"Pegando o resultado gale {i}...")
                        result = blaze_client.get_roulette_spins()[0]
                        if result['color'] == 0:
                            print("Win branco !")
                            await telegram_client.reply_channel_message(selected_group, signal_msg_id, f"Win !! ⚪️")
                            analisys_result = False
                            telegram_signal = None
                            blaze_signal = None
                            break
                        if result['color'] == blaze_signal:
                            print("Win !")
                            await telegram_client.reply_channel_message(selected_group, signal_msg_id, f"Win !!")
                            analisys_result = False
                            telegram_signal = None
                            blaze_signal = None
                            break
                        else:
                            print("Loss !")
                            await telegram_client.reply_channel_message(selected_group, signal_msg_id, f"Loss !!")
                            telegram_signal = None
                            blaze_signal = None
                            await asyncio.sleep(17)
                    analisys_result = False
                elif analisys_result == False:
                    print("Nenhuma sequencia encontrada...")
                    await asyncio.sleep(17)
            else:
                print("Roleta Bloqueada, aguardando liberação...")
        except KeyboardInterrupt:
            print("Saindo...")
            await telegram_client.send_message(selected_group, "Saindo...")
            exit(1)

def main():
    print("Bem Vindo ao Bot de sinais para Blaze[Double]")
    selected_option = input("Qual função deseja executar?\n1 - Adicionar Sequencia\n2 - Executar Bot\n3 - Sair\n")
    if selected_option == "1":
        add_sequences_handler()
        clear()
        main()
    elif selected_option == "2":
        telegram_number = input("Digite o numero de telefone para o login: ")
        telegram_client = TelegramBot(telegram_number)
        blaze_client = BlazeBot()
        print("Authenticado com sucesso!")
        sequences = load_sequences_handler()
        gales = int(input("Qauntos gales: "))
        if gales < 1:
            gales = 1 
        current_loop.run_until_complete(run_bot(telegram_client, blaze_client, sequences, gales))
    elif selected_option == "3":
        print("Saindo...")
        exit(1)
    else:
        print("Opção inválida!")
        clear()
        main()
if __name__ == "__main__":
    main()