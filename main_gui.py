import sys
import matplotlib
matplotlib.use("Qt5Agg")
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from anomaly import *
from pattern import *
from data_modify import *

class TableModel(QAbstractTableModel):
    def __init__(self, datain, headerdata, parent=None):
        """
        Args:
            datain: a list of lists\n
            headerdata: a list of strings
        """
        QAbstractTableModel.__init__(self, parent)
        self.arraydata = datain
        self.headerdata = headerdata

    def rowCount(self, parent):
        return len(self.arraydata)

    def columnCount(self, parent):
        if len(self.arraydata) > 0:
            return len(self.arraydata[0])
        return 0

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        return QVariant(self.arraydata[index.row()][index.column()])

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.left = 100
        self.top = 100
        self.title = 'Anomaly Finder'
        self.width = 1310
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

        self.sp_of = QDoubleSpinBox()
        self.sp_of.setSingleStep(0.01)
        self.sp_of.setDecimals(2)
        self.sp_of.setValue(0.5)
        self.sp_of.setMinimum(0)
        self.sp_of.setMaximum(10)

        self.lbl_i = QLabel("Длина паттерна")
        self.lbl_of = QLabel("Коэффициент поиска аномалии")

        hbox = QHBoxLayout()
        vbox_ = QVBoxLayout()

        for w in [self.button,self.lbl_i,self.sp_i,self.lbl_of,self.sp_of]:
            vbox_.addWidget(w)
            vbox_.setAlignment(w, Qt.AlignTop)

        hbox.addLayout(vbox_)
        hbox.setAlignment(vbox_, Qt.AlignTop)

        self.lbl_tb = QLabel("Аномальные паттерны")
        self.tb = QPlainTextEdit()
        self.tb.setReadOnly(True)

        vbox_tb = QVBoxLayout()
        for w in [self.lbl_tb,self.tb]:
            vbox_tb.addWidget(w)

        self.lbl_tbl = QLabel("Таблица соответствия значений")
        self.table = QTableView()

        vbox_tbl = QVBoxLayout()
        for w in [self.lbl_tbl, self.table]:
            vbox_tbl.addWidget(w)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.toolbar)
        hbox.addLayout(vbox)
        hbox.addLayout(vbox_tb)
        hbox.addLayout(vbox_tbl)

        self.main_frame.setLayout(hbox)
        self.setCentralWidget(self.main_frame)
        self.statusBar().showMessage('Добро пожаловать!', 2000)

    def search(self):
        #В этой функции выполняется обучение, поиск аномальных точек и аномальных паттернов во тестовом временном ряду

        try:
            outlier_fraction = self.sp_of.value()
            pattern_length = self.sp_i.value()

            data_train = SVM.clf(self.teacher, self.data, outlier_fraction)

            if list(data_train).count('Energy_sym') == 0:
                self.data_marked = Patterns.add_sym_str(data_train)

            indexes, pattern, percents = Patterns.find_pattern(self.data_marked, pattern_length)
            self.tb.setPlainText('')
            for i in range(0, len(indexes)):
                self.tb.appendPlainText('Anomaly in date %s with percent %f\nPattern: \'%s\' \n' % (
                                        self.data_marked['DateTime'][indexes[i]].strftime("%d-%m-%Y %H:%M"), percents[i], pattern[i]))

            lst = data_train['Energy'].sort_values().drop_duplicates().values.tolist()
            lst_sym = Patterns.represent(lst)
            lst_sym = list(lst_sym)

            tabledata = []
            for i in range(0, len(lst)):
                tabledata.append([str(lst[i]),str(lst_sym[i])])

            header = ['Num','Sym']

            model = TableModel(tabledata,header,self)
            self.table.setModel(model)
            self.table.update()

            self.axes.clear()
            self.axes.plot(data_train['DateTime'], data_train['Energy'], color='green', label="test")
            outlier = data_train[data_train.is_outlier == True]
            Xouniques, Xo = np.unique(outlier['DateTime'], return_index=True)
            self.axes.scatter(Xouniques, outlier['Energy'], color='red', s=30)
            self.axes.set_ylabel('Energy')
            self.axes.set_xlabel('DateTime')
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
            if len(path[0]) != 0:
                self.teacher = pd.read_csv(path[0], ';') #671
                self.teacher = ForData.correct_data(self.teacher)
                self.statusBar().showMessage('Файл %s загружен' % path[0], 2000)
        except  Exception:
            QMessageBox.about(self, "Ошибка",
                              """Неверный формат файла.""")
            self.statusBar().showMessage('Exception: %s' % sys.exc_info()[0], 2000)

    def on_load_file(self):
        # Функция загружающая выбранный файл тестовой выборки

        try:
            file_choices = "CSV (*.csv)|*.csv"
            path = (QFileDialog.getOpenFileName(self, 'Загрузка тестового файла', '',file_choices))
            if len(path[0]) != 0:
                self.data = pd.read_csv(path[0], ';')
                self.data = ForData.correct_data(self.data)
                self.statusBar().showMessage('Файл %s открыт' % path[0], 2000)
        except  Exception:
            QMessageBox.about(self, "Ошибка",
                              """Неверный формат файла.""")
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
