# -*- coding: utf-8 -*-
"""Definition of widget class for embeding matplotlib in PyQt5 GUI

Classes:
- MplWidget: Widget class for embeding matplotlib in GUI

@Author: Krzysztof Kordal
@Date: 2022
"""
from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from matplotlib.figure import Figure


class MplWidget(QWidget):
    """Widget class for embeding matplotlib in GUI"""
    def __init__(self, parent = None):

        super().__init__(parent)

        # Prepare canvas with figure with 1 axis
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axis = self.figure.add_subplot(111)
        
        # Put Canvas in widget layout
        self.vertical_layout = QVBoxLayout(self)
        self.vertical_layout.addWidget(self.canvas)

