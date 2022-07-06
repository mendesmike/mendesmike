import requests
import json
from requests.adapters import HTTPAdapter, Retry

class BlazeBot:

    def __init__(self):
        self.__url_roullete_state = "https://blaze.com/api/roulette_games/current"
        self.__url_roullete_historic = "https://blaze.com/api/roulette_games/recent"
        self.__url_bet_info = "https://blaze.com/api/roulette_games/"
        self.__headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'origin': 'https://blaze.com',
            'referer': 'https://blaze.com/pt/games/double',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'x-client-language': 'pt',
            'x-client-version': 'c9d9c023'
        }

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
        return self.make_request(self.__url_bet_info + bet_id, headers=self.__headers)
    
    def get_roulette_spins(self):
        custom_header = self.__headers
        custom_header['upgrade-insecure-requests'] = '1'
        try:
            custom_header.pop('x-client-language')
            custom_header.pop('x-client-version')
        except KeyError:
            pass
        return self.make_request(self.__url_roullete_historic, headers=custom_header)

    def get_roullete_data(self):
        return self.make_request(self.__url_roullete_state, headers=self.__headers)












