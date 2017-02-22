import pandas as pd
import datetime

def correctdata(df):
    del df['\t']
    df['Energy'] = df['Energy'].str.replace(',','.')
    df['Energy'] = pd.to_numeric(df['Energy'], errors='coerce')
    df['DateTime'] = pd.to_datetime(df['DateTime'],format='%d.%m.%Y %H:%M')
    return df