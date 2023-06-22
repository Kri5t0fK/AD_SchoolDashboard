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

        # Prepare data for comboBoxes
        self._prepare_student_student_comboBox()

        # Connect buttons
        self.button_general_refresh.clicked.connect(self._refresh_general_plots)
        # Connect comboBoxes to autorefresh
        self.input_comboBox_student_student.currentIndexChanged.connect(self._refresh_from_student_student)
        self.input_comboBox_student_subject.currentIndexChanged.connect(self._refresh_student_plots)





        # Plot and Refresh plots on start
        self._refresh_general_plots()
        self._refresh_student_plots()

    
    def _refresh_general_plots(self):
        
        # TABLES: Classes, Subjects, Grades, Teachers, Students

        widget_general_list = [self.mpl_widget_general_1, self.mpl_widget_general_2, self.mpl_widget_general_3]
        widget_general_names = ['exam_grade_hum', 'exam_grade_mat', 'exam_grade_lang']
        #TODO: tytuły wykresów
        
        

        for widget, column_name in zip(widget_general_list, widget_general_names):
            # Reset the canvas
            widget.axis.clear()

            self.cursor.execute(f"SELECT {column_name} FROM Students;")
            
            data = np.array(self.cursor.fetchall())

            widget.axis.hist(data, bins='auto', density=True, color='peru', edgecolor='black', zorder=3)
            widget.axis.set(title=column_name,
                            xlabel='Wynik [%] z egzaminu',
                            ylabel='Liczba uczniów')
            widget.axis.grid(zorder=0)
            
            # Show (draw) the canvas
            widget.canvas.draw()
        

        def make_autopct(total):
            def autopct_fun(pct):
                val = int(round(pct*total/100.0))
                return f'{val}'
            return autopct_fun

        str = "SELECT COUNT(ID_Student), Classes.Label FROM Students INNER JOIN Classes ON Students.ID_class=Classes.ID_class GROUP BY Classes.Label"
        self.cursor.execute(str)
        data = np.array(self.cursor.fetchall())
        values = data[:,0].astype('int')

        self.mpl_widget_general_4.axis.pie(values, labels=data[:,1], explode=len(data)*[0.02], autopct=make_autopct(values.sum()),
                                           labeldistance=1.1, radius=1, textprops={'fontsize': 14})
        self.mpl_widget_general_4.axis.set(title='Liczba uczniów w poszczgólnych klasach')
        self.mpl_widget_general_4.canvas.draw()
    
    def _refresh_from_student_student(self):
        self._prepare_student_subject_comboBox()
        self._refresh_student_plots()
    
    def _prepare_student_student_comboBox(self):
        # Get list of all students
        self.cursor.execute("SELECT ID_Student, name, surname FROM Students ORDER BY name ASC, surname ASC")
        self.students_list = np.array(self.cursor.fetchall())

        # Make list of concatenated [name+surname]
        full_names_list = [f'{name} {surname}' for name, surname in self.students_list[:, 1:3]]

        # Prepare student comboBox
        self.input_comboBox_student_student.clear()
        self.input_comboBox_student_student.addItems(full_names_list)

    def _prepare_student_subject_comboBox(self):
        # Get current selected student ID
        comboBox_index = self.input_comboBox_student_student.currentIndex()
        current_student_ID = self.students_list[comboBox_index, 0]

        # Fetch all subjects for given student
        self.cursor.execute(f"SELECT Subjects.ID_subject, Subjects.subject_name FROM Subjects INNER JOIN Grades ON Grades.ID_subject=Subjects.ID_subject INNER JOIN Students ON Students.ID_Student=Grades.ID_student WHERE Students.ID_Student={current_student_ID} GROUP BY Subjects.ID_subject ORDER BY subject_name ASC")
        self.student_subjects_list = np.array(self.cursor.fetchall())

        # Make list of concatenated [name+surname]
        subject_names_list = [f'{name}' for name in self.student_subjects_list[:, 1]]


        # # Prepare student comboBox
        self.input_comboBox_student_subject.clear()
        self.input_comboBox_student_subject.addItems(subject_names_list)
    
    def _refresh_student_plots(self):
        pass


if __name__ == "__main__":
    import sys
    app = qtw.QApplication(sys.argv)
    
    ui_window = GUI_MainWindow()
    ui_window.show()

    sys.exit(app.exec_())
