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
        query = """
            INSERT INTO transactions (
                title_id, cash_owner_id, construction_group_id, date, company_name, description,
                expense, payment_received, check_received, check_given,
                apartment_sale, invoice_amount, quantity, unit_price
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # İnşaat grubu adını ekle veya mevcut olanı bul
        construction_group_name = data.get('construction_group', '')
        construction_group_id = None
        if construction_group_name:
            cursor = self.conn.cursor()
            # Önce var mı diye kontrol et
            result = cursor.execute("SELECT id FROM construction_groups WHERE name = ?", 
                                  (construction_group_name,)).fetchone()
            if result:
                construction_group_id = result['id']
            else:
                # Yoksa yeni ekle
                cursor.execute("INSERT INTO construction_groups (name) VALUES (?)", 
                             (construction_group_name,))
                construction_group_id = cursor.lastrowid
        
        params = [
            data['title_id'],
            data['cash_owner_id'],
            construction_group_id,  # İnşaat grubu ID'si
            data['date'],
            data['company_name'],
            data['description'],
            data['expense'],
            data['payment_received'],
            data['check_received'],
            data['check_given'],
            data['apartment_sale'],
            data['invoice_amount'],
            data['quantity'],
            data['unit_price']
        ]
        
        self.execute_query(query, params)

    def get_titles(self):
        cursor = self.conn.cursor()
        return cursor.execute("SELECT * FROM titles").fetchall()

    def get_cash_owners(self):
        cursor = self.conn.cursor()
        return cursor.execute("SELECT * FROM cash_owners").fetchall()

    def get_transactions(self, filters=None):
        query = """
            SELECT t.*, 
                   title.name as title_name, 
                   cash_owner.name as cash_owner_name,
                   cg.name as construction_group_name
            FROM transactions t
            LEFT JOIN titles title ON t.title_id = title.id
            LEFT JOIN cash_owners cash_owner ON t.cash_owner_id = cash_owner.id
            LEFT JOIN construction_groups cg ON t.construction_group_id = cg.id
            WHERE 1=1
        """
        params = []

        if filters:
            if 'date_range' in filters:
                start_date, end_date = filters['date_range']
                query += " AND date BETWEEN ? AND ?"
                params.extend([start_date, end_date])
            
            if 'title_id' in filters:
                query += " AND title_id = ?"
                params.append(filters['title_id'])
            
            if 'cash_owner_id' in filters:
                query += " AND cash_owner_id = ?"
                params.append(filters['cash_owner_id'])

        query += " ORDER BY date DESC"
        
        return self.execute_query(query, params)

    def update_transaction(self, transaction_id, data):
        # İnşaat grubu güncelleme
        construction_group_name = data.get('construction_group', '')
        construction_group_id = None
        if construction_group_name:
            cursor = self.conn.cursor()
            result = cursor.execute("SELECT id FROM construction_groups WHERE name = ?", 
                                  (construction_group_name,)).fetchone()
            if result:
                construction_group_id = result['id']
            else:
                cursor.execute("INSERT INTO construction_groups (name) VALUES (?)", 
                             (construction_group_name,))
                construction_group_id = cursor.lastrowid

        query = """
            UPDATE transactions SET
                title_id = ?,
                cash_owner_id = ?,
                construction_group_id = ?,
                date = ?,
                company_name = ?,
                description = ?,
                expense = ?,
                payment_received = ?,
                check_received = ?,
                check_given = ?,
                apartment_sale = ?,
                invoice_amount = ?,
                quantity = ?,
                unit_price = ?
            WHERE id = ?
        """
        params = [
            data['title_id'],
            data['cash_owner_id'],
            construction_group_id,
            data['date'],
            data['company_name'],
            data['description'],
            data['expense'],
            data['payment_received'],
            data['check_received'],
            data['check_given'],
            data['apartment_sale'],
            data['invoice_amount'],
            data['quantity'],
            data['unit_price'],
            transaction_id
        ]
        
        self.execute_query(query, params)

    def delete_transaction(self, transaction_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        self.conn.commit()

    def get_transaction(self, transaction_id):
        cursor = self.conn.cursor()
        return cursor.execute("""
            SELECT t.*, 
                   ti.name as title_name, 
                   co.name as cash_owner_name,
                   cg.name as construction_group_name
            FROM transactions t
            LEFT JOIN titles ti ON t.title_id = ti.id
            LEFT JOIN cash_owners co ON t.cash_owner_id = co.id
            LEFT JOIN construction_groups cg ON t.construction_group_id = cg.id
            WHERE t.id = ?
        """, (transaction_id,)).fetchone()

    def get_construction_groups(self):
        cursor = self.conn.cursor()
        return cursor.execute("SELECT * FROM construction_groups").fetchall()

    def add_construction_group(self, name):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO construction_groups (name) VALUES (?)", (name,))
        self.conn.commit()
        return cursor.lastrowid 

    def execute_query(self, query, params):
        cursor = self.conn.cursor()
        return cursor.execute(query, params).fetchall() 

    def delete_title(self, title_id):
        cursor = self.conn.cursor()
        # Önce bu başlığa ait işlemleri kontrol et
        transactions = cursor.execute("SELECT COUNT(*) as count FROM transactions WHERE title_id = ?", 
                                    (title_id,)).fetchone()
        if transactions['count'] > 0:
            raise Exception("Bu başlığa ait işlemler bulunmaktadır. Önce işlemleri silmelisiniz.")
        
        cursor.execute("DELETE FROM titles WHERE id = ?", (title_id,))
        self.conn.commit()

    def delete_cash_owner(self, cash_owner_id):
        cursor = self.conn.cursor()
        # Önce bu kasa sahibine ait işlemleri kontrol et
        transactions = cursor.execute("SELECT COUNT(*) as count FROM transactions WHERE cash_owner_id = ?", 
                                    (cash_owner_id,)).fetchone()
        if transactions['count'] > 0:
            raise Exception("Bu kasa sahibine ait işlemler bulunmaktadır. Önce işlemleri silmelisiniz.")
        
        cursor.execute("DELETE FROM cash_owners WHERE id = ?", (cash_owner_id,))
        self.conn.commit() 