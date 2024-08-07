#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import requests
import hmac
from hashlib import sha256
from . import CONFIG
import pandas as pd
from datetime import datetime

class BingX:
    def __init__(self, api_key, secret_key, url):
        self._api_key = api_key
        self._secret_key = secret_key
        self._api_url = url
        
    def get_sign(self,payload):
        signature = hmac.new(self._secret_key.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
        return signature
    
    def praseParam(self, paramsMap):
        sortedKeys = sorted(paramsMap)
        paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
        return paramsStr+"&timestamp="+str(int(time.time() * 1000))
    
    def send_request(self, method, path, urlpa, payload):
        url = "%s%s?%s&signature=%s" % (self._api_url, path, urlpa, self.get_sign(urlpa))
        headers = {
            'X-BX-APIKEY': self._api_key,
        }
        response = requests.request(method, url, headers=headers, data=payload)
        return response.json()
    
    def get_position(self, symbol):
        payload = {}
        path = '/openApi/swap/v2/user/positions'
        method = "GET"
        paramsMap = {
        "symbol": symbol + "-USDT",
        "recvWindow": 0
        
        }
        paramsStr = self.praseParam(paramsMap)
        return self.send_request(method, path, paramsStr, payload)

    def get_account(self):
        payload = {}
        path = '/openApi/swap/v2/user/balance'
        method = "GET"
        paramsMap = {
        "recvWindow": 0
        }
        paramsStr = self.praseParam(paramsMap)
        return self.send_request(method, path, paramsStr, payload)

    def get_price(self, symbol):
        payload = {}
        path = '/openApi/swap/v2/quote/price'
        method = "GET"
        paramsMap = {
        "symbol": symbol.upper() + "-USDT"
        }
        paramsStr = self.praseParam(paramsMap)
        return self.send_request(method, path, paramsStr, payload)
    
    def get_price_history(self, symbol):
        payload = {}
        path = '/openApi/swap/v3/quote/klines'
        method = "GET"
        paramsMap = {
        "symbol": symbol.upper() + "-USDT",
        "interval": "4h",
        "startTime": 0,
        "endTime": 0,
        "limit": 1440
        }
        paramsStr = self.praseParam(paramsMap)
        return self.send_request(method, path, paramsStr, payload)
    
    def get_funding_rate(self, symbol):
        payload = {}
        path = '/openApi/swap/v2/quote/premiumIndex'
        method = "GET"
        paramsMap = {
        "symbol": symbol + "-USDT"
        }
        paramsStr = self.praseParam(paramsMap)
        return self.send_request(method, path, paramsStr, payload)

    def get_funding_rate_history(self, symbol, start_time=None, end_time=None, limit=1000):
        path = '/openApi/swap/v2/quote/fundingRate'
        method = "GET"
        
        # Convert start_time and end_time to milliseconds since epoch if provided
        start_time_ms = int(datetime.strptime(start_time, '%d %b %Y').timestamp() * 1000) if start_time else 0
        end_time_ms = int(datetime.strptime(end_time, '%d %b %Y').timestamp() * 1000) if end_time else int(time.time() * 1000)
        
        all_data = []
        current_start_time_ms = start_time_ms
        
        while True:
            paramsMap = {
                "symbol": symbol + "-USDT",
                "startTime": current_start_time_ms,
                "endTime": end_time_ms,
                "limit": limit
            }
            paramsStr = self.praseParam(paramsMap)
            data = self.send_request(method, path, paramsStr, payload={})
            
            if not data['data']:
                break

            all_data.extend(data['data'])

            end_time_ms = data['data'][0]['fundingTime'] -1

            if len(data['data']) < limit:
                break
        
        df = pd.DataFrame(all_data)
        if not df.empty:
            df['fundingTime'] = pd.to_datetime(df['fundingTime'], unit='ms')
            df['fundingRate'] = df['fundingRate'].astype(float)
            df['markPrice'] = df['markPrice'].astype(float)
        
        df_sorted = df.sort_values(by='fundingTime')
        return df_sorted