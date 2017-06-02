from sklearn import svm
from scipy import stats
import numpy as np
import pandas as pd
import string
import re

class Patterns:
    #Класс поиска аномальных паттернов в размеченной выборке

    ALPHABET = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
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
        # normalize input data and present as symbol string
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
            if i-length >= 0:
                tmp = []
                for j in range(i-length,i):
                    tmp.append(data['Energy_sym'][j])
                #d_p[i] = ''.join(tmp)
                list_patterns.append(''.join(tmp))
        percents = []
        for pattern in list_patterns:
            percents.append(Patterns.count_(list_patterns,pattern)/len(re.findall(pattern,string))*100)

        return indexes,list_patterns,percents

class SVM:
    #Класс обучения и поиска аномальных точек

    def prepare_data(df):
        """Функция для подготовки данных к классификации

            df - DataFrame с данными

            :return
                data_mas - Массив с данными из сходного DataFrame
        """
        data_mas = np.zeros((np.shape(df['Energy'])[0], 2))

        for i in range(0, np.shape(data_mas)[0]):
            data_mas[i][0] = i
            data_mas[i][1] = df['Energy'][i]

        return data_mas

    def clf(df_train, df_test,outlier_fraction = 0.07):
        """ Функция классификации

            df_train            - обучающая выборка
            df_test             - тестовая выборка
            outlier_fraction    - коэффициент для поиска аномальных точек

            :return
                df_test - расмеченная выборка на основе df_test
        """

        train_data = SVM.prepare_data(df_train)
        test_data = SVM.prepare_data(df_test)

        clf = svm.OneClassSVM(nu=0.1, kernel="rbf", gamma=0.1)

        clf.fit(train_data)
        y_pred_train = clf.predict(train_data)
        y_pred_test = clf.predict(test_data)
        n_error_train = y_pred_train[y_pred_train == -1].size
        n_error_test = y_pred_test[y_pred_test == -1].size

        dist_to_border = clf.decision_function(test_data).ravel()
        threshold = stats.scoreatpercentile(dist_to_border,
                                            100 * outlier_fraction)
        is_inlier = dist_to_border > threshold

        df_test.insert(2, 'is_outlier', False)

        for i in test_data[is_inlier == 0, 0]:
            df_test.loc[i,'is_outlier'] = True

        return df_test

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