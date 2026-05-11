"""
Example Qt client for the Webstore API.

Made with GitHub Copilot GPT-5 mini using simple prompts and iterative development.
"""
import sys
import requests

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget,
        QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QDialog,
        QFormLayout, QHBoxLayout, QHeaderView, QMessageBox, QStatusBar,
        QAbstractItemView, QLabel
    )
except ImportError:
    print('PySide6 is required to run this GUI. Install with: pip install PySide6')
    sys.exit(1)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.API_URL = "http://127.0.0.1:5000"
        self.setWindowTitle("Webstore Qt Client")
        self.resize(900, 600)
        # Subtle modern look: set a minimum size and style tweaks
        self.setMinimumSize(800, 480)
        QApplication.setStyle('Fusion')
        # Apply a light stylesheet to improve visual contrast
        qt_app = QApplication.instance()
        if qt_app is not None:
            qt_app.setStyleSheet(
                """
                QTableWidget { font-size: 13px; }
                QHeaderView::section { background: #f3f3f3; font-weight: 600; padding: 4px }
                QPushButton { padding: 6px 10px; border-radius: 4px }
                QPushButton:hover { background: #e6f2ff }
                QTabWidget::pane { border-top: 1px solid #ddd }
                """
            )

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Header / logo area
        header = QLabel('🛍️  Webstore')
        header.setStyleSheet('font-size:18px; font-weight:700; padding:8px 6px;')
        header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.layout.addWidget(header)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self._build_customers_tab()
        self._build_products_tab()
        self._build_orders_tab()

        self.setStatusBar(QStatusBar(self))
        self.auto_refresh()

    def _build_customers_tab(self):
        self.customer_tab = QWidget()
        self.customer_layout = QVBoxLayout(self.customer_tab)
        # toolbar-like layout for nicer look
        toolbar = QHBoxLayout()
        self.btn_refresh_customers = QPushButton('🔄 Refresh')
        self.btn_refresh_customers.setFixedWidth(110)
        self.btn_refresh_customers.clicked.connect(self.get_customers)
        self.btn_add_customer = QPushButton('➕ Add')
        self.btn_add_customer.setFixedWidth(90)
        self.btn_add_customer.clicked.connect(self.create_customer)
        self.btn_delete_customer = QPushButton('🗑️ Delete')
        self.btn_delete_customer.setFixedWidth(100)
        self.btn_delete_customer.clicked.connect(self.delete_customer)
        toolbar.addWidget(self.btn_refresh_customers)
        toolbar.addWidget(self.btn_add_customer)
        toolbar.addWidget(self.btn_delete_customer)
        toolbar.addStretch()

        self.customers_table = QTableWidget(0, 4)
        self.customers_table.setHorizontalHeaderLabels(['id','email','name','created_at'])
        # make tables more readable
        self.customers_table.setAlternatingRowColors(True)
        self.customers_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.customers_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.customers_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.customers_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.customers_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)

        self.customer_layout.addLayout(toolbar)
        self.customer_layout.addWidget(self.customers_table)
        self.tab_widget.addTab(self.customer_tab, 'Users')

    def _build_products_tab(self):
        self.products_tab = QWidget()
        self.products_layout = QVBoxLayout(self.products_tab)
        toolbar = QHBoxLayout()
        self.btn_refresh_products = QPushButton('🔄 Refresh')
        self.btn_refresh_products.setFixedWidth(110)
        self.btn_refresh_products.clicked.connect(self.get_products)
        self.btn_add_product = QPushButton('➕ Add')
        self.btn_add_product.setFixedWidth(90)
        self.btn_add_product.clicked.connect(self.create_product)
        self.btn_delete_product = QPushButton('🗑️ Delete')
        self.btn_delete_product.setFixedWidth(100)
        self.btn_delete_product.clicked.connect(self.delete_product)
        # Order from products view: opens place-order with this product pre-selected
        self.btn_order_product = QPushButton('🛒 Order')
        self.btn_order_product.setFixedWidth(100)
        self.btn_order_product.clicked.connect(self.order_from_selected_product)
        toolbar.addWidget(self.btn_refresh_products)
        toolbar.addWidget(self.btn_add_product)
        toolbar.addWidget(self.btn_delete_product)
        toolbar.addWidget(self.btn_order_product)
        toolbar.addStretch()

        self.products_table = QTableWidget(0, 5)
        self.products_table.setHorizontalHeaderLabels(['id','sku','name','price','stock'])
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.products_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.products_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.products_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.products_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.products_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)

        self.products_layout.addLayout(toolbar)
        self.products_layout.addWidget(self.products_table)
        self.tab_widget.addTab(self.products_tab, 'Products')

    def _build_orders_tab(self):
        self.orders_tab = QWidget()
        self.orders_layout = QVBoxLayout(self.orders_tab)
        toolbar = QHBoxLayout()
        self.btn_refresh_orders = QPushButton('🔄 Refresh')
        self.btn_refresh_orders.setFixedWidth(110)
        self.btn_refresh_orders.clicked.connect(self.get_orders)
        self.btn_place_order = QPushButton('🛒 Place Order')
        self.btn_place_order.setFixedWidth(120)
        self.btn_place_order.clicked.connect(self.place_order_dialog)
        self.btn_delete_order = QPushButton('🗑️ Delete')
        self.btn_delete_order.setFixedWidth(100)
        self.btn_delete_order.clicked.connect(self.delete_order)
        toolbar.addWidget(self.btn_refresh_orders)
        toolbar.addWidget(self.btn_place_order)
        toolbar.addWidget(self.btn_delete_order)
        toolbar.addStretch()

        self.orders_table = QTableWidget(0, 4)
        self.orders_table.setHorizontalHeaderLabels(['id','user_id','product_id','quantity'])
        self.orders_table.setAlternatingRowColors(True)
        self.orders_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.orders_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.orders_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.orders_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.orders_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)

        self.orders_layout.addLayout(toolbar)
        self.orders_layout.addWidget(self.orders_table)
        self.tab_widget.addTab(self.orders_tab, 'Orders')

    def auto_refresh(self):
        self.get_customers()
        self.get_products()
        self.get_orders()

    # ---------- Customers ----------
    def get_customers(self):
        self.statusBar().showMessage('Loading users...')
        try:
            r = requests.get(self.API_URL + '/api/users/', timeout=5)
            r.raise_for_status()
            data = r.json()
            users = data.get('users', [])
            self.customers_table.setRowCount(0)
            for u in users:
                row = self.customers_table.rowCount()
                self.customers_table.insertRow(row)
                self.customers_table.setItem(row, 0, QTableWidgetItem(str(u.get('id'))))
                self.customers_table.setItem(row, 1, QTableWidgetItem(u.get('email','')))
                self.customers_table.setItem(row, 2, QTableWidgetItem(u.get('name','')))
                self.customers_table.setItem(row, 3, QTableWidgetItem(str(u.get('created_at',''))))
        except requests.RequestException as e:
            self.statusBar().showMessage('Failed to load users', 5000)
            QMessageBox.critical(self, 'Error', f'Failed to get users: {e}')
        else:
            self.statusBar().showMessage('Users loaded', 2500)

    def create_customer(self):
        dlg = QDialog(self)
        dlg.setWindowTitle('Create user')
        layout = QFormLayout(dlg)
        email = QLineEdit(); name = QLineEdit()
        layout.addRow('email', email); layout.addRow('name', name)
        ok = QPushButton('💾 Save')
        ok.setFixedWidth(100)
        ok.setStyleSheet('background-color:#28a745; color:white; border-radius:4px')
        layout.addWidget(ok)
        ok.clicked.connect(lambda: self._create_customer_submit(dlg, email.text(), name.text()))
        dlg.exec()

    def _create_customer_submit(self, dlg, email, name):
        try:
            r = requests.post(self.API_URL + '/api/users/', json={'email': email, 'name': name}, timeout=5)
            if r.status_code == 201:
                dlg.accept(); self.get_customers(); QMessageBox.information(self, 'OK', 'User created')
            else:
                QMessageBox.warning(self, 'Fail', f'Create failed: {r.status_code} {r.text}')
        except requests.RequestException as e:
            QMessageBox.critical(self, 'Error', str(e))

    def delete_customer(self):
        sel = self.customers_table.selectionModel().selectedRows()
        if not sel: return
        row = sel[0].row(); user_id = self.customers_table.item(row,0).text()
        try:
            r = requests.delete(self.API_URL + f'/api/users/{user_id}/', timeout=5)
            if r.status_code == 204:
                QMessageBox.information(self, 'OK', 'Deleted'); self.get_customers()
            else:
                QMessageBox.warning(self, 'Fail', f'Delete failed: {r.status_code} {r.text}')
        except requests.RequestException as e:
            QMessageBox.critical(self, 'Error', str(e))

    # ---------- Products ----------
    def get_products(self):
        self.statusBar().showMessage('Loading products...')
        try:
            r = requests.get(self.API_URL + '/api/products/', timeout=5)
            r.raise_for_status()
            data = r.json()
            prods = data.get('products', [])
            self.products_table.setRowCount(0)
            for p in prods:
                row = self.products_table.rowCount()
                self.products_table.insertRow(row)
                self.products_table.setItem(row, 0, QTableWidgetItem(str(p.get('id'))))
                self.products_table.setItem(row, 1, QTableWidgetItem(p.get('sku','')))
                self.products_table.setItem(row, 2, QTableWidgetItem(p.get('product_name','')))
                self.products_table.setItem(row, 3, QTableWidgetItem(str(p.get('price',''))))
                self.products_table.setItem(row, 4, QTableWidgetItem(str(p.get('stock_quantity',''))))
        except requests.RequestException as e:
            self.statusBar().showMessage('Failed to load products', 5000)
            QMessageBox.critical(self, 'Error', f'Failed to get products: {e}')
        else:
            self.statusBar().showMessage('Products loaded', 2500)

    def create_product(self):
        dlg = QDialog(self)
        dlg.setWindowTitle('Create product')
        layout = QFormLayout(dlg)
        sku = QLineEdit(); name = QLineEdit(); price = QLineEdit(); stock = QLineEdit()
        layout.addRow('sku', sku); layout.addRow('name', name); layout.addRow('price', price); layout.addRow('stock', stock)
        ok = QPushButton('💾 Save')
        ok.setFixedWidth(100)
        ok.setStyleSheet('background-color:#007bff; color:white; border-radius:4px')
        layout.addWidget(ok)
        ok.clicked.connect(lambda: self._create_product_submit(dlg, sku.text(), name.text(), price.text(), stock.text()))
        dlg.exec()

    def _create_product_submit(self, dlg, sku, name, price, stock):
        try:
            r = requests.post(self.API_URL + '/api/products/', json={'sku': sku, 'product_name': name, 'price': float(price), 'stock_quantity': int(stock)}, timeout=5)
            if r.status_code == 201:
                dlg.accept(); self.get_products(); QMessageBox.information(self, 'OK', 'Product created')
            else:
                QMessageBox.warning(self, 'Fail', f'Create failed: {r.status_code} {r.text}')
        except requests.RequestException as e:
            QMessageBox.critical(self, 'Error', str(e))

    def delete_product(self):
        sel = self.products_table.selectionModel().selectedRows()
        if not sel: return
        row = sel[0].row(); pid = self.products_table.item(row,0).text()
        # Check for orders that reference this product first to avoid DB integrity errors
        try:
            r_orders = requests.get(self.API_URL + '/api/orders/', timeout=5)
            r_orders.raise_for_status()
            orders = r_orders.json().get('orders', [])
            for o in orders:
                # product_id may be int or string in responses
                if str(o.get('product_id')) == str(pid):
                    QMessageBox.warning(self, 'Cannot delete', 'This product is referenced by existing orders.\nDelete the related orders first.')
                    return
        except requests.RequestException:
            # If we cannot fetch orders, continue and let the server handle/return an error.
            pass

        try:
            r = requests.delete(self.API_URL + f'/api/products/{pid}/', timeout=5)
            if r.status_code == 204:
                QMessageBox.information(self, 'OK', 'Deleted'); self.get_products()
            else:
                # Try to show a useful message: prefer JSON, otherwise strip HTML and truncate
                msg = ''
                try:
                    data = r.json()
                    msg = data.get('message') or data.get('error') or str(data)
                except Exception:
                    import re
                    text = r.text or ''
                    # remove HTML tags (simple)
                    msg = re.sub(r'<[^>]+>', '', text).strip()
                    if len(msg) > 500:
                        msg = msg[:500] + '...'
                QMessageBox.warning(self, 'Fail', f'Delete failed: {r.status_code} {msg}')
        except requests.RequestException as e:
            QMessageBox.critical(self, 'Error', str(e))

    # ---------- Orders ----------
    def get_orders(self):
        self.statusBar().showMessage('Loading orders...')
        try:
            r = requests.get(self.API_URL + '/api/orders/', timeout=5)
            r.raise_for_status()
            data = r.json()
            orders = data.get('orders', [])
            self.orders_table.setRowCount(0)
            for o in orders:
                row = self.orders_table.rowCount()
                self.orders_table.insertRow(row)
                self.orders_table.setItem(row, 0, QTableWidgetItem(str(o.get('id'))))
                self.orders_table.setItem(row, 1, QTableWidgetItem(str(o.get('user_id'))))
                self.orders_table.setItem(row, 2, QTableWidgetItem(str(o.get('product_id'))))
                self.orders_table.setItem(row, 3, QTableWidgetItem(str(o.get('quantity'))))
        except requests.RequestException as e:
            self.statusBar().showMessage('Failed to load orders', 5000)
            QMessageBox.critical(self, 'Error', f'Failed to get orders: {e}')
        else:
            self.statusBar().showMessage('Orders loaded', 2500)

    def place_order_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle('Place order')
        layout = QFormLayout(dlg)
        user_id = QLineEdit(); product_id = QLineEdit(); qty = QLineEdit('1')
        layout.addRow('user_id', user_id); layout.addRow('product_id', product_id); layout.addRow('qty', qty)
        ok = QPushButton('💾 Save')
        ok.setFixedWidth(100)
        ok.setStyleSheet('background-color:#17a2b8; color:white; border-radius:4px')
        layout.addWidget(ok)
        ok.clicked.connect(lambda: self._place_order_submit(dlg, user_id.text(), product_id.text(), qty.text()))
        dlg.exec()

    def order_from_selected_product(self):
        """Open the place-order dialog with the selected product pre-filled."""
        sel = self.products_table.selectionModel().selectedRows()
        if not sel:
            QMessageBox.information(self, 'Info', 'Select a product first')
            return
        row = sel[0].row()
        pid_item = self.products_table.item(row, 0)
        if pid_item is None:
            QMessageBox.warning(self, 'Error', 'Selected row has no product id')
            return
        pid = pid_item.text()
        dlg = QDialog(self)
        dlg.setWindowTitle('Place order')
        layout = QFormLayout(dlg)
        user_id = QLineEdit(); product_id = QLineEdit(); qty = QLineEdit('1')
        product_id.setText(pid)
        layout.addRow('user_id', user_id); layout.addRow('product_id', product_id); layout.addRow('qty', qty)
        ok = QPushButton('💾 Save'); layout.addWidget(ok)
        ok.clicked.connect(lambda: self._place_order_submit(dlg, user_id.text(), product_id.text(), qty.text()))
        dlg.exec()

    def _place_order_submit(self, dlg, user_id, product_id, qty):
        try:
            r = requests.post(self.API_URL + '/api/orders/', json={'user_id': int(user_id), 'product_id': int(product_id), 'quantity': int(qty)}, timeout=5)
            if r.status_code == 201:
                dlg.accept(); self.get_orders(); QMessageBox.information(self, 'OK', 'Order placed')
            else:
                QMessageBox.warning(self, 'Fail', f'Place failed: {r.status_code} {r.text}')
        except requests.RequestException as e:
            QMessageBox.critical(self, 'Error', str(e))

    def delete_order(self):
        sel = self.orders_table.selectionModel().selectedRows()
        if not sel: return
        row = sel[0].row(); oid = self.orders_table.item(row,0).text()
        try:
            r = requests.delete(self.API_URL + f'/api/orders/{oid}/', timeout=5)
            if r.status_code == 204:
                QMessageBox.information(self, 'OK', 'Deleted'); self.get_orders()
            else:
                QMessageBox.warning(self, 'Fail', f'Delete failed: {r.status_code} {r.text}')
        except requests.RequestException as e:
            QMessageBox.critical(self, 'Error', str(e))


if __name__ == '__main__':
    app = QApplication([])
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
