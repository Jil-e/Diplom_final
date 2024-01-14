import configparser
import os
import sys
import time
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QListWidgetItem, QTableWidgetItem, QLabel, QListWidget, \
    QComboBox, QTableWidget, QSystemTrayIcon, QAction, qApp, QMenu, QStyle
from PyQt5.uic import loadUi
import connections
from datetime import datetime
import reqs
import operator
import bot
import hashlib
import sys, importlib


config = configparser.ConfigParser()
config_bot = configparser.ConfigParser()
config_request = configparser.ConfigParser()
config_hashes = configparser.ConfigParser()



class Login(QDialog):
    login_successful = pyqtSignal(str, str, str, str)

    def __init__(self):
        super(Login, self).__init__()
        loadUi("login_true.ui", self)
        self.loginbutton.clicked.connect(self.loginfunction)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.w = None
        self.setWindowTitle("Авторизация")
        self.status = self.findChild(QtWidgets.QLabel, "status")
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.host = self.findChild(QtWidgets.QLineEdit, "host")
        self.db_name = self.findChild(QtWidgets.QLineEdit, "db_name")
        self.login = self.findChild(QtWidgets.QLineEdit, "login")
        self.password = self.findChild(QtWidgets.QLineEdit, "password")
        self.setWindowFlags(
            Qt.Window |
            Qt.CustomizeWindowHint |
            Qt.WindowTitleHint |
            Qt.WindowCloseButtonHint
        )

    def loginfunction(self):
        global host,db_name,login,password
        host = self.host.text()
        db_name = self.db_name.text()
        login = self.login.text()
        password = self.password.text()
        if self.savedata.isChecked() and self.savedata_2.isChecked():
            print("Е")
            pass
        elif self.savedata.isChecked():
            try:
                cnx = connections.connection(host, db_name, login, password)
                if cnx.is_connected():
                    self.hide()
                    self.login_successful.emit(host, db_name, login, password)
                    self.w = MainWindow(host, db_name, login, password)
                    self.w.show()
                    with open("arguments.ini", "w") as f:
                        f.write(f"[FBS]\nhost = {host}"
                                f"\ndatabase = {db_name}"
                                f"\nlogin = {login}"
                                f"\npassword = {password}")
                        print(f"Данные верны для {login}")
                else:
                    self.status.setText(str("Ошибка подключения"))
            except Exception as ex:
                self.status.setText(str("Ошибка подключения"))
                print(ex)

        elif self.savedata_2.isChecked():
            config.read("arguments.ini")
            host = config["FBS"]["host"]
            db_name = config["FBS"]["database"]
            login = config["FBS"]["login"]
            password = config["FBS"]["password"]
            try:
                cnx = connections.connection(host, db_name, login, password)
                if cnx.is_connected():
                    self.hide()
                    self.login_successful.emit(host, db_name, login, password)
                    self.w = MainWindow(host, db_name, login, password)
                    self.w.show()
                    print("Подключение успешно")
                else:
                    self.status.setText(str("Ошибка подключения"))
            except Exception as ex:
                self.status.setText(str("Ошибка подключения"))
                print(ex)

        else:
            try:
                cnx = connections.connection(host, db_name, login, password)
                if cnx.is_connected():
                    self.hide()
                    self.login_successful.emit(host, db_name, login, password)
                    self.w = MainWindow(host, db_name, login, password)
                    self.w.show()
                else:
                    self.status.setText(str("Ошибка подключения"))
            except Exception as ex:
                self.status.setText(str("Ошибка подключения"))
                print(ex)

