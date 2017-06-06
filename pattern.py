import numpy as np
import string
import re

class Patterns:
    #Класс поиска аномальных паттернов в размеченной выборке

    ALPHABET = string.ascii_lowercase + string.ascii_uppercase + string.digits
    ALPHABET_LEN = len(ALPHABET) - 1

    def represent(data):
        """Функция поиска символа соответветствующему числу из входного массива

            data - массив с данными

            :return - строка символов, соответствующих значениям входного массива
        """

        dmin = min(data)
        dmax = max(data)
        ddelta = dmax - dmin
        dstep = ddelta / Patterns.ALPHABET_LEN
        # нормализация входных данных и символьное представление
        representer = lambda d: \
            Patterns.ALPHABET[int(np.round(((d - dmin) / ddelta) * Patterns.ALPHABET_LEN))]
        return ''.join(map(representer, data))

    def add_sym_str(df):
        """Функция добавляет в DataFrame столбец с символьным предствалением

            df - DataFrame с данными

            :return
                df - DataFrame с добавленной строкой символьного представления значений
        """

        data_sym_str = Patterns.represent(df['Energy'])
        data_sym_str = list(data_sym_str)


        df.insert(2, 'Energy_sym', data_sym_str)

        return df

    def count_(list,str):
        """Функция выполняет подсчет количества повторений паттернов в списке

            list    - список паттернов
            str     - строка с паттерном

            :return
                count - количество повторений
        """

        count = 0
        for i in list:
            if i == str:
                count += 1
        return count

    def find_pattern(data,length):
        """Функция выполняет поиск аномальных паттернов

            data    - DataFrame с данными
            length     - Длинна искомого паттерна

            :returns
                indexes - список индексов в DataFrame выборки
                list_patterns - список аномальных паттернов
                percents - - список процентов возникновения
        """

        string = ''.join(data['Energy_sym'])
        indexes = data[data.is_outlier == True].index.tolist()
        list_patterns = []
        for i in indexes:
            step = length
            if i-length <= 0:
                step = length + (i - length)
            tmp = []
            for j in range(i-step,i):
                tmp.append(data['Energy_sym'][j])
            list_patterns.append(''.join(tmp))
        percents = []
        for pattern in list_patterns:
            tmp = len(re.findall(pattern,string))
            if tmp != 0:
                percents.append(Patterns.count_(list_patterns,pattern)/tmp*100)


        return indexes,list_patterns,percents