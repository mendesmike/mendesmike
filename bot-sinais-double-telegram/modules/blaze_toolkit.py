import requests
import aiohttp
import json
from requests.adapters import HTTPAdapter, Retry



class BlazeBot:

    def __init__(self):
        self.url_roullete_state = "https://blaze.com/api/roulette_games/current"
        self.url_roullete_historic = "https://blaze.com/api/roulette_games/recent"
        self.url_bet_info = "https://blaze.com/api/roulette_games/"
        self.current_bet_id = None
        self.initial_analyse = False
        self.confirm_analyse = False
        self.win_analyse = False
        self.current_sequence = None

    def make_request(self, url, headers, post = None, req_type = "GET"):
        session = requests.Session()
        retry = Retry(
            total=5,
            read=5,
            connect=5,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
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
    
    def get_bet_result(self, bet_id):
        try:

            url = self.url_bet_info + str(bet_id) + "?page=1"
        
            headers = {
                'accept': 'application/json, text/plain, */*',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                'origin': 'https://blaze.com',
                'referer': 'https://blaze.com/pt/games/double?modal=double_history&id='+ str(bet_id),
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
                'x-client-language': 'pt',
                'x-client-version': 'c9d9c023'
            }
            response = self.make_request(url, headers)

            if 'error' not in response.text:
                return response.json()['color']
            else:
                print(f"Error on get bet result: {response.json()['error']['message']}")
        except Exception as e:
            print(f"Error on get bet result, unknow")

    def get_roulette_spins(self):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'
        }
        
        response = self.make_request(self.url_roullete_historic, headers)
        return response

    def get_roullete_data(self):
        headers = {
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json;charset=UTF-8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'origin': 'https://blaze.com',
            'referer': 'https://blaze.com/pt/games/double',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'x-client-language': 'pt',
            'x-client-version': 'c9d9c023'
        }
        
        try:
            req = self.make_request(self.url_roullete_state, headers=headers)
            return req
        except Exception as e:
            print(f"Erro to get roullete status, unknow")

    def get_roullete_bet_id(self):
        try:
            headers = {
                'accept': 'application/json, text/plain, */*',
                'content-type': 'application/json;charset=UTF-8',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                'origin': 'https://blaze.com',
                'referer': 'https://blaze.com/pt/games/double',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
                'x-client-language': 'pt',
                'x-client-version': 'c9d9c023'
            }
            
            req = requests.get(self.url_roullete_state, headers=headers)
            return req['id']
        except Exception as e:
            print("Erro on get roullet bet id, unknow")

    def analyze_sequences(self, spins_data, sequences):
        for sequence in sequences:
            print(f"Analizando sequencia: {sequence['win_result']}")
            current_sequence_analyse = sequence['start']
            current_sequence_roullete = ""
            for spin in spins_data[:len(sequence['start'])]:
                current_sequence_roullete += str(spin['color'])

            if current_sequence_analyse == current_sequence_roullete:
                self.current_sequence = sequence
                self.initial_analyse = True
                print(f"Sequence Analisys {current_sequence_analyse} X {current_sequence_roullete} found")
                current_sequence_roullete = ""
                return True
            else:
                print(f"Sequence Analisys {current_sequence_analyse} X {current_sequence_roullete} not found")
            current_sequence_roullete = ""
        return False

    def confirm_sequences(self, spins_data):
        current_seq = ""
        for spin in spins_data[:len(self.current_sequence['end'])]:
            current_seq += str(spin['color'])
            
        if current_seq == self.current_sequence['end']:
            self.confirm_analyse = True
            self.initial_analyse = False
            print(f"Sequence Confirmation {self.current_sequence['end']} X {current_seq} found")
            return self.current_sequence['end'][-1]
        else:
            self.initial_analyse = False
            self.confirm_analyse = False
            print(f"Sequence Confirmation {self.current_sequence['end']} X {current_seq} not found")
            return False

    def win_sequences(self, spins_data):
        current_seq = ""
        for spin in spins_data[:len(self.current_sequence['win_result'])]:
            current_seq += str(spin['color'])
        if current_seq == self.current_sequence['win_result']:
            self.win_analyse = True 
            self.confirm_analyse = False
            self.initial_analyse = False 
            print(f"Sequence Win {self.current_sequence['win_result']} X {current_seq} found")
            current_seq = ""
            return True
        elif current_seq[0] == 0:
            self.win_analyse = True 
            self.confirm_analyse = False
            self.initial_analyse = False 
            print(f"Sequence Win {self.current_sequence['win_result']} X {current_seq} found")
            current_seq = ""
            return 0
        else:
            self.win_analyse = False 
            self.confirm_analyse = False
            self.initial_analyse = False
            print(f"Sequence Win {self.current_sequence['win_result']} X {current_seq} not found")
            current_seq = ""
            return False

    def custom_analisys_sequence(self, spins_data):
        if spins_data[3]['color'] == 0 and spins_data[2]['color'] != 0 and spins_data[1]['color'] != 0 and spins_data[0]['color'] != 0:
            print("Custom Analisys Sequence found")
            self.initial_analyse = True
            return True
        else:
            self.initial_analyse = False
            print("Custom Analisys Sequence not found")
            return False

    def custom_confirm_sequence(self, spins_data):
        current_sequence = ""
        if spins_data[4]['color'] == 0 and spins_data[3]['color'] != 0 and spins_data[2]['color'] != 0 and spins_data[1]['color'] != 0 and spins_data[0]['color'] != 0:
            for spin in spins_data[:4]:
                current_sequence += str(spin['color'])
            count_reds = current_sequence.count("1")
            count_blacks = current_sequence.count("2")
            if count_reds < count_blacks:
                print("Custom Confirm Sequence found")
                self.confirm_analyse = True
                self.initial_analyse = False
                return 1
            elif count_blacks < count_reds:
                print("Custom Confirm Sequence found")
                self.confirm_analyse = True
                self.initial_analyse = False
                return 2
            else:
                self.confirm_analyse = False
                self.initial_analyse = False
                return False
        else:
            self.confirm_analyse = False
            self.initial_analyse = False
            print("Custom Confirm Sequence not found")
            return False
    
    def custom_win_sequence(self, spins_data, signal_win):
        if spins_data[0]['color'] == signal_win:
            self.confirm_analyse = False
            self.win_analyse = True
            print("Custom Win Sequence found")
            return True
        elif spins_data[0]['color'] == 0:
            self.confirm_analyse = False
            self.win_analyse = True
            print("Custom Win WHITE Sequence found")
            return 0
        else:
            self.confirm_analyse = False
            self.win_analyse = False
            print("Custom Win Sequence not found")
            return False












