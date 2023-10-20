import sys, os, re
from fractions import Fraction

from PyQt6.QtWidgets import QApplication, QMainWindow, QSizePolicy, QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMessageBox, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QRadioButton, QPushButton
from PyQt6.QtGui import QIcon, QFont, QPixmap, QMovie, QRegion, QColor

from window_for_gui import Ui_BeetManager
from widget_for_gui import Ui_WidgetSetConditions

from utils import *
from algorithms import Hungarian, Greedy, Thrifty, GreedyThrifty, ThriftyGreedy

import os
from datetime import datetime as dt

def parser(matrixStr):
    errorMessage = ""
    array = []
    array_str = []

    matrixStr = matrixStr.replace(',', ' ')
    matrixStr = re.sub(" +", " ", matrixStr)
    
    try:
        array = [[float(Fraction(x)) if not '.' in x else float(x) for x in line.split()] for line in matrixStr.split('\n')]
        array = [x for x in array if x]
        array_str = [[x for x in line.split()] for line in matrixStr.split('\n')]
        array_str = [x for x in array_str if x]
    except:
        errorMessage = "При обработке матрицы встретился неожиданный символ"
        return [errorMessage, []]

    if not len(array):
        errorMessage = "Задаваемая матрица не может быть пустой"
        return [errorMessage, []]
    
    if len(set(map(len, array))) != 1:
        errorMessage = "Количество элементов в строках матрицы обязано быть одинаковым"
        return [errorMessage, []]
    
    if not all(all(i > 0 for i in sublist) for sublist in array):
        errorMessage = "Все элементы матрицы обязаны быть строго положительными"
        return [errorMessage, []]
    
    return [errorMessage, array, array_str]

def is_digit(str):
    if str.isdigit():
       return True
    else:
        try:
            float(Fraction(str)) if '/' in str else float(str)
            return True
        except ValueError:
            return False
        except ZeroDivisionError:
            return False


def resource_path(relative):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative)
    else:
        return os.path.join(os.path.abspath("."), relative)

# Любой символ, кроме цифр, точек и слэшей
def remove_non_math_symbols(str):
    return re.sub(r"[^0-9./\-\s]", "", str)

def create_error_box(error_msg):
    msgBox = QMessageBox()
    msgBox.setWindowTitle("Ошибка запуска")
    msgBox.setText("Произошла ошибка обработки данных")
    msgBox.setInformativeText("Описание:\n" + error_msg)
    msgBox.exec()

def show_graph_results(result):
    ui.graph_frame = QFrame()
    ui.graph_frame.setWindowTitle("График")
    ui.graph_frame.setFrameShape(QFrame.Shape.StyledPanel)
    ui.graph_frame.setLineWidth(1)
    ui.graph_frame.resize(1000, 500)
    ui.graph_frame.show()
    ui.layout = QVBoxLayout(ui.graph_frame)

    ui.graph_figure = Plot(result)
    ui.canvas = FigureCanvas(ui.graph_figure)
    ui.canvas.updateGeometry()

    toolbar = NavigationToolbar(ui.canvas, BeetManager)

    ui.layout.addWidget(toolbar)
    ui.layout.addWidget(ui.canvas)
    
    def button_save_event():
        text = ""
        num_msg = 1
        _dir = 'calculation_results'
        if not os.path.exists(_dir):
            os.mkdir(_dir)
            text += "1) Была создана папка ./" + _dir + "\n"
            num_msg += 1
        path = _dir + '/relative_result_' + dt.now().strftime('%d_%m_%Y_%H_%M_%S')
        Save_to_file(result, path +'.txt')
        ui.graph_figure.savefig(path +'.png')
        msgBox = QMessageBox()
        msgBox.setWindowTitle("Сохранено!")
        info_text = "Графики и относительные погрешности были\n" + "сохранены в папку ./calculation_results"
        msgBox.setText(info_text)
        text += str(num_msg) + ") Был создан файл ./" + path +'.txt\n'
        text += str(num_msg + 1) + ") Был создан файл ./" + path +'.png\n'
        msgBox.setInformativeText(text)
        msgBox.exec()

    button = QPushButton("Сохранить результаты (текстовый файл с относительными погрешностями + графики)", ui.graph_frame)
    button.setFixedHeight(40)
    button.font().setPointSize(14)
    button.clicked.connect(button_save_event)
    ui.layout.addWidget(button)

