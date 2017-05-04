from sklearn import svm
from scipy import stats
import numpy as np

class SVM:
    def prepare_data(df):
        data_mas = np.zeros((np.shape(df['Energy'])[0], 2))

        for i in range(0, np.shape(data_mas)[0]):
            data_mas[i][0] = df['DateTime'][i]
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
        xx, yy = np.meshgrid(np.linspace(0, 70, 700), np.linspace(0, 50, 500))
        Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)


        return train_data, test_data[is_inlier == 1], test_data[is_inlier == 0], xx, yy, Z