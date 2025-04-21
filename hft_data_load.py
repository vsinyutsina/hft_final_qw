from airflow.decorators import task, dag
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
from pendulum import duration

DEFAULT_ARGS = {
    'owner': 'vinyutsina',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 30),
    'email': ['inucinavs@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=30),
    'execution_timeout': duration(hours=24)
}

@dag(
        catchup=True,
        default_args=DEFAULT_ARGS,
        schedule_interval='30 11 * * *',
        max_active_runs=1,
        dagrun_timeout=duration(hours=24)
)
def hft_data_load():

    def get_data(name, ticker, start, end):
        import yfinance as yf

        data = yf.download(ticker, start=start, end=end, interval='1m')
        cols = [cols[0] for cols in data.columns]
        data.columns = cols
        data['share_name'] = name
        data['ticker_name'] = ticker

        return data.reset_index()


    def normalize_columns(data):
        cols = list(map(lambda x: str.lower(x), data.columns))
        data.columns = cols
        target_columns = ['datetime', 'close', 'high', 'low', 'open', 'volume', 'ticker_name', 'share_name']
        add_cols = set(target_columns) - set(cols)
        del_cols = set(cols) - set(target_columns)
        if len(add_cols):
            for col in add_cols:
                data[col] = [None for _ in range(data.shape[0])]

        if len(del_cols):
            data.drop(del_cols, axis=1, inplace=True)

        return data[target_columns]


    shares = {
                'Microsoft': 'MSFT',
                'Apple': 'AAPL',
                'NVIDIA': 'NVDA',
                'Amazon': 'AMZN',
                'Alphabet': 'GOOG',
                'Tesla': 'TSLA',
                'Broadcom': 'AVGO',
                'Meta': 'META',
                'Costco': 'COST',
                'Netflix': 'NFLX'
            }
    crypto = {
                'Bitcoin': 'BTC',
                'Ethereum': 'ETH',
                'Tether': 'USDT',
                'Binance': 'BNB',
                'Solana': 'SOL',
                'USD': 'USDC',
                'XRP': 'XRP',
                'Cardano': 'ADA',
                'Dogecoin': 'DOGE',
                'Toncoin': 'TON'
            }

    @task
    def clear_data(**kwargs):
        postgres_hook = PostgresHook(postgres_conn_id='postgres_hse')
        conn = postgres_hook.get_conn()
        ds = kwargs["logical_date"].to_date_string()
        print(ds)
        query = f'''
        delete from dwh_raw.timeseries_shares
        where datetime::date >= '{ds}'
        '''
        cursor = conn.cursor()
        cursor.execute(query)


    @task
    def load_data(**kwargs):
        import pandas as pd

        data_list = []
        start = kwargs["logical_date"].to_date_string()
        end = kwargs["data_interval_end"].to_date_string()
        for k, v in shares.items():
          data = get_data(k, v, start=start, end=end)
          data_list.append(data)

        for k, v in crypto.items():
          data = get_data(k, v, start=start, end=end)
          data_list.append(data)

        data = pd.concat(data_list)
        data = normalize_columns(data)

        data_to_insert = [tuple(d.values()) for d in data.to_dict('records')]

        postgres_hook = PostgresHook(postgres_conn_id='postgres_hse')
        conn = postgres_hook.get_conn()
        query = 'INSERT INTO dwh_raw.timeseries_shares (datetime, close, high, low, open, volume, ticker_name, share_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'

        cursor = conn.cursor()
        cursor.executemany(query, data_to_insert)
        conn.commit()

    clear_data() >> load_data()

hft_data_load()
