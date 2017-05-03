import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager
from sklearn import svm
import pandas as pd
from scipy import stats
import string

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

if __name__ == '__main__':
    teacher = pd.read_csv('data/Building02.csv', ';', nrows=67,header=0)
    del teacher['\t']
    teacher['Energy'] = teacher['Energy'].str.replace(',','.')
    teacher['Energy'] = pd.to_numeric(teacher['Energy'], errors='coerce')
    X_tr = np.zeros((66, 2))

    data_tr = np.array(teacher['Energy'])
    result_string_tr = represent(data_tr)
    result_string_tr = list(result_string_tr)
    for i in range(0,np.shape(X_tr)[0]):
        X_tr[i][0]= teacher['DateTime'][i]
        X_tr[i][1]= teacher['Energy'][i]

    data = pd.read_csv('data/Building0teacher2.csv', ';', nrows=67,header=0)
    del data['\t']
    data['Energy'] = data['Energy'].str.replace(',','.')
    data['Energy'] = pd.to_numeric(data['Energy'], errors='coerce')
    X_ts = np.zeros((66, 2))

    data_ts = np.array(data['Energy'])
    result_string_ts = represent(data_ts)
    result_string_ts = list(result_string_ts)
    for i in range(0,np.shape(X_ts)[0]):
        X_ts[i][0]= data['DateTime'][i]
        X_ts[i][1]= data['Energy'][i]

    # fit the model
    clf = svm.OneClassSVM(nu=0.1, kernel="rbf", gamma=0.1)

    clf.fit(X_tr)
    y_pred_train = clf.predict(X_tr)
    y_pred_test = clf.predict(X_ts)
    #y_pred_outliers = clf.predict(X_outliers)
    n_error_train = y_pred_train[y_pred_train == -1].size
    n_error_test = y_pred_test[y_pred_test == -1].size
    #n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size

    OUTLIER_FRACTION = 0.07
    dist_to_border = clf.decision_function(X_ts).ravel()
    threshold = stats.scoreatpercentile(dist_to_border,
                100 * OUTLIER_FRACTION)
    is_inlier = dist_to_border > threshold

    # plot the line, the points, and the nearest vectors to the plane
    xx, yy = np.meshgrid(np.linspace(0, 70, 700), np.linspace(0, 50, 500))
    n_inliers = int((1. - OUTLIER_FRACTION) * np.shape(X_tr)[0])
    n_outliers = int(OUTLIER_FRACTION * np.shape(X_tr)[0])
    Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    plt.title("Novelty Detection")
    plt.contourf(xx, yy, Z, levels=np.linspace(Z.min(), 0, 7), cmap=plt.cm.PuBu)
    a = plt.contour(xx, yy, Z, levels=[0], linewidths=2, colors='darkred')
    plt.contourf(xx, yy, Z, levels=[0, Z.max()], colors='palevioletred')

    s = 40
    b1 = plt.scatter(X_tr[is_inlier == 0, 0], X_tr[is_inlier == 0, 1], c='white', s=s)
    b2 = plt.scatter(X_ts[is_inlier == 1, 0], X_ts[is_inlier == 1, 1], c='blueviolet', s=s)
    b3 = plt.scatter(X_ts[is_inlier == 0, 0], X_ts[is_inlier == 0, 1], c='gold', s=s)
    outliers = X_ts[is_inlier == 0]
    for i in outliers:
        print(int(i[0]),' ',result_string_ts[int(i[0])],' ', i[1])
    #c = plt.scatter(X_outliers[:, 0], X_outliers[:, 1], c='gold', s=s)
    plt.axis('tight')
    plt.xlim((-1, 75))
    plt.ylim((-1, 70))
    plt.legend([a.collections[0], b1, b2,b3],
               ['learned decision function', 'inliers_train', 'inliers_test','outliers_test'],
               loc="upper left",
               prop=matplotlib.font_manager.FontProperties(size=11))
    #plt.xlabel("error train: %d/200 ; errors novel regular: %d/40 ; ""errors novel abnormal: %d/40"% (n_error_train, n_error_test, n_error_outliers))
    plt.show()

"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager
from sklearn import svm
import pandas as pd


teacher = pd.read_csv('data/Building02.csv', ';', nrows=67,header=0)
del teacher['\t']
teacher['Energy'] = teacher['Energy'].str.replace(',','.')
teacher['Energy'] = pd.to_numeric(teacher['Energy'], errors='coerce')
X_tr = np.zeros((66, 2))

for i in range(0,np.shape(X_tr)[0]):
    X_tr[i][0]= teacher['DateTime'][i]
    X_tr[i][1]= teacher['Energy'][i]

data = pd.read_csv('data/Building0teacher2.csv', ';', nrows=25,header=0)
del data['\t']
data['Energy'] = data['Energy'].str.replace(',','.')
data['Energy'] = pd.to_numeric(data['Energy'], errors='coerce')
X_ts = np.zeros((24, 2))

for i in range(0,np.shape(X_ts)[0]):
    X_ts[i][0]= data['DateTime'][i]
    X_ts[i][1]= data['Energy'][i]



xx, yy = np.meshgrid(np.linspace(0, 70, 700), np.linspace(0, 50, 500))
# Generate train data
X = 0.3 * np.random.randn(100, 2)

X_train = np.r_[X + 2, X - 2]
#for i in X_train:
  #  print(i)
# Generate some regular novel observations
X = 0.3 * np.random.randn(20, 2)
X_test = np.r_[X + 2, X - 2]

# Generate some abnormal novel observations
#X_outliers = np.random.uniform(low=-4, high=4, size=(20, 2))

# fit the model
clf = svm.OneClassSVM(nu=0.1, kernel="rbf", gamma=0.1)
clf.fit(X_tr)
y_pred_train = clf.predict(X_tr)
y_pred_test = clf.predict(X_ts)
#y_pred_outliers = clf.predict(X_outliers)
n_error_train = y_pred_train[y_pred_train == -1].size
n_error_test = y_pred_test[y_pred_test == -1].size
#n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size

# plot the line, the points, and the nearest vectors to the plane
Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)

plt.title("Novelty Detection")
plt.contourf(xx, yy, Z, levels=np.linspace(Z.min(), 0, 7), cmap=plt.cm.PuBu)
a = plt.contour(xx, yy, Z, levels=[0], linewidths=2, colors='darkred')
plt.contourf(xx, yy, Z, levels=[0, Z.max()], colors='palevioletred')

s = 40
b1 = plt.scatter(X_tr[:, 0], X_tr[:, 1], c='white', s=s)
b2 = plt.scatter(X_ts[:, 0], X_ts[:, 1], c='blueviolet', s=s)
#c = plt.scatter(X_outliers[:, 0], X_outliers[:, 1], c='gold', s=s)
plt.axis('tight')
plt.xlim((0, 70))
plt.ylim((0, 55))
plt.legend([a.collections[0], b1, b2],
           ["learned frontier", "training observations",
            "new regular observations", "new abnormal observations"],
           loc="upper left",
           prop=matplotlib.font_manager.FontProperties(size=11))
#plt.xlabel("error train: %d/200 ; errors novel regular: %d/40 ; ""errors novel abnormal: %d/40"% (n_error_train, n_error_test, n_error_outliers))
plt.show()
"""