def get_all_table_items_as_string(table_widget):
    items = ""
    for i in range(table_widget.rowCount()):
        row_items = []
        for j in range(table_widget.columnCount()):
            row_items.append(str(table_widget.item(i, j).text()))
        items += (' '.join(row_items) + '\n')
    return items

def deselect_table_items():
    ui.tableWidget.selectionModel().clear()

def clear_selected_items():
    flag = False
    for item in ui.tableWidget.selectedItems():
        if item.text() != "":
            item.setText("")
            flag = True
    deselect_table_items()
    if flag:
        global need_to_rewrite
        need_to_rewrite = True
        reset_highlighted_result()

def clear_table_elems():
    for i in range(ui.tableWidget.rowCount()):
        for j in range(ui.tableWidget.columnCount()):
            ui.tableWidget.setItem(i, j, QTableWidgetItem(""))

highlighted_result = []
last_selected = False
def reset_highlighted_result(point_of_exec = 0):
    global last_selected
    if point_of_exec == 1:
        last_selected = True
        pass
    else:
        last_selected = False
        global highlighted_result
        if len(highlighted_result):
            col = 0
            for row in highlighted_result:
                ui.tableWidget.item(row, col).setBackground(QColor(255, 255, 255))
                col += 1
            ui.line_for_output_results_tab2.setText("не определена")
            highlighted_result = []

def cell_changed_action():
    if last_selected == True:
        reset_highlighted_result(2)
    global need_to_rewrite
    need_to_rewrite = True

def cosmetic_clear():
    reset_highlighted_result()
    deselect_table_items()

def radio_button_click_action():
    cosmetic_clear()

need_to_rewrite = True
def rewrite_table(array):
    global need_to_rewrite
    need_to_rewrite = False
    clear_table_elems()
    for i in range(len(array)):
        for j in range(len(array[0])):
            item = QTableWidgetItem(str(array[i][j]))
            ui.tableWidget.setItem(i, j, item)

# В vec запиcываются основные переменные, содержащиеся в tab1
vec = []
vec_names = ["Значение размера n",
             "Значение a слева", "Значение a справа",
             "Значение b слева", "Значение b справа",
             "Значение K слева", "Значение K справа",
             "Значение Na слева", "Значение Na справа",
             "Значение N слева", "Значение N справа"]

vecCond_names = ["Количество опытов",
                 "Доля жадности",
                 "Доля бережливости"]

