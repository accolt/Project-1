from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLineEdit, QLabel, QPushButton, QWidget, \
    QHBoxLayout, QFileDialog, QMessageBox, QComboBox, QMessageBox, QGroupBox, QSlider
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.pyplot as plt
import numpy as np
import sys
from sympy import sympify, lambdify, Symbol
import mplcursors
import ctypes
import os

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

function_dictionary = {'': ...,
                       'Sin': np.sin,
                       'Cos': np.cos,
                       'Parabola': lambda x: np.power(x, 2),
                       'Hyperbola': lambda x: np.power(x, -1),
                       'Cubic': lambda x: np.power(x, 3)}


class PlotCanvas(FigureCanvasQTAgg):
    def __init__(self):
        self.fig = plt.figure()

        super().__init__(self.fig)

        x = np.linspace(0, 0, 10)
        y = x ** 0
        self.ax = self.fig.add_subplot()
        self.curve, = self.ax.plot(x, y)
        self.ax.set(xlabel='X', ylabel='Y')
        self.ax.axhline(y=0, color='k')
        self.ax.axvline(x=0, color='k')
        self.ax.grid()
        mplcursors.cursor(hover=True)


class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('G-plotter')
        self.setWindowIcon(QIcon('sinus.png'))

        self.initUI()
        self.menu_bar()

    def initUI(self):
        self.central = QWidget()

        self.graph = PlotCanvas()

        self.main_layout = QHBoxLayout()
        self.layout1 = QVBoxLayout()
        self.layout2 = QHBoxLayout()
        self.layout3 = QVBoxLayout()

        self.label1 = QLabel('Insert Your function here:')

        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText('y(x)=')

        self.label2 = QLabel()

        self.label3 = QLabel('Or choose a function to plot:')

        self.function_droplist = QComboBox()
        self.function_droplist.addItems(tuple(function_dictionary.keys()))

        self.plot_button = QPushButton('Plot')
        self.clear_button = QPushButton('Clear')
        self.exit_button = QPushButton('Exit')

        self.layout1.addWidget(self.label1)
        self.layout1.addWidget(self.text_edit)
        self.layout1.addWidget(self.label2)
        self.layout1.addWidget(self.label3)
        self.layout1.addWidget(self.function_droplist)

        self.layout2.addWidget(self.plot_button)
        self.layout2.addWidget(self.clear_button)
        self.layout2.addWidget(self.exit_button)
        self.layout2.addStretch()

        self.layout1.addLayout(self.layout2)
        self.layout1.addStretch()

        self.label4 = QLabel('Choose a colour of the graph')
        self.color_droplist = QComboBox()
        self.color_droplist.addItem('Blue')
        self.color_droplist.addItem('Red')
        self.color_droplist.addItem('Green')
        self.layout3.addWidget(self.label4)
        self.layout3.addWidget(self.color_droplist)
        self.layout3.addStretch()
        self.label5 = QLabel('Adjust line width')
        self.layout3.addWidget(self.label5)
        self.line_size_slider = QSlider(Qt.Horizontal)
        self.line_size_slider.setMinimum(2)
        self.line_size_slider.setMaximum(10)
        self.line_size_slider.setValue(4)
        self.line_size_slider.valueChanged.connect(self.change_line_size)
        self.layout3.addWidget(self.line_size_slider)
        self.layout3.addStretch()

        self.layout1.addLayout(self.layout3)
        self.main_layout.addLayout(self.layout1)
        self.main_layout.addWidget(self.graph)

        self.central.setLayout(self.main_layout)
        self.setCentralWidget(self.central)
        self.connect_buttons()

    def connect_buttons(self):
        self.plot_button.clicked.connect(self.check_if_typed)
        self.clear_button.clicked.connect(self.clear_it)
        self.exit_button.clicked.connect(self.close)
        self.function_droplist.activated.connect(self.change_function)
        self.color_droplist.activated.connect(self.change_color)

    def check_if_typed(self):

        if self.text_edit.text():
            self.plot()
        else:
            self.nothing_to_plot()

    def change_function(self):
        func = self.function_droplist.currentText()
        x = np.linspace(-10, 10, 100)
        y = function_dictionary[func](x)
        self.update(x, y)

    def change_color(self):
        color = self.color_droplist.currentText()
        self.graph.curve.set_color(color)
        self.graph.draw()

    def invalid_input(self):
        reply1 = QMessageBox.question(self, 'Attention!', 'Invalid input! Check out acceptable input data in the'
                                                          ' "Help" menu', QMessageBox.Ok)

    def nothing_to_plot(self):
        reply2 = QMessageBox.question(self, 'Attention!', 'Nothing to plot! Please type in Your function'
                                                          ' or choose one from the dropdown list.', QMessageBox.Ok)

    def plot(self):
        self.label2.setText(self.text_edit.text())
        self.label2.adjustSize()
        font = QFont()
        font.setWeight(QFont.Bold)
        self.label2.setFont(QFont("Italic", 13, QFont.Bold))

        try:
            function = self.text_edit.text()
            x = Symbol('x')
            x_data = np.linspace(1, 10, 100)

            func = sympify(function)
            func_numpy = lambdify(x, func, 'numpy')
            y = func_numpy(x_data)
            self.update(x_data, y)
        except Exception:
            self.invalid_input()

    def update(self, x, y):
        self.graph.curve.set_data(x, y)
        self.graph.ax.set_ylim(y.min(), y.max())
        self.graph.ax.set_xlim(x.min(), x.max())

        self.graph.draw()

    def change_line_size(self, width):
        width = self.line_size_slider.value()
        self.graph.curve.set_linewidth(width)
        self.graph.draw()

    def clear_it(self):
        self.text_edit.setText('')
        self.label2.setText("")
        self.main_layout.itemAt(1).widget().deleteLater()
        self.graph = PlotCanvas()
        self.main_layout.addWidget(self.graph)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def menu_bar(self):

        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu('File')
        help_menu = menu_bar.addMenu('Help')
        save_submenu = file_menu.addMenu('Save')
        file_menu.addSeparator()
        self.exit_action = file_menu.addAction('Exit')
        self.exit_action.triggered.connect(self.close)
        self.save_image_action = save_submenu.addAction('Save plot')
        self.save_image_action.triggered.connect(self._save_plot)
        self.display_help = help_menu.addAction('Help')
        self.display_help.triggered.connect(self._help)

    def _save_plot(self):
        self.graph.fig.savefig('D:/Montan University/2021 Summer semester/GUI in Python/Plots/graph1.png')

    def _help(self):
        reply3 = QMessageBox.question(self, 'G-plotter', 'Hello there! You are using G-plotter v.1.0 - '
                                                         'the ultimate app for making graphs, upload and download'
                                                         ' coordinates data. A few tips how to input '
                                                         'a function: '
                                                         '1) A function can include x, sin(),'
                                                         'cos(),tan(),cotan() etc. No log can be used; '
                                                         '2) To return a power use **; '
                                                         '3) Multiplication is provided by * and division '
                                                         'by /. Enjoy Your plotting! ', QMessageBox.Ok)


app = QApplication([])
window = MyApp()
window.show()
app.exec()
