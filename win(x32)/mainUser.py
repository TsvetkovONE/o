import sys
from PyQt6 import QtWidgets
from user import Ui_MainWindow
from busket import Ui_MainWindow as Ui_BasketWindow
from db import Database
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt

class BasketWindow(QtWidgets.QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.ui = Ui_BasketWindow()
        self.ui.setupUi(self)
        self.load_cart_data()
        self.ui.editButton.clicked.connect(self.enable_editing)
        self.ui.makeButton.clicked.connect(self.make_order)
        self.ui.orderButton.clicked.connect(self.show_orders)

    def load_cart_data(self):
        db = Database()
        try:
            cart_items = db.execute_query("""
                SELECT c.product_id, p.name, c.quantity, p.price*c.quantity as price
                FROM cart c 
                JOIN products p ON c.product_id = p.id
                WHERE c.client_id = %s
            """, (self.user_id,))

            self.ui.tableWidget.setRowCount(len(cart_items))
            self.ui.tableWidget.setColumnCount(3)
            self.ui.tableWidget.setHorizontalHeaderLabels(["Product", "Quantity", "Price"])
            self.cart_data = {}

            for row_idx, item in enumerate(cart_items):
                self.cart_data[row_idx] = item['product_id']
                self.ui.tableWidget.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(str(item['name'])))
                self.ui.tableWidget.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(str(item['quantity'])))
                self.ui.tableWidget.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(str(item['price'])))
        except Exception as e:
            print("Ошибка при загрузке корзины:", e)
        finally:
            db.close()

    def enable_editing(self):
        self.ui.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.AllEditTriggers)

        confirm = QtWidgets.QMessageBox.question(
            self, "Применить изменения", "Применить изменения в корзине?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if confirm == QtWidgets.QMessageBox.StandardButton.Yes:
            db = Database()
            try:
                for row in range(self.ui.tableWidget.rowCount()):
                    product_id = self.cart_data[row]
                    quantity_item = self.ui.tableWidget.item(row, 1)
                    if quantity_item is None:
                        continue
                    try:
                        quantity = int(quantity_item.text())
                        if quantity < 0:
                            raise ValueError
                    except ValueError:
                        QtWidgets.QMessageBox.warning(self, "Ошибка", f"Неверное количество в строке {row + 1}")
                        continue

                    if quantity == 0:
                        db.execute_query("DELETE FROM cart WHERE client_id = %s AND product_id = %s",
                                         (self.user_id, product_id))

                    else:
                        db.execute_query("""
                            UPDATE cart SET quantity = %s 
                            WHERE client_id = %s AND product_id = %s
                        """, (quantity, self.user_id, product_id))
                QtWidgets.QMessageBox.information(self, "Успех", "Корзина обновлена.")
                self.load_cart_data()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении корзины: {e}")
            finally:
                db.close()
        else:
            self.load_cart_data()

    def make_order(self):
        client_id = self.user_id
        db = Database()
        try:
            cart_items = db.execute_query("""
                SELECT product_id, quantity 
                FROM cart 
                WHERE client_id = %s
            """, (client_id,))

            if not cart_items:
                QtWidgets.QMessageBox.information(self, "Пусто", "Корзина пуста.")
                return

            db.execute_query("""
                INSERT INTO orders (client_id, status_id, order_date)
                VALUES (%s, %s, NOW())
            """, (client_id, 1))

            order_id = db.execute_query("SELECT LAST_INSERT_ID() AS id")[0]['id']

            for item in cart_items:
                product_id = item['product_id']
                quantity = item['quantity']
                product = db.execute_query("SELECT price FROM products WHERE id = %s", (product_id,))
                price = product[0]['price'] if product else 0.0

                db.execute_query("""
                    INSERT INTO order_items (order_id, product_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, product_id, quantity, price))

            db.execute_query("DELETE FROM cart WHERE client_id = %s", (client_id,))

            QtWidgets.QMessageBox.information(self, "Успех", "Заказ оформлен успешно!")
            self.load_cart_data()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось оформить заказ: {e}")
        finally:
            db.close()

    def show_orders(self):
        client_id = self.user_id
        db = Database()
        try:
            orders = db.execute_query("""
                SELECT o.id AS order_id, o.order_date, s.name AS status 
                FROM orders o
                JOIN statuses s ON o.status_id = s.id
                WHERE o.client_id = %s
                ORDER BY o.order_date DESC
            """, (client_id,))

            if not orders:
                QtWidgets.QMessageBox.information(self, "Нет заказов", "Вы еще не оформили ни одного заказа.")
                return

            self.ui.tableWidget.clear()
            self.ui.tableWidget.setRowCount(len(orders))
            self.ui.tableWidget.setColumnCount(3)
            self.ui.tableWidget.setHorizontalHeaderLabels(["ID заказа", "Дата заказа", "Статус"])

            for row, order in enumerate(orders):
                self.ui.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(str(order['order_id'])))
                self.ui.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(str(order['order_date'])))
                self.ui.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(order['status']))

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось получить список заказов: {e}")
        finally:
            db.close()


class MainApp(QtWidgets.QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.load_product_data()
        self.ui.basketButton.clicked.connect(self.open_basket_window)
        self.ui.infoButton.clicked.connect(self.show_product_info)
        self.ui.addButton.clicked.connect(self.add_to_cart)
        self.ui.backButton.clicked.connect(QtWidgets.QApplication.quit)
        self.ui.comboBox.addItem("Без сортировки")
        self.ui.comboBox.addItem("По возрастанию цены")
        self.ui.comboBox.addItem("По убыванию цены")
        self.ui.comboBox.currentIndexChanged.connect(self.load_product_data)

    def load_product_data(self):
        db = Database()
        try:
            sort_index = self.ui.comboBox.currentIndex()
            if sort_index == 1:
                query = "SELECT name, price, photo FROM products ORDER BY price ASC"
            elif sort_index == 2:
                query = "SELECT name, price, photo FROM products ORDER BY price DESC"
            else:
                query = "SELECT name, price, photo FROM products"

            products = db.execute_query(query)

            self.ui.tableWidget.setRowCount(len(products))
            self.ui.tableWidget.setColumnCount(3)
            self.ui.tableWidget.setHorizontalHeaderLabels(["Name", "Price", "Photo"])

            for row_idx, product in enumerate(products):
                self.ui.tableWidget.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(product['name']))
                self.ui.tableWidget.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(str(product['price'])))

                photo_data = product['photo']
                if photo_data:
                    pixmap = QPixmap()
                    pixmap.loadFromData(photo_data)
                    pixmap = pixmap.scaled(100, 100)

                    label = QLabel()
                    label.setPixmap(pixmap)
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    label.setFixedSize(100, 100)
                    self.ui.tableWidget.setCellWidget(row_idx, 2, label)
                    self.ui.tableWidget.setRowHeight(row_idx, 100)
                else:
                    self.ui.tableWidget.setItem(row_idx, 2, QtWidgets.QTableWidgetItem("Нет фото"))

        except Exception as e:
            print("Ошибка при загрузке товаров:", e)
        finally:
            db.close()

    def show_product_info(self):
        selected_row = self.ui.tableWidget.currentRow()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "Выбор товара", "Пожалуйста, выберите товар из таблицы.")
            return

        product_name = self.ui.tableWidget.item(selected_row, 0).text()

        db = Database()
        try:
            query = "SELECT description FROM products WHERE name = %s"
            result = db.execute_query(query, (product_name,))
            if result:
                description = result[0]['description']
                QtWidgets.QMessageBox.information(self, "Описание товара", description)
            else:
                QtWidgets.QMessageBox.information(self, "Описание товара", "Описание не найдено.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка при получении описания: {e}")
        finally:
            db.close()

    def add_to_cart(self):
        selected_row = self.ui.tableWidget.currentRow()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "Выбор товара", "Пожалуйста, выберите товар.")
            return

        product_name = self.ui.tableWidget.item(selected_row, 0).text()

        quantity, ok = QtWidgets.QInputDialog.getInt(self, "Количество",
                                                     f"Сколько '{product_name}' добавить в корзину?", 1, 1)
        if not ok:
            return

        db = Database()
        try:
            product = db.execute_query("SELECT id FROM products WHERE name = %s", (product_name,))
            if not product:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Товар не найден.")
                return
            product_id = product[0]['id']

            client_id = self.user_id

            db.execute_query("""
                INSERT INTO cart (client_id, product_id, quantity)
                VALUES (%s, %s, %s)
            """, (client_id, product_id, quantity))

            QtWidgets.QMessageBox.information(self, "Успех", "Товар добавлен в корзину!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось добавить товар в корзину: {e}")
        finally:
            db.close()

    def open_basket_window(self):
        self.basket_window = BasketWindow(self.user_id)
        self.basket_window.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
