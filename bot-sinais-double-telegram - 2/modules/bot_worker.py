import asyncio
import threading
import time

class Bot_Worker():

    def __init__(self, bot_setup):
        #threading.Thread.__init__(self)
        self.bot_setup = bot_setup
        self.telegram_client = self.bot_setup['telegram_client']
        self.blaze_client = self.bot_setup['blaze_client']
        self.sequences = self.bot_setup['sequences']
        self.gales = self.bot_setup['gales_amount']
        self.selected_group = self.bot_setup['selected_group']
        self.in_analisys = False
        self.current_soros_level = 0
        self.bot_wins = 0
        self.bot_loses = 0
        self.bot_gales_wins = 0
        self.signal_msg_id = None
        self.bet_id = None

    async def make_operations(self, signal):
        self.bet_id = self.blaze_client.get_roullete_data()['id']
        print("Fazendo aposta")
        print(f"Id da aposta: {self.bet_id}")
        while True:
            await asyncio.sleep(1)
            roulette_data = self.blaze_client.get_roullete_data()
            if roulette_data['status'] == 'complete':
                print("Checando resultado da aposta...")
                await asyncio.sleep(3)
                result_bet = self.blaze_client.get_bet_result(self.bet_id)
                result_bet_number = int(result_bet['color'])
                result_bet_color = str(result_bet['color']).replace('1', '🔴').replace('2', '⚫️').replace('0', '⚪️')
                print(f"Resultado da aposta: {result_bet_color}")
                if result_bet_color == int(signal):
                    print("Aposta venceu!")
                    op =  True
                    break
                elif result_bet_color == 0:
                    print("Aposta venceu!")
                    op = True
                    break
                else:
                    print("Aposta perdeu!")
                    op = False
                    break
        return op

    async def run_work(self):
        print("Iniciando trabalho...")
        while True:
            roullete_data = self.blaze_client.get_roullete_data()
            if roullete_data['status'] == 'waiting':
                print("Roleta livre !")
                if self.in_analisys == False:
                    print("Analisando OFF")
                    print("Iniciando análise...")
                    roullete_spins = self.blaze_client.get_roulette_spins()
                    for sequence in self.sequences:
                        spins = roullete_spins[:int(sequence['amt_spins'])]
                        current_spin_sequence = ""
                        for spin in spins:
                            current_spin_sequence += str(spin['color'])
                        
                        red_amt = current_spin_sequence.count('1')
                        black_amt = current_spin_sequence.count('2')
                        last_sq_color = int(roullete_spins[int(sequence['amt_spins'])]['color'])

                        formated_current_spin_sequence = current_spin_sequence.replace('1', '🔴').replace('2', '⚫️').replace('0', '⚪️')
                        formated_last_sq_color = str(last_sq_color).replace('1', '🔴').replace('2', '⚫️').replace('0', '⚪️')

                        print("-------------------------------")
                        print(f"Sequencia atual da roleta: {formated_current_spin_sequence}")
                        print(f"Ultimo numero da sequencia: {formated_last_sq_color}")
                        print(f"Sequencia esperada: 🔴[{sequence['red_amount']}] ⚫️[{sequence['black_amount']}]")
                        print(f"Sequencia atual: 🔴[{red_amt}] ⚫️[{black_amt}]")
                        print("-------------------------------")

                        if red_amt == int(sequence['red_amount']) and black_amt == int(sequence['black_amount']):
                            if int(sequence['win_signal']) == 1:
                                print("Sinal de vitoria: 🔴")
                                telegram_signal = '🔴'
                                signal = 1
                            elif int(sequence['win_signal']) == 2:
                                print("Sinal de vitoria: ⚫️")
                                telegram_signal = '⚫️'
                                signal = 2

                            print("Sequencia encontrada!")
                            
                            op_result = await self.make_operations(signal)
                            if op_result == True:
                                self.bot_wins += 1
                            else:
                                print("Gale Ativado")
                                for i in range(self.gales):
                                    op_result_gale = await self.make_operations(signal)
                                    if op_result_gale == True:
                                        self.bot_gales_wins += 1
                                        print(f"Win Gale {i}")
                                        break
                                    else:
                                        self.bot_loses += 1
                                        print(f"Loss Gale {i}")

                                print("Gale Finalizado")
                                print("")
                                
                    
                    print("Sequencias não encontradas.")
                    print("Aguardando proximo giro...")
                    print("")
                    await asyncio.sleep(18)