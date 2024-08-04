import time
import requests
import hmac
from hashlib import sha256
import CONFIG
from datetime import datetime
import pandas as pd
import json

class Binance:
    def __init__(self, api_key, secret_key):
        self._api_key = api_key
        self._secret_key = secret_key
        self._api_url = CONFIG.BINANCE['MAIN_URL']
        
    def get_sign(self, payload):
        signature = hmac.new(self._secret_key.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
        return signature
    
    def parse_params(self, params_map):
        sorted_keys = sorted(params_map)
        params_str = "&".join(["%s=%s" % (x, params_map[x]) for x in sorted_keys])
        return params_str
    
    def send_request(self, method, path, params_str, payload):
        url = "%s%s?%s&signature=%s" % (self._api_url, path, params_str, self.get_sign(params_str))
        headers = {
            'X-MBX-APIKEY': self._api_key,
        }
        response = requests.request(method, url, headers=headers, data=payload)
        return response.json()

    def get_historical_spot_price(self, symbol, interval, start_time=None, end_time=None, limit=1000):
        path = '/api/v3/klines'
        method = 'GET'
        all_data = []
        
        if start_time:
            start_time_ms = int(datetime.strptime(start_time, '%d %b %Y').timestamp() * 1000)
        else:
            start_time_ms = None
            
        if end_time:
            end_time_ms = int(datetime.strptime(end_time, '%d %b %Y').timestamp() * 1000)
        else:
            end_time_ms = None
        
        while True:
            params_map = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            if start_time_ms:
                params_map['startTime'] = start_time_ms
            if end_time_ms:
                params_map['endTime'] = end_time_ms
            
            params_str = self.parse_params(params_map)
            url = "%s%s?%s" % (self._api_url, path, params_str)
            response = requests.request(method, url)
            json_data = response.json()
            
            if not json_data:
                break
            
            all_data.extend(json_data)
            
            start_time_ms = json_data[-1][0] + 1
            
            if end_time_ms and start_time_ms >= end_time_ms:
                break
            
            if len(json_data) < limit:
                break
        
        df = pd.DataFrame(all_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        
        return df
    
api_key = 'your_api_key'
secret_key = 'your_secret_key'
binance = Binance(secret_key)

historical_spot_price = binance.get_historical_spot_price('ONTUSDT', '1h', start_time='1 Jan 2022')
print(historical_spot_price)