"""
inventory.py
Simple inventory tracking with low-stock alerts.
"""

from database import get_connection


def get_inventory():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, item_name, quantity, unit, low_stock_threshold FROM inventory ORDER BY item_name")
    rows = cur.fetchall()
    conn.close()
    return rows


def add_inventory_item(name: str, quantity: float, unit: str, threshold: float):
    if not name.strip():
        return False, "Item name cannot be empty."
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO inventory (item_name, quantity, unit, low_stock_threshold) VALUES (?, ?, ?, ?)",
            (name.strip(), quantity, unit, threshold),
        )
        conn.commit()
        return True, "Inventory item added."
    except Exception:
        return False, "Item already exists in inventory."
    finally:
        conn.close()


def update_stock(item_id: int, new_quantity: float):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE inventory SET quantity = ? WHERE id = ?", (new_quantity, item_id))
    conn.commit()
    conn.close()
    return True, "Stock updated."


def delete_inventory_item(item_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return True, "Inventory item deleted."


def get_low_stock_items():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT item_name, quantity, unit, low_stock_threshold FROM inventory WHERE quantity <= low_stock_threshold")
    rows = cur.fetchall()
    conn.close()
    return rows
