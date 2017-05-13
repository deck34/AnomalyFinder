import pandas as pd
import datetime

class ForData:
    def correct_data(df):
        del df['\t']
        df['Energy'] = df['Energy'].str.replace(',','.')
        df['Energy'] = pd.to_numeric(df['Energy'], errors='coerce')
        df['DateTime'] = pd.to_datetime(df['DateTime'],format='%d.%m.%Y %H:%M')
        return df

    def to_symbolic(df):

        return df

    def to_list(arr,n):
        list = []
        for i in arr:
            list.append(i[n])
        return list