import requests
import datetime
import pandas as pd

class Deribit:
    BASE_URL = "https://www.deribit.com/api/v2/public"

    def __init__(self, url):
        self.BASE_URL = url

    def get_historical_futures_price(self, symbol, start_time, end_time, resolution='1D'):
        """
        :param resolution: 데이터 간격 ('1', '3', '5', '10', '15', '30', '60', '120', '180', '240', 'D', 'W', 'M')
                           '1': 1분, '3': 3분, '5': 5분, '10': 10분, '15': 15분, '30': 30분, '60': 1시간,
                           '120': 2시간, '180': 3시간, '240': 4시간, 'D': 1일, 'W': 1주, 'M': 1개월
        """
        all_data = {
            "ticks": [],
            "open": [],
            "high": [],
            "low": [],
            "close": [],
            "volume": [],
            "cost": []
        }

        while start_time < end_time:
            url = f"{self.BASE_URL}/get_tradingview_chart_data"
            params = {
                'instrument_name': symbol,
                'start_timestamp': int(start_time.timestamp() * 1000),
                'end_timestamp': int(end_time.timestamp() * 1000),
                'resolution': resolution
            }
            response = requests.get(url, params=params)
            data = response.json().get('result', {})

            if data['status'] == 'no_data':
                break
            
            for item in all_data:
                all_data[item] = data[item] + all_data[item]

            last_timestamp = data['ticks'][0] / 1000.0
            end_time = datetime.datetime.fromtimestamp(last_timestamp) + datetime.timedelta(milliseconds=-1)

        df = pd.DataFrame(all_data)
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['ticks'], unit='ms')
            df.set_index('timestamp', inplace=True)
        
        return df


    def get_historical_funding_rate(self, symbol, start_time, end_time):
        all_data = []

        while start_time < end_time:
            url = f"{self.BASE_URL}/get_funding_rate_history"
            params = {
                'instrument_name': symbol,
                'start_timestamp': int(start_time.timestamp() * 1000),
                'end_timestamp': int(end_time.timestamp() * 1000)
            }
            response = requests.get(url, params=params)
            data = response.json().get('result', {})

            if not data:
                break

            all_data = data + all_data

            last_timestamp = data[0]['timestamp'] / 1000.0
            end_time = datetime.datetime.fromtimestamp(last_timestamp) + datetime.timedelta(milliseconds=-1)

        df = pd.DataFrame(all_data)
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
        
        return df

    def get_instrument(self, instrument_name):
        url = f"{self.BASE_URL}/get_instrument"
        params = {'instrument_name': instrument_name}
        response = requests.get(url, params=params)
        return response.json().get('result', [])

    def get_instruments(self, currency):
        url = f"{self.BASE_URL}/get_instruments"
        params = {'currency': currency, 'kind': 'future'}
        response = requests.get(url, params=params)
        return response.json().get('result', [])
