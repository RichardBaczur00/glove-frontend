import json
import serial
import random

from PyQt5 import QtCore

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPlainTextEdit

from PyQt5.QtCore import Qt, QThread, pyqtSignal

from pyqtgraph import PlotWidget
from pyqtgraph import plot
import pyqtgraph as pg


class SerialReader(QThread):
    data_received = pyqtSignal(str)

    def __init__(self, port, baud_rate):
        super().__init__()
        self.serial_port = serial.Serial(port, baud_rate)

    def run(self):
        while True:
            if self.serial_port.is_open:
                data = self.serial_port.readline.decode().strip()
                self.data_received.emit(data)


class IndexPage(QWidget):
    def __init__(self):
        super(IndexPage, self).__init__()
        self.initUI()

        self.serial_reader = SerialReader('COM3', 9600)
        self.serial_reader.data_received.connect(self.update_plots)

        self.serial_reader.start()

    def init_graphs(self):
        graph_widgets = [
            pg.PlotWidget() for i in range(5)
        ]

        graph_widgets[0].setTitle('Thumb')
        graph_widgets[1].setTitle('Index')
        graph_widgets[2].setTitle('Middle')
        graph_widgets[3].setTitle('Ring')
        graph_widgets[4].setTitle('Pinky')

        pen = pg.mkPen(color=(255,0,0))
        self.graph_data = [
            [[0], [0], graph_widgets[i].plot([], [], pen=pen)] for i in range(5)
        ]

        graphs_layout = QVBoxLayout()
        first_row = QHBoxLayout()
        second_row = QHBoxLayout()

        for i in range(3):
            first_row.addWidget(graph_widgets[i])
        for i in range(3, 5):
            second_row.addWidget(graph_widgets[i])
        
        graphs_layout.addLayout(first_row)
        graphs_layout.addLayout(second_row)

        return graphs_layout
    
    def init_controls(self):
        control_layout = QVBoxLayout()

        start_session_button = QPushButton('Start session')
        start_session_button.clicked.connect(self.start_session)
        self.next_prompt_button = QPushButton('Next prompt')
        self.next_prompt_button.clicked.connect(self.next_prompt)
        self.next_prompt_button.setEnabled(False)

        label = QLabel('Please perform the handmotions to get this result:')
        self.category = QLabel('')
        self.text = QPlainTextEdit('(Aici o sa vina textul, acum e doar asta, Lorem ipsum ceva ceva)')
        self.text.setReadOnly(True)

        control_layout.addWidget(label)
        control_layout.addWidget(self.category)
        control_layout.addWidget(self.text)

        control_layout.addWidget(start_session_button)
        control_layout.addWidget(self.next_prompt_button)        

        return control_layout

    def initUI(self):
        layout = QHBoxLayout()
        self.setWindowTitle('Glove Index')
        self.setGeometry(100, 100, 1600, 900)
        
        graphs_layout = self.init_graphs()
        controls_layout = self.init_controls()
        layout.addLayout(controls_layout)
        layout.addLayout(graphs_layout)
        # self.open_window_button.clicked.connect(self.start_session)
        self.setLayout(layout)

    def start_session(self):
        with open('data.json', 'r') as f:
            data = json.load(f)
            self.prompt_generator = ((key, value) for key, values in data.items() for value in values)
            self.next_prompt()
            self.next_prompt_button.setEnabled(True)
        
    def next_prompt(self):
        try:
            category, prompt_text = next(self.prompt_generator)
            self.text.setPlainText(prompt_text)
            self.category.setText(f'Category: {category}')
            self.update_plots_testing()
        except StopIteration:
            self.next_prompt_button.setEnabled(False)
            self.text.setPlainText('All done!')

    def update_plots_testing(self):
        for gi in range(5):
            if len(self.graph_data[gi][0]) > 50:
                self.graph_data[gi][0] = self.graph_data[gi][0][1:]
                self.graph_data[gi][1] = self.graph_data[gi][1][1:]
            self.graph_data[gi][0].append(self.graph_data[gi][0][-1] + 1)
            self.graph_data[gi][1].append(random.randint(0, 100))
            self.graph_data[gi][2].setData(self.graph_data[gi][0], self.graph_data[gi][1])

    def update_plots(self, data):
        pass
