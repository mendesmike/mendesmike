import asyncio
import time
import sys

from datetime import datetime
from os.path import exists

from modules.utils import load_points, load_sched, make_request, load_sequences, save_points, save_sequences, clear_terminal, group_menu, schedule_points
from modules.blaze_toolkit import BlazeBot
from modules.telegram_toolkit import build_client, delete_channel_messages, edit_channel_message, get_groups, reply_channel_message, send_message, get_channel_messages

selected_group = None
msg_id = None
current_loop = asyncio.get_event_loop()

bot_wins = 0
bot_loss = 0
bot_win_gale = 0

def analise_sequences(blaze, telegram, sequences):
    balze_spins = blaze.get_roulette_spins()
    print("Iniciando Análise")
    print(f"Giros carregados: {len(balze_spins)}")
    print("Analisando giros...")
    i = 0
    for sequence in sequences:
        i += 1

        spins = balze_spins[:int(sequence['amt_spins'])]

        current_spin_sequence = ""
        for spin in spins:
            current_spin_sequence += str(spin['color'])

        red_amt = int(current_spin_sequence.count('1'))
        black_amt = int(current_spin_sequence.count('2'))
        last_sq_color = int(balze_spins[int(sequence['amt_spins'])]['color'])
        formated_current_spin_sequence = current_spin_sequence.replace('1', '🔴').replace('2', '⚫️').replace('0', '⚪️')
        formated_last_sq_color = str(last_sq_color).replace('1', '🔴').replace('2', '⚫️').replace('0', '⚪️')
        print(f"Analisando sequência {i} de {len(current_spin_sequence)} giros")
        print(f"Ultima cor da sequencia: {formated_last_sq_color}")
        print(f"Sequencia atual da roleta: {formated_current_spin_sequence}")
        print(f"Sequencia esperada: 🔴[{sequence['red_amount']}] ⚫️[{sequence['black_amount']}]")
        print(f"Sequencia atual: 🔴[{red_amt}] ⚫️[{black_amt}]")
        print("")

        if last_sq_color == 0 and red_amt == int(sequence['red_amount']) and black_amt == int(sequence['black_amount']):
            print("Sequencia encontrada!")
            sequence_found = sequence
            break
        else:
            print("Sequencia não encontrada!")
            sequence_found = False
            
    return sequence_found

def fazer_aposta(blaze, telegram, signal):
    print("Iniciando aposta...")
    signal_color = str(signal).replace('1', '🔴').replace('2', '⚫️').replace('0', '⚪️')
    print("Sinal escolhido: " + signal_color)
    bet_id = blaze.get_roullete_data()['id']
    print(f"Id da aposta: {bet_id}")
    while True:
        time.sleep(1)
        roullete_data = blaze.get_roullete_data()
        if roullete_data['status'] == 'complete':
            print("Aposta concluida!")
            print("Checando resultado...")
            time.sleep(4)
            #result = int(blaze.get_bet_result(bet_id)['color'])
            result = int(blaze.get_roulette_spins()[0]['color'])
            if result == int(signal):
                print("Win !")
                op = True
                break
            elif result == 0:
                print("Win Branco !")
                op = True
                break
            else:
                print("Lose !")
                op = False
                break
    return op

def core_loop(blaze, telegram):
    global current_loop
    global selected_group
    global msg_id
    global bot_wins
    global bot_loss
    global bot_win_gale

    print("Iniciando operações...")
    sequences = load_sequences()[0]
    if exists('points.txt'):
        points = load_points()[0]
        if len(points) > 0:
            bot_wins = points['wins']
            bot_loss = points['loses']
            bot_win_gale = points['gales']
    else:
        save_points(bot_wins, bot_loss, bot_win_gale)
    scheds = load_sched()[0]
    print(f"Sequências carregadas: {len(sequences)}")
    print(f"Agendamentos carregadas: {len(scheds)}")
    while True:
        time.sleep(1)
        roullete_data = blaze.get_roullete_data()
        if roullete_data['status'] == 'waiting':
            print("Roleta liberada !")
            catalogation = analise_sequences(blaze, telegram, sequences)

            if catalogation:
                signal_color = str(catalogation['win_signal']).replace('1', '🔴').replace('2', '⚫️').replace('0', '⚪️')
                current_loop.run_until_complete(send_message(telegram, selected_group, f"<b>✅Entrada confirmada ✅</b>\n<b>🎲Apostar em {signal_color}</b>\n<b>🎰PROTEGE no branco ⚪</b>\n<b>🚀 https://blaze.com/r/VAdwV</b>\n<b>⚠️⚠️1 MARTINGALE⚠️⚠️</b>"))
                channel_msgs = current_loop.run_until_complete(get_channel_messages(telegram, selected_group))
                msg_id = channel_msgs[-1].id
                result = fazer_aposta(blaze, telegram, catalogation['win_signal'])

                if result == False:
                    print("Entrando no gale...")
                    current_loop.run_until_complete(reply_channel_message(telegram, selected_group, msg_id, "Vamo para o gale !"))
                    channel_msgs = current_loop.run_until_complete(get_channel_messages(telegram, selected_group))
                    gale_msg_id = channel_msgs[-1].id
                    gale_result = fazer_aposta(blaze, telegram, catalogation['win_signal'])
                    if gale_result == True:
                        print("Gale concluido!")
                        bot_win_gale += 1
                        current_loop.run_until_complete(delete_channel_messages(telegram, selected_group, gale_msg_id))
                        current_loop.run_until_complete(reply_channel_message(telegram, selected_group, msg_id, "✅ Win Gale 🎉"))
                    else:
                        bot_loss += 1
                        print("Gale concluido!")
                        current_loop.run_until_complete(delete_channel_messages(telegram, selected_group, gale_msg_id))
                        current_loop.run_until_complete(reply_channel_message(telegram, selected_group, msg_id, "🅾️ Loss "))
                else:
                    bot_wins += 1
                    current_loop.run_until_complete(reply_channel_message(telegram, selected_group, msg_id, "✅ Win 🎉"))
                
                save_points(bot_wins, bot_loss, bot_win_gale)
            
            for sch in scheds:
                if datetime.now().strftime("%H:%M") == sch.strftime("%H:%M"):
                    print("Mostrando placar...")
                    current_loop.run_until_complete(send_message(telegram, selected_group, f"✅ Wins: {bot_wins}\n🅾️ Losses: {bot_loss}\n✅ Win Gale: {bot_win_gale}"))
            
            time.sleep(16)

def main():
    global selected_group
    global msg_id
    global current_loop

    print("Ben-vindo ao bot de sinais da Blaze[Double]")
    print("Selecione uma opção:")
    print("[1] - Adicionar sequencias")
    print("[2] - Inicializar bot")
    print("[3] - Agendar Placar")
    print("[4] - Sair")

    option = input("Opção: ")

    if option == "1":
        save_sequences()
        clear_terminal()
        main()
    elif option == "2":
        clear_terminal()
        telegram_number = input("Digite o número do telegram: ")
        print("Inicializando bot...")
        blaze_cli = BlazeBot()
        telegram_cli = build_client(telegram_number)
        groups = current_loop.run_until_complete(get_groups(telegram_cli))
        selected_group = group_menu(groups)
        core_loop(blaze_cli, telegram_cli)
    elif option == "3":
        clear_terminal()
        schedule_points()
        main()
    elif option == "4":
        print("Saindo...")
        sys.exit(0)


if __name__ == "__main__":
    main()































