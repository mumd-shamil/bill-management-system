"""
menu.py
CRUD operations for categories and menu items.
"""

from database import get_connection


def get_categories():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM categories ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return rows


def add_category(name: str) -> tuple[bool, str]:
    if not name.strip():
        return False, "Category name cannot be empty."
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO categories (name) VALUES (?)", (name.strip(),))
        conn.commit()
        return True, "Category added."
    except Exception:
        return False, "Category already exists."
    finally:
        conn.close()


def get_menu_items(category_id=None, available_only=False):
    conn = get_connection()
    cur = conn.cursor()
    query = """
        SELECT m.id, m.name, c.name, m.price, m.is_veg, m.available
        FROM menu_items m
        LEFT JOIN categories c ON m.category_id = c.id
    """
    conditions = []
    params = []
    if category_id:
        conditions.append("m.category_id = ?")
        params.append(category_id)
    if available_only:
        conditions.append("m.available = 1")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY c.name, m.name"

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows


def add_menu_item(name: str, category_id, price: float, is_veg: bool) -> tuple[bool, str]:
    if not name.strip():
        return False, "Item name cannot be empty."
    if price <= 0:
        return False, "Price must be greater than zero."

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO menu_items (name, category_id, price, is_veg, available) VALUES (?, ?, ?, ?, 1)",
        (name.strip(), category_id, price, 1 if is_veg else 0),
    )
    conn.commit()
    conn.close()
    return True, "Menu item added."


def update_menu_item(item_id: int, name: str, category_id, price: float, is_veg: bool, available: bool):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """UPDATE menu_items
           SET name = ?, category_id = ?, price = ?, is_veg = ?, available = ?
           WHERE id = ?""",
        (name.strip(), category_id, price, 1 if is_veg else 0, 1 if available else 0, item_id),
    )
    conn.commit()
    conn.close()
    return True, "Menu item updated."


def delete_menu_item(item_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return True, "Menu item deleted."