class MainWindow(QMainWindow):
    tray_icon = None
    def __init__(self, host, db_name, login, password):
        super(MainWindow, self).__init__()
        loadUi("main_true.ui", self)
        self.setWindowTitle("Конструктор запросов")
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.host = host
        self.db_name = db_name
        self.login = login
        self.password = password
        self.refresh.clicked.connect(self.refreshing)
        self.api_submit.clicked.connect(self.api_add)
        self.save_conf.clicked.connect(self.save_request)
        self.delete_req.clicked.connect(self.req_del)
        self.list.itemDoubleClicked.connect(self.coloms_show)
        self.list_2.itemDoubleClicked.connect(self.column_add)
        self.list_5.setWordWrap(True)
        self.start.clicked.connect(self.start_search)
        self.flag_search = False
        self.hash_1 = ' '
        self.hash_2 = ' '

        self.setWindowFlags(
            Qt.Window |
            Qt.CustomizeWindowHint |
            Qt.WindowTitleHint |
            Qt.WindowCloseButtonHint |
            Qt.WindowMinimizeButtonHint
        )
        if not os.path.isfile("bot_sets.ini"):
            with open("bot_sets.ini", "w") as f:
                f.write(f"[BFS]\napi = "
                        f"\nchat_id = ")
        else:
            config_bot.read("bot_sets.ini")
            if len(config_bot['BFS']['api']) and len(config_bot['BFS']['api']) != 0:
                self.api_submit.hide()
                self.api.hide()
                self.api_2.hide()
            else:
                api_data = config_bot['BFS']['api']
                chat_id = config_bot['BFS']['chat_id']
                print(len(api_data), len(chat_id))

        if not os.path.isfile("requests.ini"):
            with open("requests.ini", "w") as f:
                f.write(f"[RQST]\n")

        else:
            config_request.read("requests.ini")
            for i in range(len(config_request.options('RQST'))):
                if config_request['RQST'][f'{i}'] != '':
                    self.list_5.addItem(f"{i} = {config_request['RQST'][f'{i}']}")

        if not os.path.isfile("hashes.ini"):
            with open("hashes.ini", "w") as f:
                f.write(f"[HSH]\n")

    def refreshing(self):
        date = datetime.now()
        date = date.strftime('%Y-%m-%d %H:%M:%S')
        self.okno.clear()
        self.okno.setRowCount(0)
        self.okno.setColumnCount(0)
        self.console.clear()
        self.req_con.clear()
        self.list.clear()
        self.list_2.clear()
        host = self.host
        db_name = self.db_name
        login = self.login
        password = self.password
        self.console.append(f"{date} Используем '{host}',база данных '{db_name}', логин '{login}'")
        try:
            cnx = connections.connection(host, db_name, login, password)
            print("all good")
            with cnx.cursor() as cursor:
                cursor.execute(reqs.show_tables(db_name))
                data = cursor.fetchall()
                for row in data:
                    item = QListWidgetItem(str(format(*row)))
                    self.list.addItem(item)
        except Exception as ex:
            print(ex)

    def api_add(self):
        api = str(self.api.text())
        chat_id = str(self.api_2.text())
        if (len(api) or len(chat_id)) < 6:
            pass
        else:
            self.api.setEnabled(False)
            self.api_2.setEnabled(False)
            config_bot.read("bot_sets.ini")
            config_bot.set('BFS', 'api', str(api))
            config_bot.set('BFS', 'chat_id', str(chat_id))
            with open("bot_sets.ini", "w") as fp:
                config_bot.write(fp)

    def coloms_show(self):
        global name_table
        date = datetime.now()
        date = date.strftime('%Y-%m-%d %H:%M:%S')
        self.okno.clear()
        self.okno.setRowCount(0)
        self.okno.setColumnCount(0)
        self.list_2.clear()
        self.req_con.clear()
        name_table = self.list.currentItem()
        name_table = str(name_table.text())
        host = self.host
        db_name = self.db_name
        login = self.login
        password = self.password
        self.console.append(f"{date} Добавляем столбцы из базы данных {db_name}, table {name_table}")
        try:
            cnx = connections.connection(host, db_name, login, password)
            print("all good")
            with cnx.cursor() as cursor:
                cursor.execute(reqs.coloms(name_table))
                data = cursor.fetchall()
                first_data = map(operator.itemgetter(0), data)
                for row in first_data:
                    item = QListWidgetItem(str(row))
                    self.list_2.addItem(item)
        except Exception as ex:
            print(ex)

        if not self.checkBox.isChecked():
            self.req_con.insertPlainText(f"SELECT * FROM {name_table} WHERE")
        else:
            pass

    def column_add(self):
        global oper, column_name
        oper_list = ['=', '>=', '<=', '>', '<', '!=', 'LIKE', '!=']
        oper = QComboBox()
        oper.addItems(oper_list)
        date = datetime.now()
        date = date.strftime('%Y-%m-%d %H:%M:%S')

        if self.checkBox.isChecked():

            column_name = self.list_2.currentItem()
            column_name = column_name.text()
            count = self.okno.columnCount()
            self.okno.insertColumn(count)
            self.okno.setHorizontalHeaderItem(count, QTableWidgetItem(column_name))
            self.okno.setRowCount(2)
            self.okno.setCellWidget(0,count,oper)
            self.console.append(f"{date} Adding column {column_name} from table {name_table}, DB {db_name}")

        else:
            column_name = self.list_2.currentItem()
            column_name = column_name.text()
            self.req_con.insertPlainText(f" `{column_name}` ")




    def save_request(self):

        config_request.read("requests.ini")
        counter = len(config_request.options('RQST'))
        self.number = counter
        print(counter)
        if self.checkBox.isChecked():
            try:
                request = f"SELECT * FROM {name_table} WHERE "
                colcount = self.okno.columnCount()
                for column in range(colcount):
                    try:
                        col = self.okno.horizontalHeaderItem(column).text()
                        print(col)
                        exp = self.okno.cellWidget(0, column).currentText()
                        print(exp)
                        data = self.okno.item(1, column)
                        data_text = data.text()
                        print(data_text)
                        request = request + f"`{col}` {exp} '{data_text}' AND "


                    except Exception as ex:
                        self.console.append(str(ex))

                request_true = request[:-4]
                try:
                    cnx = connections.connection(host, db_name, login, password)
                    with cnx.cursor() as cursor:
                        if connections.validate(cursor,request_true) == True:
                            config_request.read("requests.ini")
                            config_request.set('RQST', f'{self.number}', str(request_true))
                            self.list_5.addItem(str(f"{self.number} = {request_true}"))
                            with open("requests.ini", "a") as myfile:
                                myfile.write(f'{self.number} = {str(request_true)}\n')

                            self.number += 1
                        else:
                            self.console.append("Запрос был построен неверно. Ошибка синтаксиса")


                except Exception as ex:
                    self.console.append(str(ex))


            except Exception as ex:
                self.console.append(str(ex))

        else:
            request_manual = self.req_con.toPlainText()
            try:
                cnx = connections.connection(host, db_name, login, password)
                with cnx.cursor() as cursor:
                    if connections.validate(cursor,request_manual) == True:
                        config_request.read("requests.ini")
                        config_request.set('RQST', f'{self.number}', str(request_manual))
                        self.list_5.addItem(str(f"{self.number} = {request_manual}"))
                        with open("requests.ini", "a") as myfile:
                             myfile.write(f'{self.number} = {str(request_manual)}\n')

                        self.number += 1

                    else:
                        self.console.append("Запрос был построен неверно. Ошибка синтаксиса")

            except Exception as ex:
                self.console.append(str(ex))

    def req_del(self):
        try:
            self.list_5.clear()
            with open("requests.ini", "w") as myfile:
                myfile.write("[RQST]\n")

            with open("hashes.ini", "w") as myfile_hash:
                myfile_hash.write("[HSH]\n")

            print("Удалили")


        except Exception as ex:
            print(ex)


    def start_search(self):
        config_bot.read("bot_sets.ini")
        config_hashes.read("hashes.ini")
        config_request.read("requests.ini")
        bot_data = config_bot["BFS"]["api"]
        bot_data_chat = config_bot["BFS"]['chat_id']
        counter = len(config_request.options('RQST'))

        if (config_bot["BFS"]["api"] or config_bot["BFS"]["chat_id"]) == '':
            self.console.append("Вы не ввели информацию об используемом боте. Без этих данных работа программы невозможна")
            pass

        elif config_request.has_option('RQST', "0") == False:
            self.console.append(
                "Нет созданного запроса для поиска. Создайте запрос с помощью конструктора или мануально")
            pass

        else:
            for i in range(counter):
                try:
                    cnx = connections.connection(host, db_name, login, password)
                    print("ищем чота")
                    with cnx.cursor() as cursor:
                        cursor.execute(config_request['RQST'][f'{i}'])
                        data = cursor.fetchall()
                    if data == "":
                        print("Каких-либо данных пока нет")
                        bot.send_error(bot_data, bot_data_chat)
                        pass
                    else:
                        h = hashlib.sha256(str(data).encode('utf-8')).hexdigest()
                        with open("hashes.ini", "a") as hashes:
                            hashes.write(f'{i} = {str(h)}\n')

                    print(i, h)

                except Exception as ex:
                    self.console.append(str(ex))
                    print(ex)


            tray_menu = QMenu()
            extaction = tray_menu.addAction("Завершить работу")
            extaction.triggered.connect(qApp.quit)
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
            self.tray_icon.show()
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
            self.tray_icon.showMessage(
                "Система мониторинга",
                "Программа была свернута в трей и начала наблюдение",
                QSystemTrayIcon.Information,
                2000
            )

            self.hide()
            config_hashes.read("hashes.ini")
            while True:
                for ite in range(counter):
                    try:
                        cnx = connections.connection(host, db_name, login, password)
                        with cnx.cursor() as cursor:
                            cursor.execute(config_request['RQST'][f'{ite}'])
                            data = cursor.fetchall()
                        if data == '':
                            print("Каких-либо данных пока нет")
                            pass
                        else:
                            h = hashlib.sha256(str(data).encode('utf-8')).hexdigest()

                    except Exception as ex:
                        print(ex)
                    time.sleep(5)

                    if str(h) != str(config_hashes["HSH"][f"{ite}"]):
                        bot.sending_m(ite, config_request['RQST'][f'{ite}'], bot_data,bot_data_chat)
                        print(config_hashes["HSH"][f"{ite}"], "!=", str(h))
                    else:
                        pass



if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Login()
    w.show()
    app.exec()

