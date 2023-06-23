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
        self._prepare_teacher_comboBox()
        self._prepare_teacher_subject_comboBox()
        self._prepare_teacher_class_comboBox()

        # Connect buttons
        self.button_general_refresh.clicked.connect(self._refresh_general_view)
        # Connect comboBoxes to autorefresh
        self.input_comboBox_student_student.currentIndexChanged.connect(self._refresh_from_student_student)
        self.input_comboBox_student_subject.currentIndexChanged.connect(self._refresh_student_view)
        self.input_comboBox_teacher_teacher.currentIndexChanged.connect(self._refresh_from_teacher_teacher)
        self.input_comboBox_teacher_subject.currentIndexChanged.connect(self._refresh_teacher_view)
        self.input_comboBox_teacher_class.currentIndexChanged.connect(self._refresh_teacher_view)




        # print(self.db_connection)

        #TODO: remove (GETTING TABLE NAMES)
        # self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        # print(self.cursor.fetchall())

        # Plot and Refresh plots on start
        self._refresh_general_view()
        self._prepare_student_subject_comboBox()
        self._refresh_student_view()
        self._prepare_teacher_comboBox()
        self._refresh_teacher_view()

    
    def _refresh_general_view(self):
        
        # TABLES: Classes, Subjects, Grades, Teachers, Students

        widget_general_list = [self.mpl_widget_general_1, self.mpl_widget_general_2, self.mpl_widget_general_3]
        widget_general_names = ['exam_grade_hum', 'exam_grade_mat', 'exam_grade_lang']
        colors = ['aqua', 'darkorange', 'gold']
        titles = ['Wyniki Egzaminu Humanistycznego', 'Wyniki Egzaminu Matematycznego', 'Wyniki Egzaminu Językowego']
        
        

        for widget, column_name, color, title in zip(widget_general_list, widget_general_names, colors, titles):
            # Reset the canvas
            widget.axis.clear()

            self.cursor.execute(f"SELECT {column_name} FROM Students;")
            
            data = np.array(self.cursor.fetchall())

            widget.axis.hist(data, bins='auto', density=True, color=color, edgecolor='black', zorder=3)
            widget.axis.set(title=title,
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
        
        self.mpl_widget_general_4.axis.clear()
        self.mpl_widget_general_4.axis.pie(values, labels=data[:,1], explode=len(data)*[0.02], autopct=make_autopct(values.sum()),
                                           labeldistance=1.1, radius=1, textprops={'fontsize': 14})
        self.mpl_widget_general_4.axis.set(title='Liczba uczniów w poszczgólnych klasach')
        self.mpl_widget_general_4.canvas.draw()
    
    def _refresh_from_student_student(self):
        self._prepare_student_subject_comboBox()
        # NOT USED cause it refreshes when subject comboBox gets updated (above)
        # self._refresh_student_view()
    
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
        self.cursor.execute(f"""SELECT Subjects.ID_subject, Subjects.subject_name FROM Subjects
                            INNER JOIN Grades ON Grades.ID_subject=Subjects.ID_subject
                            INNER JOIN Students ON Students.ID_Student=Grades.ID_student
                            WHERE Students.ID_Student={current_student_ID}
                            GROUP BY Subjects.subject_name
                            ORDER BY subject_name ASC""")
        self.student_subjects_list = np.array(self.cursor.fetchall())

        # Make list of concatenated [name+surname]
        subject_names_list = [f'{name}' for name in self.student_subjects_list[:, 1]]


        # # Prepare student comboBox
        self.input_comboBox_student_subject.clear()
        self.input_comboBox_student_subject.addItems(subject_names_list)
    
    def _refresh_student_view(self):
        # Get chosen data
        ## Get current selected student ID
        comboBox_index_aux = self.input_comboBox_student_student.currentIndex()
        current_student_ID = self.students_list[comboBox_index_aux, 0]
        ## Get current selected subject ID
        comboBox_index_aux = self.input_comboBox_student_subject.currentIndex()
        current_subject_name = self.student_subjects_list[comboBox_index_aux, 1]
        
        # Text: Gender and class
        ## Get gender and class for student
        self.cursor.execute(f"""SELECT Students.gender, Classes.Label FROM Students
                               INNER JOIN Classes ON Students.ID_Class=Classes.ID_Class
                               WHERE Students.ID_Student={current_student_ID}""")
        student_info = np.array(self.cursor.fetchall())
        ## Print to textBox
        self.lineEdit_student_gender.setText(student_info[0][0])
        self.lineEdit_student_class.setText(student_info[0][1])
        
        # Text: Latest 5 grades
        ## get 5 newest grades for current student
        self.cursor.execute(f"""SELECT Grades.date, Grades.grade_value, Subjects.subject_name, Teachers.name, Teachers.surname FROM Grades
                            INNER JOIN Students ON Students.ID_Student=Grades.ID_student
                            INNER JOIN Subjects ON Grades.ID_subject=Subjects.ID_subject
                            INNER JOIN Teachers ON Subjects.ID_teacher=Teachers.ID_teacher
                            WHERE Students.ID_Student={current_student_ID}
                            ORDER BY Grades.date DESC""")
        grades_list = np.array(self.cursor.fetchall())
        grades_5newest = grades_list[0:5]
        ## Prepare text table for output
        out =  '[data]     Ocena | Przedmiot (nauczyciel)\n'
        out += '-----------------|-----------------------'
        for row in grades_5newest:
            # date with time cut out
            date = row[0][0:10]
            grade_value, chosen_subject_name, teacher_name, teacher_surname = row[1:5]
            out += f'\n[{date}] {grade_value} | {chosen_subject_name} ({teacher_name} {teacher_surname})'
        ## Print to textBox
        self.plainTextEdit_student_newest_grades.setPlainText(out)
        
        # Plot 1: mean grades, all subjects
        self.cursor.execute(f"""SELECT Subjects.subject_name, AVG(Grades.grade_value) FROM Subjects
                            INNER JOIN Grades ON Subjects.ID_subject=Grades.ID_subject 
                            INNER JOIN Students ON Grades.ID_student=Students.ID_Student 
                            WHERE Students.ID_Student={current_student_ID}
                            GROUP BY Subjects.subject_name""") 
        
        mean_grades_for_student = np.array(self.cursor.fetchall())
        subject_names_short = [name[:3] for name in mean_grades_for_student[:,0]]

        self.mpl_widget_student_1.axis.clear()
        self.mpl_widget_student_1.axis.bar(subject_names_short, mean_grades_for_student[:,1].astype('float'), align='center', width=0.8, color="limegreen", edgecolor="lightgray", linewidth=0.7, zorder=3)
        self.mpl_widget_student_1.axis.grid(zorder=0)
        self.mpl_widget_student_1.axis.set(title="Średnie oceny dla poszczególnych przedmiotów",
                                           ylabel='Średnia ocen')
        self.mpl_widget_student_1.canvas.draw()
                            
        # Plot 2: number of grades, chosen subject
        ## get grades for current student and subject
        self.cursor.execute(f"""SELECT Grades.grade_value, COUNT(Grades.grade_value), Subjects.subject_name FROM Grades
                            INNER JOIN Students ON Students.ID_Student=Grades.ID_student
                            INNER JOIN Subjects ON Grades.ID_subject=Subjects.ID_subject
                            WHERE (Students.ID_Student={current_student_ID} AND Subjects.subject_name='{current_subject_name}')
                            GROUP BY Grades.grade_value""")
        grades_subject_list = np.array(self.cursor.fetchall())
        chosen_subject_name = grades_subject_list[0, 2]
        grades_list = grades_subject_list[:, 0:2]

        # Plot on PIE chart
        def make_autopct(total):
            def autopct_fun(pct):
                val = int(round(pct*total/100.0))
                return f'{val}'
            return autopct_fun
        
        values = grades_list[:, 1].astype('float')

        self.mpl_widget_student_2.axis.clear()
        self.mpl_widget_student_2.axis.pie(values, labels=grades_list[:, 0], explode=grades_list.shape[0]*[0.02], autopct=make_autopct(values.sum()),
                                           labeldistance=1.1, radius=1, textprops={'fontsize': 14})
        self.mpl_widget_student_2.axis.set(title=f'Liczba poszczególnych ocen z [{chosen_subject_name}]')
        self.mpl_widget_student_2.canvas.draw()

        # Plot 3: exams grades
        ## get exam grades for current student
        self.cursor.execute(f"""SELECT exam_grade_hum, exam_grade_mat, exam_grade_lang FROM Students
                            WHERE Students.ID_Student={current_student_ID}""")
        exam_grades_list = np.array(self.cursor.fetchall())[0]
        exam_names = ['Human.', 'Matemat.', 'Językowy']
        colors = ['greenyellow' if val >= 30 else 'orangered' for val in exam_grades_list]
        
        self.mpl_widget_student_3.axis.clear()
        bar_cont = self.mpl_widget_student_3.axis.barh(exam_names, exam_grades_list, align='center', height=0.8, color=colors, edgecolor="lightgray", linewidth=0.7, zorder=3)
        self.mpl_widget_student_3.axis.bar_label(bar_cont)
        self.mpl_widget_student_3.axis.grid(zorder=0)
        self.mpl_widget_student_3.axis.set(title="Wyniki egzaminów w [%]",
                                           xlim=(0, 100))
        self.mpl_widget_student_3.canvas.draw()


    def _refresh_from_teacher_teacher(self):
        self._prepare_teacher_subject_comboBox()
        self._prepare_teacher_class_comboBox()

    def _prepare_teacher_comboBox(self):
        # Get list of all teachers
        self.cursor.execute("SELECT ID_teacher, name, surname FROM Teachers ORDER BY name ASC, surname ASC")
        self.teachers_list = np.array(self.cursor.fetchall())

        # Make list of concatenated [name+surname]
        full_names_list = [f'{name} {surname}' for name, surname in self.teachers_list[:, 1:3]]

        # Prepare teacher comboBox
        self.input_comboBox_teacher_teacher.clear()
        self.input_comboBox_teacher_teacher.addItems(full_names_list)

    def _prepare_teacher_subject_comboBox(self):
        # Get current selected teacher ID
        comboBox_index = self.input_comboBox_teacher_teacher.currentIndex()
        current_teacher_ID = self.teachers_list[comboBox_index, 0]

        # Fetch all subjects for given teacher
        self.cursor.execute(f"""SELECT Subjects.ID_subject, Subjects.subject_name FROM Subjects
                            INNER JOIN Teachers ON Subjects.ID_teacher=Teachers.ID_teacher
                            WHERE Teachers.ID_teacher={current_teacher_ID}
                            ORDER BY subject_name ASC""")
        self.teacher_subjects_list = np.array(self.cursor.fetchall())
        
        # Make list of subject names
        subject_names_list = [f'{name}' for name in self.teacher_subjects_list[:, 1]]

        # Prepare subject comboBox
        self.input_comboBox_teacher_subject.clear()
        self.input_comboBox_teacher_subject.addItems(subject_names_list)

    def _prepare_teacher_class_comboBox(self):
        # Get current selected teacher ID
        comboBox_index = self.input_comboBox_teacher_teacher.currentIndex()
        current_teacher_ID = self.teachers_list[comboBox_index, 0]

        # Fetch all classes for given teacher
        self.cursor.execute(f"""SELECT Classes.ID_Class, Classes.Label FROM Classes
                            INNER JOIN Students ON Classes.ID_Class=Students.ID_Class
                            INNER JOIN Grades ON Students.ID_Student=Grades.ID_student
                            INNER JOIN Subjects ON Grades.ID_subject=Subjects.ID_subject
                            INNER JOIN Teachers ON Subjects.ID_teacher=Teachers.ID_teacher
                            WHERE Teachers.ID_teacher={current_teacher_ID}
                            GROUP BY Classes.Label
                            ORDER BY Classes.Label ASC""")
        self.teacher_class_list = np.array(self.cursor.fetchall())

        # Make list of class names
        class_names_list = [f'{name}' for name in self.teacher_class_list[:, 1]]

        # Prepare class comboBox
        self.input_comboBox_teacher_class.clear()
        self.input_comboBox_teacher_class.addItems(class_names_list)

    def _refresh_teacher_view(self):
        # Get chosen data
        ## Get current selected teache ID
        comboBox_index_aux = self.input_comboBox_teacher_teacher.currentIndex()
        current_teacher_ID = self.teachers_list[comboBox_index_aux, 0]
        # Get current selected subject ID
        comboBox_index_aux = self.input_comboBox_teacher_subject.currentIndex()
        current_subject_ID = self.teacher_subjects_list[comboBox_index_aux, 0]
        # Get current selected ID
        comboBox_index_aux = self.input_comboBox_teacher_class.currentIndex()
        current_class_ID = self.teacher_class_list[comboBox_index_aux, 0] 
        
        # Fetch students for given teacher, subject & class
        self.cursor.execute(f"""SELECT Students.name, Students.surname, AVG(Grades.grade_value), Students.graduated FROM Students
                            INNER JOIN Classes ON Classes.ID_Class=Students.ID_Class
                            INNER JOIN Grades ON Students.ID_Student=Grades.ID_student
                            INNER JOIN Subjects ON Grades.ID_subject=Subjects.ID_subject
                            INNER JOIN Teachers ON Subjects.ID_teacher=Teachers.ID_teacher
                            WHERE (Teachers.ID_teacher={current_teacher_ID} AND Subjects.ID_subject={current_subject_ID} AND Classes.ID_Class={current_class_ID})
                            GROUP BY Students.ID_Student
                            ORDER BY Students.name ASC, Students.surname ASC""")
        students_list = np.array(self.cursor.fetchall())

        # Plot 1: Number of graduated students
        graduated_data = [list(students_list[:,3]).count('tak'), list(students_list[:,3]).count('nie')]
        self.mpl_widget_teacher_1.axis.clear()
        self.mpl_widget_teacher_1.axis.pie(graduated_data, labels=['TAK', 'NIE'], explode=2*[0.05], autopct=lambda x: f'{x:.1f}%',
                                           labeldistance=1.1, radius=1, textprops={'fontsize': 14}, colors=['limegreen', 'chocolate'])
        self.mpl_widget_teacher_1.axis.set(title="Ukończenie szkoły przez uczniów wybranej klasy")
        self.mpl_widget_teacher_1.canvas.draw()

        # Text: Prepare text table for output
        out =  'Śr. ocen | Ukończył | Imię nazwisko\n'
        out += '---------|----------|---------------'
        for row in students_list:
            # date with time cut out
            name, surname, grades_mean, graduated = row
            out += f'\n {(grades_mean).astype("float"):^7.2f} | {graduated:^8} | {name} {surname}'
        ## Print to textBox
        self.plainTextEdit_teacher_students_list.setPlainText(out)



if __name__ == "__main__":
    import sys
    app = qtw.QApplication(sys.argv)
    
    ui_window = GUI_MainWindow()
    ui_window.show()

    sys.exit(app.exec_())
