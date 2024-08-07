from crypto import pybinance
from datetime import datetime
import pandas as pd

#client = Client(CONFIG.BINANCE['API_KEY'], CONFIG.BINANCE['SECRET_KEY'])
#단순 시세 조회 용도.
client = pybinance.Binance('AA', 'BB')

symbol = 'ONTUSDT'
interval = '4h'
start_str = '1 Jan 2024'
now = datetime.now()
end_str = now.strftime('%d %b %Y')

df_ont = client.get_historical_spot_price('ONTUSDT', interval, start_str, end_str)
print(df_ont)