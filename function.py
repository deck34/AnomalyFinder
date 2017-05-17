from sklearn import svm
from scipy import stats
import numpy as np
import pandas as pd
import string
import re

ALPHABET = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
ALPHABET_LEN = len(ALPHABET)-1

def represent(data):
    dmin = min(data)
    dmax = max(data)
    ddelta = dmax - dmin
    dstep = ddelta / ALPHABET_LEN
    # normalize input data and present as symbol string
    representer = lambda d: \
        ALPHABET[int(np.round(((d - dmin) / ddelta) * ALPHABET_LEN))]
    return ''.join(map(representer, data))

def add_sym_str(data):
    data_sym_str = represent(data['Energy'])
    data_sym_str = list(data_sym_str)

    data.insert(2, 'Energy_sym', data_sym_str)
    return data

def count_(list,str):
    count = 0
    for i in list:
        if i == str:
            count += 1
    return count
def find_pattern(data,length):
    string = ''.join(data['Energy_sym'])
    indexes = data[data.is_outlier == True].index.tolist()
    list_patterns = []
    for i in indexes:
        if i-length >= 0:
            tmp = []
            for j in range(i-length,i):
                tmp.append(data['Energy_sym'][j])
            list_patterns.append(''.join(tmp))
    percents = []
    for pattern in list_patterns:
        percents.append(count_(list_patterns,pattern)/len(re.findall(pattern,string))*100)

    print(string)
    print(list_patterns)
    print(percents)

class SVM:
    def prepare_data(df):
        data_mas = np.zeros((np.shape(df['Energy'])[0], 2))

        for i in range(0, np.shape(data_mas)[0]):
            data_mas[i][0] = i #df['DateTime'][i]
            data_mas[i][1] = df['Energy'][i]
        return data_mas

    def clf(df_train, df_test,outlier_fraction = 0.07):
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

        #xx, yy = np.meshgrid(np.linspace(0, 70, 700), np.linspace(0, 50, 500))
        #Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()])
        #Z = Z.reshape(xx.shape)


        return df_test