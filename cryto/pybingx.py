#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
import time
import requests
import hmac
from hashlib import sha256
import CONFIG

class BingX:
    def __init__(self, api_key, secret_key):
        self._api_key = api_key
        self._secret_key = secret_key
        self._api_url = CONFIG.BINGX['MAIN_URL']
        
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

    def get_funding_rate_history(self, symbol):
        payload = {}
        path = '/openApi/swap/v2/quote/fundingRate'
        method = "GET"
        paramsMap = {
        "symbol": symbol + "-USDT",
        "startTime": 0,
        "endTime": 0,
        "limit": 0
        }
        paramsStr = self.praseParam(paramsMap)
        return self.send_request(method, path, paramsStr, payload)
