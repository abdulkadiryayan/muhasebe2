import sqlite3
from pathlib import Path

class Database:
    def __init__(self):
        self.db_path = Path("database/muhasebe.db")
        self.db_path.parent.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        with open("database/schema.sql", "r", encoding="utf-8") as f:
            self.conn.executescript(f.read())
        self.conn.commit()

    def add_title(self, name):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO titles (name) VALUES (?)", (name,))
        self.conn.commit()
        return cursor.lastrowid

    def add_cash_owner(self, name):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO cash_owners (name) VALUES (?)", (name,))
        self.conn.commit()
        return cursor.lastrowid

    def add_transaction(self, data):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (
                title_id, cash_owner_id, date, company_name, 
                construction_group_id, description, expense,
                payment_received, check_received, check_given,
                apartment_sale, invoice_amount, quantity, unit_price
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['title_id'], data['cash_owner_id'], data['date'],
            data['company_name'], data['construction_group_id'],
            data['description'], data['expense'], data['payment_received'],
            data['check_received'], data['check_given'], data['apartment_sale'],
            data['invoice_amount'], data['quantity'], data['unit_price']
        ))
        self.conn.commit()
        return cursor.lastrowid

    def get_titles(self):
        cursor = self.conn.cursor()
        return cursor.execute("SELECT * FROM titles").fetchall()

    def get_cash_owners(self):
        cursor = self.conn.cursor()
        return cursor.execute("SELECT * FROM cash_owners").fetchall()

    def get_transactions(self, filters=None):
        cursor = self.conn.cursor()
        query = """
            SELECT t.*, ti.name as title_name, co.name as cash_owner_name
            FROM transactions t
            LEFT JOIN titles ti ON t.title_id = ti.id
            LEFT JOIN cash_owners co ON t.cash_owner_id = co.id
        """
        conditions = []
        params = []

        if filters:
            # Tarih aralığı filtresi
            if 'date_range' in filters:
                start_date, end_date = filters['date_range']
                conditions.append("t.date BETWEEN ? AND ?")
                params.extend([start_date, end_date])

            # Diğer filtreler
            for key, value in filters.items():
                if value is not None and key != 'date_range':
                    conditions.append(f"t.{key} = ?")
                    params.append(value)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY t.date DESC"  # En son tarihli işlemler üstte
        return cursor.execute(query, params).fetchall()

    def update_transaction(self, transaction_id, data):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE transactions SET
                title_id = ?, cash_owner_id = ?, date = ?,
                company_name = ?, construction_group_id = ?,
                description = ?, expense = ?, payment_received = ?,
                check_received = ?, check_given = ?, apartment_sale = ?,
                invoice_amount = ?, quantity = ?, unit_price = ?
            WHERE id = ?
        """, (
            data['title_id'], data['cash_owner_id'], data['date'],
            data['company_name'], data['construction_group_id'],
            data['description'], data['expense'], data['payment_received'],
            data['check_received'], data['check_given'], data['apartment_sale'],
            data['invoice_amount'], data['quantity'], data['unit_price'],
            transaction_id
        ))
        self.conn.commit()

    def delete_transaction(self, transaction_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        self.conn.commit()

    def get_transaction(self, transaction_id):
        cursor = self.conn.cursor()
        return cursor.execute("""
            SELECT t.*, ti.name as title_name, co.name as cash_owner_name
            FROM transactions t
            LEFT JOIN titles ti ON t.title_id = ti.id
            LEFT JOIN cash_owners co ON t.cash_owner_id = co.id
            WHERE t.id = ?
        """, (transaction_id,)).fetchone() 