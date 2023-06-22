# -*- coding: utf-8 -*-
"""School Dashboard - Main file for running the program with GUI

Main class GUI_MainWindow implements:

@Author: Krzysztof Kordal, Michał Święciło
@Date: 2023.06
"""

# Built-in

# Other Libs
from PyQt5 import QtWidgets as qtw  # GUI
import numpy as np                  # Input data manipulation
import matplotlib.pyplot as plt     # Plot drawing

# Owned modules
from src.gui_main_window import Ui_MainWindow   # Auto-generated file - GUI definition
import src.database_functions as db_func



class GUI_MainWindow(qtw.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        """Initializes Main Window, connects functionality of buttons and inputs."""
        super().__init__(*args, **kwargs)

        # Setup the UI
        self.setupUi(self)

        
        # Connect database
        self.DATABASE_PATH = r'./data/AD_Project_School.db'

        # Create a database connection
        self.db_connection = db_func.create_connection(self.DATABASE_PATH)
        self.cursor = self.db_connection.cursor()
        # Connect buttons
        self.button_general_refresh.clicked.connect(self._refresh_general_plots)


        # Plot and Refresh plots on start
        # self._refresh_general_plots()

    
    def _refresh_general_plots(self):
        # Reset the canvas
        self.mpl_widget_general_1.axis.clear()
        self.mpl_widget_general_1.axis.plot([0, 1, 2, 3], [5, 7, 2, 8])
        # Show (draw) the canvas
        self.mpl_widget_general_1.canvas.draw()

if __name__ == "__main__":
    import sys
    app = qtw.QApplication(sys.argv)
    
    ui_window = GUI_MainWindow()
    ui_window.show()

    sys.exit(app.exec_())
