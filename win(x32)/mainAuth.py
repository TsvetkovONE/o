import sys
from PyQt6 import QtWidgets
from auth import Ui_MainWindow
from db import Database
from mainAdmin import MainWindow as AdminWindow
from mainUser import MainApp


class AuthWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.db = Database()
        self.ui.pushButton.clicked.connect(self.login)

    def login(self):
        login = self.ui.loginEdit.text()
        password = self.ui.passwordEdit.text()

        if not login or not password:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Введите логин и пароль.")
            return

        try:
            query = "SELECT * FROM clients WHERE login = %s AND password = %s"
            result = self.db.execute_query(query, (login, password))

            if not result:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль.")
                return

            user = result[0]
            role_id = user["role_id"]

            if role_id == 2:
                self.admin_window = AdminWindow()
                self.admin_window.show()
                self.close()
            elif role_id == 1:
                self.user_window = MainApp(user_id=user['id'])
                self.user_window.show()
                self.close()
            else:
                QtWidgets.QMessageBox.information(self, "Инфо", "Неизвестная роль.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка при входе: {e}")


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = AuthWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
