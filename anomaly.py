from sklearn import svm
from scipy import stats
import numpy as np

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

    def clf(df_train, df_test,outlier_fraction = 0.05):
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
                                            outlier_fraction*10)

        is_inlier = dist_to_border > threshold

        if list(df_test).count('is_outlier') > 0:
            del df_test['is_outlier']

        df_test.insert(2, 'is_outlier', False)

        for i in test_data[is_inlier == 0, 0]:
            df_test.loc[i,'is_outlier'] = True

        return df_test