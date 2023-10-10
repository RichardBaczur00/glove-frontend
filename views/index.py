import json
import serial
import random
 
from PyQt5 import QtCore
from PyQt5 import QtGui
 
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
 
from network import session
 
FINGER_NAMES = [
    'a',
    'b',
    'c',
    'd',
    'e',
    'g'
]
 
 
class SerialReader(QThread):
    data_received = pyqtSignal(str)
 
    def __init__(self, port, baud_rate):
        super().__init__()
        self.serial_port = serial.Serial(port, baud_rate)
 
    def run(self):
        while True:
            if self.serial_port.is_open:
                data = self.serial_port.readline().decode().strip()
                self.data_received.emit(data)
 
 
class IndexPage(QWidget):
    def __init__(self):
        super(IndexPage, self).__init__()
        self.initUI()
 
        self.serial_reader = SerialReader('/dev/cu.usbmodem0740D1DC33491', 115200)
        self.serial_reader.data_received.connect(self.update_plots)
 
        self.serial_reader.start()
        self.running = False
 
    def init_graphs(self):
        graph_widgets = [
            pg.PlotWidget() for i in range(6)
        ]
 
        graph_widgets[0].setTitle('Thumb - Duim')
        graph_widgets[1].setTitle('Index - Wijsvinger')
        graph_widgets[2].setTitle('Middle - Middelvinger')
        graph_widgets[3].setTitle('Ring - Ringvinger')
        graph_widgets[4].setTitle('Pinky - Pink')
        graph_widgets[5].setTitle('Hand Motion - Handbeweging')
 
        pen = pg.mkPen(color=(255,0,0))
        self.graph_data = [
            [[0], [0], graph_widgets[i].plot([], [], pen=pen)] for i in range(5)
        ]
        self.gyro_data = [
            [[0], [0], graph_widgets[5].plot([], [], pen=(i, 3))] for i in range(3)
        ]
 
        graphs_layout = QVBoxLayout()
        first_row = QHBoxLayout()
        second_row = QHBoxLayout()
 
        for i in range(3):
            first_row.addWidget(graph_widgets[i])
        for i in range(3, 6):
            second_row.addWidget(graph_widgets[i])
        
        graphs_layout.addLayout(first_row)
        graphs_layout.addLayout(second_row)
 
        return graphs_layout
    
    def init_controls(self):
        control_layout = QVBoxLayout()
 
        start_session_button = QPushButton('Start')
        start_session_button.clicked.connect(self.start_session)
        self.next_prompt_button = QPushButton('Next')
        self.next_prompt_button.clicked.connect(self.next_prompt)
        self.next_prompt_button.setEnabled(False)
 
        label_en = QLabel('Data collected for the hand and each finger')
        label_dt = QLabel('Verzamelde gegevens voor de hand en elke vinger')
        self.category = QLabel('')
        self.text = QPlainTextEdit('Wij zijn het team van de ChatterGlove en dit is onze gegevensverzamelingstoepassing voor het trainen van de handschoen.')
        self.text.setReadOnly(True)
        
        font = QtGui.QFont()
        font.setPointSize(16)
        self.text.setFont(font)
 
        control_layout.addWidget(label_en)
        control_layout.addWidget(label_dt)
        control_layout.addWidget(self.category)
        control_layout.addWidget(self.text)
 
        control_layout.addWidget(start_session_button)
        control_layout.addWidget(self.next_prompt_button)        
 
        return control_layout
 
    def initUI(self):
        layout = QHBoxLayout()
        self.setWindowTitle('ChatterGlove Data Acquisition - ChatterGlove-gegevensverzameling')
        self.setGeometry(100, 100, 1600, 900)
        
        graphs_layout = self.init_graphs()
        controls_layout = self.init_controls()
        layout.addLayout(controls_layout)
        layout.addLayout(graphs_layout)
        # self.open_window_button.clicked.connect(self.start_session)
        self.setLayout(layout)
 
    def start_session(self):
        with open('../data.json', 'r') as f:
            data = json.load(f)
            self.prompt_generator = ((key, value) for key, values in data.items() for value in values)
            self.next_prompt()
            self.next_prompt_button.setEnabled(True)
            self.running = True
        
    def next_prompt(self):
        try:
            category, prompt_text = next(self.prompt_generator)
            response = session.create_session(prompt_text, 1)
            print(response.json())
            self.current_session_id = response.json()['_id']
            self.current_order_number = 0
            self.text.setPlainText(prompt_text)
            self.category.setText(f'Category: {category}')
        except StopIteration:
            self.next_prompt_button.setEnabled(False)
            self.text.setPlainText('All done!')
            self.running = False

    def update_plots_testing(self):
        for gi in range(5):
            if len(self.graph_data[gi][0]) > 50:
                self.graph_data[gi][0] = self.graph_data[gi][0][1:]
                self.graph_data[gi][1] = self.graph_data[gi][1][1:]
            self.graph_data[gi][0].append(self.graph_data[gi][0][-1] + 1)
            self.graph_data[gi][1].append(random.randint(0, 100))
            self.graph_data[gi][2].setData(self.graph_data[gi][0], self.graph_data[gi][1])
        for gi in range(3):
            if (len(self.gyro_data[gi][0])) > 50:
                self.gyro_data[gi][0] = self.gyro_data[gi][0][1:]
                self.gyro_data[gi][1] = self.gyro_data[gi][1][1:]
            self.gyro_data[gi][0].append(self.gyro_data[gi][0][-1] + 1)
            self.gyro_data[gi][1].append(random.randint(0, 100))
            self.gyro_data[gi][2].setData(self.gyro_data[gi][0], self.gyro_data[gi][1])

 
    def update_plots(self, data):
        if self.running:
            print(data)
            values = list(map(lambda x: float(x), data.split(' ')))
            response = session.put_result_data(
                self.current_session_id,
                self.current_order_number,
                {
                    finger: val for finger, val in zip(FINGER_NAMES, values)
                }
            )
            self.current_order_number += 1
            for gi in range(5):
                if len(self.graph_data[gi][0]) > 50:
                    self.graph_data[gi][0] = self.graph_data[gi][0][1:]
                    self.graph_data[gi][1] = self.graph_data[gi][1][1:]
                self.graph_data[gi][0].append(self.graph_data[gi][0][-1] + 1)
                self.graph_data[gi][1].append(values[gi])
                self.graph_data[gi][2].setData(self.graph_data[gi][0], self.graph_data[gi][1])
            for gi in range(3):
                if (len(self.gyro_data[gi][0])) > 50:
                    self.gyro_data[gi][0] = self.gyro_data[gi][0][1:]
                    self.gyro_data[gi][1] = self.gyro_data[gi][1][1:]
                self.gyro_data[gi][0].append(self.gyro_data[gi][0][-1] + 1)
                self.gyro_data[gi][1].append(values[gi + 5])
                self.gyro_data[gi][2].setData(self.gyro_data[gi][0], self.gyro_data[gi][1])
