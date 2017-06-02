import sys
import matplotlib
matplotlib.use("Qt5Agg")
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import pandas as pd
import function as f
import numpy as np

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.left = 100
        self.top = 100
        self.title = 'Anomaly Finder'
        self.width = 1110
        self.height = 620

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.create_main_window()
        self.create_menu()

    def create_menu(self):
        # Создание пунктов меню интерфейса

        self.file_menu = QMenu('&Файл', self)
        self.file_menu.addAction("&Загрузить тестовую выборку", self.on_load_file, QtCore.Qt.CTRL + QtCore.Qt.Key_T)
        self.file_menu.addAction("&Загрузить обучающую выборку", self.on_load_teacherfile, QtCore.Qt.CTRL + QtCore.Qt.Key_Y)
        self.file_menu.addSeparator()
        self.file_menu.addAction("&Сохранить график", self.on_save_plot, QtCore.Qt.CTRL + QtCore.Qt.Key_P)
        self.file_menu.addAction("&Сохранить размеченную выборку", self.on_save_marked, QtCore.Qt.CTRL + QtCore.Qt.Key_S)
        self.file_menu.addSeparator()
        self.file_menu.addAction('&Выход', self.on_fileQuit, QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)
        self.help_menu = QMenu('&Помощь', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)
        self.help_menu.addAction('&О программе', self.on_about)

    def create_main_window(self):
        # Создание интерфейса главного окна

        self.main_frame = QWidget()

        self.button = QPushButton('Поиск', self)
        self.button.setToolTip('Выполнится поиск аномалий и аномальных паттернов')
        self.button.clicked.connect(self.on_click)

        self.dpi = 100
        self.fig = Figure(figsize=(10, 6), dpi=self.dpi)

        self.axes = self.fig.add_subplot(111)
        self.axes.tick_params(labelsize=8)
        self.axes.set_title('Time series')
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        self.toolbar = NavigationToolbar(self.canvas, self.main_frame)

        self.sp_i = QSpinBox()
        self.sp_i.setMinimum(2)
        self.sp_i.setMaximum(10)

        self.lbl_i = QLabel("Длина паттерна")

        hbox = QHBoxLayout()
        vbox_ = QVBoxLayout()

        for w in [self.button,self.lbl_i,self.sp_i]:
            vbox_.addWidget(w)
            vbox_.setAlignment(w, Qt.AlignTop)

        hbox.addLayout(vbox_)
        hbox.setAlignment(vbox_, Qt.AlignTop)

        self.tb = QPlainTextEdit()
        self.tb.setReadOnly(True)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.toolbar)
        hbox.addLayout(vbox)
        hbox.addWidget(self.tb)
        self.main_frame.setLayout(hbox)
        self.setCentralWidget(self.main_frame)
        self.statusBar().showMessage('Добро пожаловать!', 2000)

    def search(self):
        #В этой функции выполняется обучение, поик аномальных точек и аномальных паттернов во тестовом временном ряду

        try:
            outlier_fraction = 0.07
            pattern_length = self.sp_i.value()
            data_train = f.SVM.clf(self.teacher, self.data, outlier_fraction)
            # n_inliers = int((1. - outlier_fraction) * np.shape(data_train[data_train.is_outlier == False])[0])
            # n_outliers = int(outlier_fraction * np.shape(data_train[data_train.is_outlier == True])[0])

            # plot the line, the points, and the nearest vectors to the plane
            # self.axes.contour(xx, yy, Z, levels=np.linspace(Z.min(), 0, 7))
            # a = self.axes.contour(xx, yy, Z, levels=[0], linewidths=2, colors='darkred')
            # self.axes.contour(xx, yy, Z, levels=[0, Z.max()], colors='palevioletred')

            self.data_marked = f.Patterns.add_sym_str(data_train)
            indexes, pattern, percents = f.Patterns.find_pattern(self.data_marked, pattern_length)
            self.tb.setPlainText('')
            for i in range(0, len(indexes)):
                self.tb.appendPlainText('Anomaly in date %s with percent %f\nPattern: \'%s\' \n' % (
                                        self.data_marked['DateTime'][indexes[i]].strftime("%d-%m-%Y %H:%M"), percents[i], pattern[i]))

                # b1 = self.axes.plot(self.teacher['DateTime'], self.teacher['Energy'], c='black', label = "train")

            b2 = self.axes.plot(data_train['DateTime'], data_train['Energy'], color='green', label="test")
            outlier = data_train[data_train.is_outlier == True]
            Xouniques, Xo = np.unique(outlier['DateTime'], return_index=True)

            b3 = self.axes.scatter(Xouniques, outlier['Energy'], color='red', s=30)
            # self.axes.legend([b3],
            #                 ['outliers_test'],
            #                 loc="upper left",
            #                 prop=matplotlib.font_manager.FontProperties(size=11))
            self.axes.set_ylabel('Energy')
            self.axes.set_xlabel('DateTime')
            # self.axes.set_yticklabels(self.data_marked['Energy_sym'])
            self.show()
            self.canvas.draw()


        except  Exception:
            self.statusBar().showMessage('Exception: %s' % sys.exc_info()[0], 2000)

    def on_click(self):
        #Функция вызываемая при нажатии кнопки "Поиск

        all_load = True

        try:
            self.teacher
        except  Exception:
            all_load = False
            QMessageBox.about(self, "Ошибка",
                              """Перед поиском необходимо загрузить обучающую выборку.""")

        try:
            self.data
        except  Exception:
            all_load = False
            QMessageBox.about(self, "Ошибка",
                              """Перед поиском необходимо загрузить тестовую выборку.""")

        if all_load:
            self.search()

    def on_load_teacherfile(self):
        #Функция загружающая выбранный файл обучающей выборки

        try:
            file_choices = "CSV (*.csv)|*.csv"
            path = (QFileDialog.getOpenFileName(self, 'Загрузка обучающей выборки', '',file_choices))
            self.teacher = pd.read_csv(path[0], ';', nrows=67) #671
            self.teacher = f.ForData.correct_data(self.teacher)
            self.statusBar().showMessage('Файл %s загружен' % path[0], 2000)
        except  Exception:
            self.statusBar().showMessage('Exception: %s' % sys.exc_info()[0], 2000)

    def on_load_file(self):
        # Функция загружающая выбранный файл тестовой выборки

        try:
            file_choices = "CSV (*.csv)|*.csv"
            path = (QFileDialog.getOpenFileName(self, 'Загрузка тестового файла', '',file_choices))
            self.data = pd.read_csv(path[0], ';', nrows=67)
            self.data = f.ForData.correct_data(self.data)
            self.statusBar().showMessage('Файл %s открыт' % path[0], 2000)
        except  Exception:
            self.statusBar().showMessage('Exception: %s' % sys.exc_info()[0], 2000)

    def on_fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.on_fileQuit()

    def on_about(self):
        QMessageBox.about(self, "О программе","""Эта программа выполняет поиск аномальных паттернгов во временном ряду энергопотребления при помощи символьного анализа.""")

    def on_save_plot(self):
        #Функция сохранения графика в файл

        file_choices = "PNG (*.png)|*.png"
        path = (QFileDialog.getSaveFileName(self,'Сохранить график', '',file_choices))
        if path:
            self.canvas.print_figure(filename = path[0], format = 'png', dpi=self.dpi)
            self.statusBar().showMessage('График сохранен в %s' % path[0], 2000)

    def on_save_marked(self):
        #Функция сохранения размеченного временного ряда

        isfile = True
        try:
            self.data_marked
        except  Exception:
            isfile = False
            QMessageBox.about(self, "Ошибка",
                              """Перед сохранением необходимо произвести поиск аномальных паттернов.""")

        if isfile:
            try:
                file_choices = "CSV (*.csv)|*.csv"
                path = (QFileDialog.getSaveFileName(self, 'Сохранить размеченный временной ряд', '',file_choices))
                if path:
                    self.data_marked.to_csv(path[0])
                self.statusBar().showMessage('Сохранен в %s' % path[0], 2000)
            except  Exception:
                self.statusBar().showMessage('Exception: %s' % sys.exc_info()[0], 2000)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
