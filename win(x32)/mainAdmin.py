import sys
from PyQt6 import QtWidgets, QtGui
from create import Ui_MainWindow
from db import Database
from PyQt6.QtCore import QSize, Qt, pyqtSignal
from product import Ui_MainWindow as Ui_ProductWindow


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.addButton.clicked.connect(self.open_add_product_window)
        self.db = Database()
        self.load_products()
        self.ui.orderButton_2.clicked.connect(self.show_orders)
        self.ui.orderButton.clicked.connect(self.enable_product_editing)
        self.ui.backButton.clicked.connect(self.close_application)
        self.ui.comboBox.currentTextChanged.connect(self.load_products)
        self.ui.deleteButton.clicked.connect(self.delete_selected_product)

    def load_products(self):
        sort_option = self.ui.comboBox.currentText()
        order_clause = ""

        if sort_option == "По возрастанию цены":
            order_clause = "ORDER BY p.price ASC"
        elif sort_option == "По убыванию цены":
            order_clause = "ORDER BY p.price DESC"
        query = f"""
            SELECT p.name, m.name AS material, p.price, p.photo
            FROM products p
            JOIN materials m ON p.material_id = m.id
            {order_clause}
            """
        products = self.db.execute_query(query)

        table = self.ui.tableWidget
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Название", "Материал", "Цена", "Фото"])
        table.setRowCount(len(products))

        for row_idx, product in enumerate(products):
            table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(product['name']))
            table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(product['material']))
            table.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(str(product['price'])))

            if product['photo']:
                image_data = product['photo']
                image = QtGui.QImage.fromData(image_data)
                pixmap = QtGui.QPixmap.fromImage(image).scaled(QSize(100, 100), Qt.AspectRatioMode.KeepAspectRatio)
                label = QtWidgets.QLabel()
                label.setPixmap(pixmap)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setCellWidget(row_idx, 3, label)
            else:
                table.setItem(row_idx, 3, QtWidgets.QTableWidgetItem("Нет"))

        table.resizeColumnsToContents()
        table.resizeRowsToContents()

    def delete_selected_product(self):
        table = self.ui.tableWidget
        selected_row = table.currentRow()

        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Выберите товар для удаления.")
            return

        name_item = table.item(selected_row, 0)
        material_item = table.item(selected_row, 1)

        if not name_item or not material_item:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Невозможно получить данные о товаре.")
            return

        name = name_item.text()
        material = material_item.text()

        confirm = QtWidgets.QMessageBox.question(
            self, "Подтверждение удаления",
            f"Удалить товар: {name} ({material})?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if confirm != QtWidgets.QMessageBox.StandardButton.Yes:
            return

        # Получаем ID материала
        material_result = self.db.execute_query(
            "SELECT id FROM materials WHERE name = %s", (material,))
        if not material_result:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Материал не найден.")
            return
        material_id = material_result[0]['id']

        product_result = self.db.execute_query(
            "SELECT id FROM products WHERE name = %s AND material_id = %s", (name, material_id))
        if not product_result:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Товар не найден в базе данных.")
            return
        product_id = product_result[0]['id']

        self.db.execute_query("DELETE FROM products WHERE id = %s", (product_id,))
        QtWidgets.QMessageBox.information(self, "Успех", "Товар удалён.")
        self.load_products()

    def open_add_product_window(self):
        self.product_window = ProductWindow(self.db)
        self.product_window.product_added.connect(self.load_products)
        self.product_window.show()

    def show_orders(self):
        self.orders_window = OrdersWindow(self.db)
        self.orders_window.show()

    def enable_product_editing(self):
        table = self.ui.tableWidget
        table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.AllEditTriggers)

        confirm = QtWidgets.QMessageBox.question(
            self, "Применить изменения", "Сохранить изменения в продуктах?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if confirm == QtWidgets.QMessageBox.StandardButton.Yes:
            try:
                for row in range(table.rowCount()):
                    name_item = table.item(row, 0)
                    material_item = table.item(row, 1)
                    price_item = table.item(row, 2)

                    if not (name_item and material_item and price_item):
                        continue

                    name = name_item.text()
                    material = material_item.text()
                    try:
                        price = float(price_item.text())
                    except ValueError:
                        QtWidgets.QMessageBox.warning(self, "Ошибка", f"Неверная цена в строке {row + 1}")
                        continue

                    material_result = self.db.execute_query(
                        "SELECT id FROM materials WHERE name = %s", (material,))
                    if not material_result:
                        QtWidgets.QMessageBox.warning(self, "Ошибка", f"Материал не найден в строке {row + 1}")
                        continue
                    material_id = material_result[0]['id']

                    product_result = self.db.execute_query(
                        """SELECT id FROM products WHERE name = %s AND material_id = %s""",
                        (name, material_id)
                    )
                    if not product_result:
                        continue
                    product_id = product_result[0]['id']

                    self.db.execute_query(
                        """UPDATE products SET name = %s, material_id = %s, price = %s WHERE id = %s""",
                        (name, material_id, price, product_id)
                    )

                QtWidgets.QMessageBox.information(self, "Успех", "Продукты обновлены.")
                self.load_products()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении: {e}")
        else:
            self.load_products()

    def close_application(self):
        confirm = QtWidgets.QMessageBox.question(
            self, "Выход", "Вы точно хотите выйти?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if confirm == QtWidgets.QMessageBox.StandardButton.Yes:
            QtWidgets.QApplication.quit()


class ProductWindow(QtWidgets.QMainWindow):
    product_added = pyqtSignal()

    def __init__(self, db):
        super().__init__()
        self.ui = Ui_ProductWindow()
        self.ui.setupUi(self)
        self.db = db
        self.load_materials()
        self.ui.pushButton.clicked.connect(self.add_product)

    def load_materials(self):
        query = "SELECT id, name FROM materials"
        materials = self.db.execute_query(query)

        self.material_map = {}
        for material in materials:
            name = material['name']
            mid = material['id']
            self.ui.matelialcomboBox.addItem(name)
            self.material_map[name] = mid

    def add_product(self):
        name = self.ui.nameEdit.text()
        material_name = self.ui.matelialcomboBox.currentText()
        material_id = self.material_map.get(material_name)
        price = self.ui.priceEdit.text()
        photo = self.ui.photoEdit.text()

        if not name or not price or not photo:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены")
            return

        try:
            price = float(price)
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Цена должна быть числом")
            return

        query = """
            INSERT INTO products (name, material_id, price, photo)
            VALUES (%s, %s, %s, %s)
        """
        self.db.execute_query(query, (name, material_id, price, photo))
        QtWidgets.QMessageBox.information(self, "Успех", "Продукт добавлен!")
        self.product_added.emit()
        self.close()

class OrdersWindow(QtWidgets.QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Список заказов")
        self.setGeometry(100, 100, 600, 400)

        self.table = QtWidgets.QTableWidget(self)
        self.table.setGeometry(10, 10, 580, 380)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Номер Заказа", "Клиент", "Дата", "Статус"])

        self.load_orders()

    def load_orders(self):
        query = """
            SELECT o.id AS order_id, clients.name, o.order_date, s.name AS status 
            FROM orders o
            JOIN statuses s ON o.status_id = s.id
            JOIN clients ON o.client_id = clients.id
            ORDER BY o.order_date DESC
        """
        orders = self.db.execute_query(query)

        self.table.setRowCount(len(orders)) 

        for row_idx, order in enumerate(orders):
            self.table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(str(order['order_id'])))
            self.table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(order['name']))
            self.table.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(str(order['order_date'])))
            self.table.setItem(row_idx, 3, QtWidgets.QTableWidgetItem(order['status']))

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
