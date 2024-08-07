# -*- coding: utf-8 -*-

#%%
import time
import requests
import hmac
from hashlib import sha256
import CONFIG

class HTX:
    def __init__(self, api_key, secret_key):
        self._api_key = api_key
        self._secret_key = secret_key
        self._api_url = CONFIG.HTX['MAIN_URL']
        
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
    
    def get_funding_rate(self, symbol):
        payload = {}
        path = '/linear-swap-api/v1/swap_funding_rate'
        method = "GET"
        paramsMap = {
        "contract_code": symbol + "-USDT"
        }
        paramsStr = self.praseParam(paramsMap)
        return self.send_request(method, path, paramsStr, payload)

    def get_funding_rate_history(self, symbol):
        payload = {}
        path = '/linear-swap-api/v1/swap_historical_funding_rate'
        method = "GET"
        paramsMap = {
        "contract_code": symbol + "-USDT",
        "page_index": 1,
        "page_size": 20
        }
        paramsStr = self.praseParam(paramsMap)  
        return self.send_request(method, path, paramsStr, payload)

    def get_account(self):
        payload = {}
        path = '/linear-swap-api/v1/swap_balance_valuation'
        method = "POST"
        paramsMap = {
        "valuation_asset": "USDT"
        }
        paramsStr = self.praseParam(paramsMap)
        return self.send_request(method, path, paramsStr, payload)