def button_to_go_count_handler():
    # Сбор содержимого из QLineEdit
    vec.append(remove_non_math_symbols(ui.line_get_n_2.text()))
    vec.append(remove_non_math_symbols(ui.line_get_a_left_2.text()))
    vec.append(remove_non_math_symbols(ui.line_get_a_right_2.text()))
    vec.append(remove_non_math_symbols(ui.line_get_b_left_2.text()))
    vec.append(remove_non_math_symbols(ui.line_get_b_right_2.text()))
    vec.append(remove_non_math_symbols(ui.line_get_K_left_2.text()))
    vec.append(remove_non_math_symbols(ui.line_get_K_right_2.text()))
    vec.append(remove_non_math_symbols(ui.line_get_Na_left_2.text()))
    vec.append(remove_non_math_symbols(ui.line_get_Na_right_2.text()))
    vec.append(remove_non_math_symbols(ui.line_get_N_left_2.text()))
    vec.append(remove_non_math_symbols(ui.line_get_N_right_2.text()))
    ui.line_get_n_2.setText(vec[0])
    ui.line_get_a_left_2.setText(vec[1])
    ui.line_get_a_right_2.setText(vec[2])
    ui.line_get_b_left_2.setText(vec[3])
    ui.line_get_b_right_2.setText(vec[4])
    ui.line_get_K_left_2.setText(vec[5])
    ui.line_get_K_right_2.setText(vec[6])
    ui.line_get_Na_left_2.setText(vec[7])
    ui.line_get_Na_right_2.setText(vec[8])
    ui.line_get_N_left_2.setText(vec[9])
    ui.line_get_N_right_2.setText(vec[10])
    # Вспомогательные переменные
    error_msg = ""
    num_err = 0

    # Проверка учтена ли неорганика
    end_iter = 5
    for i in range(5, 11):
        if vec[i] == "":
            vec[i] = "0"
        else:
            end_iter = 11

    # Цикл обработки ошибок
    for i in range(0, end_iter):
        if not is_digit(vec[i]):
            num_err += 1
            error_msg += str(num_err) + ") " + vec_names[i] + " обязано быть числом\n"
            continue
        if float(Fraction(vec[i])) <= 0:
            num_err += 1
            error_msg += str(num_err) + ") " + vec_names[i] + " обязано быть положительным\n"
        if i == 0:
            if not vec[0].find(".") == -1 or not vec[0].find("/") == -1:
                num_err += 1
                error_msg += str(num_err) + ") " + vec_names[i] + " обязано быть целым числом\n"
            continue
        if i == 3 or i == 4:
            if float(Fraction(vec[i])) > 1.0:
                num_err += 1
                error_msg += str(num_err) + ") " + vec_names[i] + " обязано быть меньше 1\n"
        if i % 2 == 0:
            if is_digit(vec[i - 1]) and float(Fraction(vec[i])) < float(Fraction(vec[i - 1])):
                num_err += 1
                error_msg += str(num_err) + ") " + vec_names[i] + " обязано быть больше чем значение слева\n"

    if not (ui.checkBox_1_Hungarian_min_2.isChecked() or
        ui.checkBox_2_Hungarian_max_2.isChecked() or
        ui.checkBox_3_Greedy_2.isChecked() or
        ui.checkBox_4_Thrifty_2.isChecked() or
        ui.checkBox_5_Greedy_Thrifty_2.isChecked() or
        ui.checkBox_6_Thrifty_Greedy_2.isChecked()):
        num_err += 1
        error_msg += str(num_err) + ") Не выбран ни один алгоритм\n"

    if error_msg != "":
        vec.clear()
        create_error_box(error_msg)
    else:
        set_params(int(vec[0]), float(Fraction(vec[1])), float(Fraction(vec[2])), float(Fraction(vec[3])), float(Fraction(vec[4])))
        set_minerals(float(Fraction(vec[5])), float(Fraction(vec[6])), float(Fraction(vec[7])), float(Fraction(vec[8])), float(Fraction(vec[9])), float(Fraction(vec[10])))
        vec.clear()
        ui.Form = QtWidgets.QWidget()
        ui.widget = Ui_WidgetSetConditions()
        ui.widget.setupUi(ui.Form)
        ui.widget.line_get_num_exp.setPlaceholderText("Положительное число")
        ui.widget.line_get_share_of_greed.setPlaceholderText("Для Жадно-Бережливого алгоритма (0 < x < 1)")
        ui.widget.line_get_share_of_thrift.setPlaceholderText("Для Бережливо-Жадного алгоритма (0 < x < 1)")
        if not ui.checkBox_5_Greedy_Thrifty_2.isChecked():
            ui.widget.line_get_share_of_greed.setReadOnly(True)
            ui.widget.line_get_share_of_greed.setStyleSheet("QLineEdit { color: black; background-color: lightgray;}")
        if not ui.checkBox_6_Thrifty_Greedy_2.isChecked():
            ui.widget.line_get_share_of_thrift.setReadOnly(True)
            ui.widget.line_get_share_of_thrift.setStyleSheet("QLineEdit { color: black; background-color: lightgray;}")
        
        vecCond = []
        def button_to_set_condition_handler():
            vecCond.append(ui.widget.line_get_num_exp.text())
            vecCond.append(ui.widget.line_get_share_of_greed.text())
            vecCond.append(ui.widget.line_get_share_of_thrift.text())
            error_msg = ""
            num_err = 0
            if not is_digit(vecCond[0]):
                num_err += 1
                error_msg += str(num_err) + ") " + vecCond_names[0] + " обязано быть числом\n"
            elif not vecCond[0].find(".") == -1:
                num_err += 1
                error_msg += str(num_err) + ") " + vecCond_names[0] + " обязано быть целым числом\n"
            elif int(vecCond[0]) <= 0:
                num_err += 1
                error_msg += str(num_err) + ") " + vecCond_names[0] + " обязано быть положительным числом\n"

            if not is_digit(vecCond[1]):
                if ui.widget.line_get_share_of_greed.isReadOnly() == False:
                    num_err += 1
                    error_msg += str(num_err) + ") " + vecCond_names[1] + " обязана быть числом\n"
            elif float(vecCond[1]) < 0.0 or float(vecCond[1]) > 1.0:
                num_err += 1
                error_msg += str(num_err) + ") " + vecCond_names[1] + " обязана быть больше 0 и меньше 1\n"

            if not is_digit(vecCond[2]):
                if ui.widget.line_get_share_of_thrift.isReadOnly() == False:
                    num_err += 1
                    error_msg += str(num_err) + ") " + vecCond_names[2] + " обязана быть числом\n"
            elif float(vecCond[2]) < 0.0 or float(vecCond[2]) > 1.0:
                num_err += 1
                error_msg += str(num_err) + ") " + vecCond_names[2] + " обязана быть больше 0 и меньше 1\n"

            if error_msg != "":
                vecCond.clear()
                create_error_box(error_msg)
            else:
                algos = []
                if ui.checkBox_1_Hungarian_min_2.isChecked():
                    algos.append(("Венгерский min", Hungarian, {'mode': 'min'}))
                if ui.checkBox_2_Hungarian_max_2.isChecked():
                    algos.append(("Венгерский max", Hungarian, {'mode': 'max'}))
                if ui.checkBox_3_Greedy_2.isChecked():
                    algos.append(('Жадный', Greedy, {}))
                if ui.checkBox_4_Thrifty_2.isChecked():
                    algos.append(('Бережливый', Thrifty, {}))
                if ui.checkBox_5_Greedy_Thrifty_2.isChecked():
                    algos.append(('Жадно-Бережливый', GreedyThrifty, {'p': float(vecCond[1])}))
                if ui.checkBox_6_Thrifty_Greedy_2.isChecked():
                    algos.append(('Бережливо-Жадный', ThriftyGreedy, {'p': float(vecCond[2])}))
                
                matr_count = int(vecCond[0])
                vecCond.clear()
                matr = (get_matrix() for i in range(matr_count))
                n = get_n()

                results = Benchmark(matr, matr_count, np.zeros(n), algos)
                show_graph_results(results)

                ui.Form.close()

        ui.widget.button_to_set_condition.clicked.connect(button_to_set_condition_handler)
        ui.Form.show()

