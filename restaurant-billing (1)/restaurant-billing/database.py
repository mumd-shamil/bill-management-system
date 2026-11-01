"""
database.py
Handles SQLite connection and schema creation for the Restaurant Billing System.
"""

import sqlite3
import os

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "restaurant.db")


def get_connection():
    """Return a new SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all required tables if they do not already exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'cashier'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            price REAL NOT NULL,
            is_veg INTEGER NOT NULL DEFAULT 1,
            available INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS dining_tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_no TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL DEFAULT 'Available' CHECK(status IN ('Available', 'Occupied'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_no TEXT UNIQUE NOT NULL,
            table_id INTEGER,
            order_type TEXT NOT NULL DEFAULT 'Dine-in',
            subtotal REAL NOT NULL,
            tax_percent REAL NOT NULL,
            tax_amount REAL NOT NULL,
            discount_percent REAL NOT NULL DEFAULT 0,
            discount_amount REAL NOT NULL DEFAULT 0,
            total REAL NOT NULL,
            payment_mode TEXT NOT NULL DEFAULT 'Cash',
            amount_received REAL NOT NULL DEFAULT 0,
            balance_returned REAL NOT NULL DEFAULT 0,
            cashier TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (table_id) REFERENCES dining_tables(id) ON DELETE SET NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bill_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            total REAL NOT NULL,
            FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT UNIQUE NOT NULL,
            quantity REAL NOT NULL DEFAULT 0,
            unit TEXT NOT NULL DEFAULT 'pcs',
            low_stock_threshold REAL NOT NULL DEFAULT 5
        )
    """)

    conn.commit()
    conn.close()


def seed_demo_data():
    """Insert some starter data so the app is usable immediately (idempotent)."""
    conn = get_connection()
    cur = conn.cursor()

    # Categories
    categories = ["Starters", "Main Course", "Beverages", "Desserts"]
    for c in categories:
        cur.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (c,))

    conn.commit()

    cur.execute("SELECT id, name FROM categories")
    cat_map = {name: cid for cid, name in cur.fetchall()}

    # Menu items: (name, category, price, is_veg)
    menu_items = [
        ("Veg Spring Roll", "Starters", 120, 1),
        ("Chicken Wings", "Starters", 180, 0),
        ("Paneer Butter Masala", "Main Course", 220, 1),
        ("Chicken Biryani", "Main Course", 250, 0),
        ("Veg Fried Rice", "Main Course", 160, 1),
        ("Cold Coffee", "Beverages", 90, 1),
        ("Masala Chai", "Beverages", 40, 1),
        ("Gulab Jamun", "Desserts", 70, 1),
        ("Chocolate Brownie", "Desserts", 110, 1),
    ]
    for name, cat, price, veg in menu_items:
        cur.execute("SELECT id FROM menu_items WHERE name = ?", (name,))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO menu_items (name, category_id, price, is_veg, available) VALUES (?, ?, ?, ?, 1)",
                (name, cat_map.get(cat), price, veg),
            )

    # Tables
    for i in range(1, 9):
        table_no = f"T{i}"
        cur.execute("INSERT OR IGNORE INTO dining_tables (table_no, status) VALUES (?, 'Available')", (table_no,))

    # Inventory
    inventory_items = [
        ("Chicken (kg)", 20, "kg", 5),
        ("Paneer (kg)", 10, "kg", 3),
        ("Rice (kg)", 30, "kg", 8),
        ("Milk (litre)", 15, "litre", 5),
        ("Cooking Oil (litre)", 12, "litre", 4),
    ]
    for name, qty, unit, threshold in inventory_items:
        cur.execute(
            "INSERT OR IGNORE INTO inventory (item_name, quantity, unit, low_stock_threshold) VALUES (?, ?, ?, ?)",
            (name, qty, unit, threshold),
        )

    conn.commit()
    conn.close()
