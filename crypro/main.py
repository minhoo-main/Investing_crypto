#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pybingx
import pyhtx
import CONFIG
#import yfinance as yf

bingx = pybingx.BingX(CONFIG.BINGX['API_KEY'], CONFIG.BINGX['SECRET_KEY'])
#upbit = pyupbit.Upbit(CONFIG.UPBIT['API_KEY'], CONFIG.UPBIT['SECRET_KEY'])

bingx.get_account()

#pyupbit.get_current_price("KRW-ATOM")
#upbit.get_balance("KRW")


data = bingx.get_funding_rate_history("ONT")
#data = yf.download('USDKRW=X')

#%%
import pandas as pd
ont = bingx.get_price_history('ONT')
ong = bingx.get_price_history('ONG')

df_ont = pd.DataFrame(ont['data'],dtype=float)
df_ong = pd.DataFrame(ong['data'],dtype=float)

merged_df = pd.merge(df_ont, df_ong, on='time')

merged_df['ratio'] = merged_df['close_x'] / merged_df['close_y']

merged_df = merged_df.dropna()
#%%
import datetime


def convert_timestamp(ts):
    return datetime.datetime.fromtimestamp(ts / 1000)

merged_df['date'] = merged_df['time'].apply(convert_timestamp)

merged_df.set_index('date', inplace=True)

merged_df.drop(columns=['time'], inplace=True)
#%%
import matplotlib.pyplot as plt
plt.plot(merged_df[['close_x','close_y','ratio']])
#%%
from binance.client import Client
import pandas as pd

client = Client(CONFIG.BINANCE['API_KEY'], CONFIG.BINANCE['SECRET_KEY'])

def get_historical_spot_data(symbol, interval, start_str, end_str):
    """
    바이낸스에서 과거 현물 데이터를 가져오는 함수

    Parameters:
    symbol (str): 거래 쌍 (예: 'BTCUSDT')
    interval (str): 데이터 간격 (예: '1d', '1h', '1m')
    start_str (str): 시작 날짜 (예: '1 Jan 2021')
    end_str (str): 종료 날짜 (예: '1 Jan 2022')

    Returns:
    pd.DataFrame: 과거 현물 데이터 프레임
    """

    klines = client.get_historical_klines(symbol, interval, start_str, end_str)
    
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    
    df['open'] = pd.to_numeric(df['open'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['close'] = pd.to_numeric(df['close'])
    df['volume'] = pd.to_numeric(df['volume'])
    
    return df
#%%
# 함수 사용 예제
symbol = 'ONTUSDT'
interval = '4h'
start_str = '1 Jan 2018'
end_str = '27 Jul 2024'

df_ont = get_historical_spot_data('ONTUSDT', interval, start_str, end_str)
df_ong = get_historical_spot_data('ONGUSDT', interval, start_str, end_str)

#%%
merged_df = pd.merge(df_ont, df_ong, on='timestamp')

merged_df['ratio'] = merged_df['close_y'] / merged_df['close_x']

merged_df = merged_df.dropna()

merged_df.set_index('timestamp', inplace=True)

plt.plot(merged_df['close_x'], label='ont')
plt.plot(merged_df['close_y'], label='ong')
plt.plot(merged_df['ratio'], label='ong/ont')
plt.legend()
plt.show()