def button_to_go_count_tab2_handler():
    deselect_table_items()
    matrix_str = get_all_table_items_as_string(ui.tableWidget)
    matrix_str = remove_non_math_symbols(matrix_str)
    # print(matrix_str)
    res = parser(matrix_str)
    error_msg = res[0]
    if not error_msg and len(res[1]) != len(res[1][0]):
        error_msg = "Задаваемая матрица обязана быть квадратной"
    if error_msg != "":
        if error_msg == "Задаваемая матрица не может быть пустой":
            clear_table_elems()
        create_error_box(error_msg)
    else:
        algo = None
        if ui.radioButton_1_Hungarian_min_tab2.isChecked():
            algo = ("Венгерский min", Hungarian, {'mode': 'min'})
        if ui.radioButton_2_Hungarian_max_tab2.isChecked():
            algo = ("Венгерский max", Hungarian, {'mode': 'max'})
        if ui.radioButton_3_Greedy_tab2.isChecked():
            algo = ('Жадный', Greedy, {})
        if ui.radioButton_4_Thrifty_tab2.isChecked():
            algo = ('Бережливый', Thrifty, {})

        if ui.radioButton_5_Greedy_Thrifty_tab2.isChecked():
            tmp_str = ui.line_get_share_of_greed_tab2.text()
            if not is_digit(tmp_str):
                error_msg = vecCond_names[1] + " обязана быть числом\n"
            elif float(Fraction(tmp_str)) < 0.0 or float(Fraction(tmp_str)) > 1.0:
                error_msg = vecCond_names[1] + " обязана быть больше 0 и меньше 1\n"
            else:
                algo = ('Жадно-Бережливый', GreedyThrifty, {'p': float(Fraction(tmp_str))})

        if ui.radioButton_6_Thrifty_Greedy_tab2.isChecked():
            tmp_str = ui.line_get_share_of_thrift_tab2.text()
            if not is_digit(tmp_str):
                error_msg = vecCond_names[2] + " обязана быть числом\n"
            elif float(Fraction(tmp_str)) < 0.0 or float(Fraction(tmp_str)) > 1.0:
                error_msg = vecCond_names[2] + " обязана быть больше 0 и меньше 1\n"
            else:
                algo = ('Бережливо-Жадный', ThriftyGreedy, {'p': float(Fraction(tmp_str))})

        if error_msg != "":
            create_error_box(error_msg)
        elif algo is None:
            create_error_box("Не выбран ни один алгоритм")
        else:
            global need_to_rewrite
            if need_to_rewrite:
                rewrite_table(res[2])
            deselect_table_items()
            # Матрица P (P[i] - i-ый день)
            P = np.array(res[1]).T

            i, j = algo[1](P, **algo[2])
            
            global highlighted_result
            highlighted_result = j
            
            col = 0
            for row in j:
                ui.tableWidget.item(row, col).setBackground(QColor(3, 172, 19))
                col += 1

            res = P[i, j].sum()
            sum_text = ''
            for x in P[i, j]:
                sum_text += str(round(x,2)) + ' + '
            sum_text = sum_text[0:-2] + '= ' + str(round(res, 2))

            ui.line_for_output_results_tab2.setText(sum_text)
        
