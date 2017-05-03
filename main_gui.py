import sys
import matplotlib
matplotlib.use("Qt5Agg")
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import work_with_data as wd
from sklearn import svm
from sklearn.preprocessing import scale
from sklearn.decomposition import PCA

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.left = 100
        self.top = 100
        self.title = 'PyQt5 application'
        self.width = 1110
        self.height = 620

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.create_main_window()
        self.create_menu()

    def create_menu(self):
        self.file_menu = QMenu('&File', self)
        self.file_menu.addAction("&Load file", self.on_load_file, QtCore.Qt.CTRL + QtCore.Qt.Key_T)
        self.file_menu.addAction("&Load teacher file", self.on_load_teacherfile, QtCore.Qt.CTRL + QtCore.Qt.Key_Y)
        self.file_menu.addSeparator()
        self.file_menu.addAction("&Save plot", self.on_save_plot, QtCore.Qt.CTRL + QtCore.Qt.Key_S)
        self.file_menu.addSeparator()
        self.file_menu.addAction('&Quit', self.on_fileQuit, QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)
        self.help_menu = QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)
        self.help_menu.addAction('&About', self.on_about)

    def create_main_window(self):
        self.main_frame = QWidget()

        self.button = QPushButton('Start', self)
        self.button.setToolTip('Press this button')
        self.button.clicked.connect(self.on_click)

        self.dpi = 100
        self.fig = Figure(figsize=(10, 6), dpi=self.dpi)

        self.axes = self.fig.add_subplot(111)
        self.axes.tick_params(labelsize='small')
        self.axes.set_title('PyQt Matplotlib')
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        self.toolbar = NavigationToolbar(self.canvas, self.main_frame)

        hbox = QHBoxLayout()

        for w in [self.button]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignTop)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.toolbar)
        hbox.addLayout(vbox)

        self.main_frame.setLayout(hbox)
        self.setCentralWidget(self.main_frame)

    def plot(self):
        try:
            # fit the model
            self.teacher['Energy'] = scale(self.teacher['Energy'])
            self.data['Energy'] = scale(self.data['Energy'])

            clf = svm.OneClassSVM(kernel="rbf")
            clf.fit(self.teacher)
            y_pred_train = clf.predict(self.teacher)
            y_pred_test = clf.predict(self.data)
            #y_pred_outliers = clf.predict(X_outliers)
            n_error_train = y_pred_train[y_pred_train == -1].size
            n_error_test = y_pred_test[y_pred_test == -1].size
           # n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size
            print(y_pred_train)
            print('\n\n')
            print(y_pred_test)

            #self.axes.plot(self.data['DateTime'], self.data['Energy'], color='b', label="Normal")

            self.show()
            self.canvas.draw()
            """
            self.teacher = wd.ForData.correct_data(self.teacher)
            #self.teacher1 = self.teacher[self.teacher['Anomaly'] == True]

            self.axes.plot(self.teacher['DateTime'], self.teacher['Energy'], color='b', label="Normal")
            #self.axes.plot(self.teacher1['DateTime'], self.teacher1['Energy'], color='r', label="Anomaly")
            self.show()
            self.canvas.draw()
            """
        except  Exception:
            self.statusBar().showMessage('Exception: %s' % sys.exc_info()[0], 2000)

    def on_click(self):
        self.plot()

    def on_load_teacherfile(self):
        print("load teacher")
        try:
            file_choices = "CSV (*.csv)|*.csv"
            path = (QFileDialog.getOpenFileName(self, 'Save file', '',file_choices))
            self.teacher = pd.read_csv(path[0], ';', nrows=671)
            self.teacher = wd.ForData.correct_data(self.teacher)
            self.statusBar().showMessage('ВЖУХ an file %s has opened' % path[0], 2000)
        except  Exception:
            self.statusBar().showMessage('Exception: %s' % sys.exc_info()[0], 2000)

    def on_load_file(self):
        print("load file")
        try:
            file_choices = "CSV (*.csv)|*.csv"
            path = (QFileDialog.getOpenFileName(self, 'Save file', '',file_choices))
            self.data = pd.read_csv(path[0], ';', nrows=671)
            self.data = wd.ForData.correct_data(self.data)
            self.statusBar().showMessage('VJUH an file %s has opened' % path[0], 2000)
        except  Exception:
            self.statusBar().showMessage('Exception: %s' % sys.exc_info()[0], 2000)

    def on_fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.on_fileQuit()

    def on_about(self):
        QMessageBox.about(self, "About","""This program for search of anomaly patterns in temporary ranks of energy consumption on the basis of the symbolical analysis.""")

    def on_save_plot(self):
        file_choices = "PNG (*.png)|*.png"
        path = (QFileDialog.getSaveFileName(self,'Save file', '',file_choices))
        if path:
            self.canvas.print_figure(filename = path[0], format = 'png', dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path[0], 2000)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
