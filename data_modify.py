import pandas as pd

class ForData:
    #Класс для операций с файлами

    def correct_data(df):
        """Функция для приведения входного файла к нужному форматуи

            df - DataFrame с данными

            :return
                df - DataFrame с скорректированными форматами данных
        """

        del df['\t']
        df['Energy'] = df['Energy'].str.replace(',','.')
        df['Energy'] = pd.to_numeric(df['Energy'], errors='coerce')
        df['DateTime'] = pd.to_datetime(df['DateTime'],format='%d.%m.%Y %H:%M')
        return df