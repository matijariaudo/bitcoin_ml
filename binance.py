import requests
import pandas as pd

def get_binance_input_row(symbol="BTCUSDT", interval="15m", limit=30):
    """
    Descarga los últimos `limit` valores de velas de Binance y los convierte en una sola fila.
    """
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    # Columnas completas según Binance
    columns = ['open_time', 'open', 'high', 'low', 'close', 'volume',
               'close_time', 'quote_asset_volume', 'number_of_trades',
               'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore']
    #Creo el DF
    df = pd.DataFrame(data, columns=columns).astype(float)
    df.drop(columns=['ignore'], inplace=True)
    
    #Agrego columnas de fecha y hora
    df['day'] = pd.to_datetime(df['open_time']).dt.day
    df['month'] = pd.to_datetime(df['open_time']).dt.month
    df['day_of_week'] = pd.to_datetime(df['open_time']).dt.dayofweek
    df['hour'] = pd.to_datetime(df['open_time']).dt.hour
    df['minute'] = pd.to_datetime(df['open_time']).dt.minute

    # Convertir las últimas 30 filas en una sola fila
    row = {}
    for i in range(limit):
        for col in df.columns:
            row[f"{col}_{i}"] = df.iloc[limit - 1 - i][col]

    return pd.DataFrame([row])

#df_input = get_binance_input_row()
#print(df_input.shape)