app = QtWidgets.QApplication(sys.argv)
qss = """ 
QTabBar::tab:selected  { color: white; background-color: rgb(0, 114, 187); }  
QTabBar::tab:!selected { color: black; background-color: rgb(220, 220, 220); }
"""
app.setStyleSheet(qss)
app.setWindowIcon(QtGui.QIcon(QPixmap(resource_path('beet.png'))))
BeetManager = QtWidgets.QMainWindow()
ui = Ui_BeetManager()
ui.setupUi(BeetManager)
ui.button_to_go_count.clicked.connect(button_to_go_count_handler)
ui.button_to_go_count_tab2.clicked.connect(button_to_go_count_tab2_handler)
ui.button_to_clear_selected_items.clicked.connect(clear_selected_items)
ui.tableWidget.cellPressed.connect(lambda : reset_highlighted_result(1))
ui.tableWidget.cellChanged.connect(cell_changed_action)
ui.radioButton_1_Hungarian_min_tab2.toggled.connect(radio_button_click_action)
ui.radioButton_2_Hungarian_max_tab2.toggled.connect(radio_button_click_action)
ui.radioButton_3_Greedy_tab2.toggled.connect(radio_button_click_action)
ui.radioButton_4_Thrifty_tab2.toggled.connect(radio_button_click_action)
ui.radioButton_5_Greedy_Thrifty_tab2.toggled.connect(radio_button_click_action)
ui.radioButton_6_Thrifty_Greedy_tab2.toggled.connect(radio_button_click_action)
ui.line_get_share_of_greed_tab2.textChanged.connect(cosmetic_clear)
ui.line_get_share_of_thrift_tab2.textChanged.connect(cosmetic_clear)
ui.line_get_K_left_2.setPlaceholderText("0")
ui.line_get_K_right_2.setPlaceholderText("0")
ui.line_get_Na_left_2.setPlaceholderText("0")
ui.line_get_Na_right_2.setPlaceholderText("0")
ui.line_get_N_left_2.setPlaceholderText("0")
ui.line_get_N_right_2.setPlaceholderText("0")
ui.line_get_share_of_greed_tab2.setPlaceholderText("Для Жадно-Бережливого алгоритма")
ui.line_get_share_of_thrift_tab2.setPlaceholderText("Для Бережливо-Жадного алгоритма")
ui.logo_box_1.setPixmap(QPixmap(resource_path('unn_logo_ru.png')).scaled(40, 45))
ui.logo_box_2.setPixmap(QPixmap(resource_path('unn_logo_ru.png')).scaled(40, 45))
ui.tabWidget.setStyleSheet("border-color: 1px solid rgb(0, 114, 187);")
ui.frame_decoration_1.setStyleSheet("background-color: rgb(0, 114, 187);")
ui.frame_decoration_2.setStyleSheet("background-color: rgb(0, 114, 187);")
ui.button_to_go_count.setStyleSheet("color: white; background-color: rgb(0, 114, 187);")
ui.button_to_go_count_tab2.setStyleSheet("color: white; background-color: rgb(0, 114, 187);")
ui.text_unit_1.setStyleSheet("font: bold; color: rgb(0, 114, 187);")
ui.text_unit_2.setStyleSheet("font: bold; color: rgb(0, 114, 187);")
ui.text_choice_of_algs.setStyleSheet("font: bold; color: rgb(0, 114, 187);")
ui.text_choice_of_algs_2.setStyleSheet("font: bold; color: rgb(0, 114, 187);")
ui.text_info_params_2.setStyleSheet("font: bold; color: rgb(0, 114, 187);")
ui.text_total_cost_tab2.setStyleSheet("font: bold; color: rgb(0, 114, 187);")
ui.line_for_output_results_tab2.setStyleSheet("font: bold;")
ui.tableWidget.horizontalHeader().hide()
ui.tableWidget.verticalHeader().hide()
header = ui.tableWidget.horizontalHeader()
for i in range(ui.tableWidget.columnCount()):
    header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
clear_table_elems() # to set type as string for every elem
BeetManager.show()
sys.exit(app.exec())
