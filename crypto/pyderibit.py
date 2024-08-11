import requests
import datetime
import pandas as pd

class Deribit:

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

    def generate_fridays(self, start_date_str, end_date_str=None):
        if end_date_str == None:
            now = datetime.datetime.now()
            end_date_str = now.strftime('%Y-%m-%d')
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
        
        if start_date.weekday() != 4: 
            days_to_friday = 4 - start_date.weekday() if start_date.weekday() < 4 else 7 - (start_date.weekday() - 4)
            start_date += datetime.timedelta(days=days_to_friday)
        
        ls_mty = []
        
        while True:
            formatted_date = start_date.strftime('%d%b%y').upper()
            ls_mty.append(formatted_date)
            
            start_date += datetime.timedelta(weeks=1)
            
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
            if start_date > end_date:
                break

        return ls_mty
    
    def get_instruments_all_list(self, currency, str_from):
        dict_fut = {}
        ls_old_mty = self.generate_fridays(str_from)
        for str_mty in ls_old_mty:
            fut = self.get_instrument(currency+'-'+str_mty)
            if len(fut) != 0 :
                dict_fut[currency+'-'+str_mty] = fut
        
        ls_live_mty = self.get_instruments(currency)
        for dict_mty in ls_live_mty:
            dict_fut[dict_mty['instrument_name']] = dict_mty
        
        return dict_fut