"""
billing.py
Handles bill creation, table status updates, and bill history lookups.
"""

from datetime import datetime
from database import get_connection


def get_tables():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, table_no, status FROM dining_tables ORDER BY table_no")
    rows = cur.fetchall()
    conn.close()
    return rows


def set_table_status(table_id: int, status: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE dining_tables SET status = ? WHERE id = ?", (status, table_id))
    conn.commit()
    conn.close()


def generate_bill_no() -> str:
    """Generate a unique, human-readable bill number like BILL-20260628-0001."""
    conn = get_connection()
    cur = conn.cursor()
    today = datetime.now().strftime("%Y%m%d")
    cur.execute("SELECT COUNT(*) FROM bills WHERE bill_no LIKE ?", (f"BILL-{today}-%",))
    count = cur.fetchone()[0] + 1
    conn.close()
    return f"BILL-{today}-{count:04d}"


def create_bill(cart: list, table_id, order_type: str, tax_percent: float,
                 discount_percent: float, payment_mode: str, amount_received: float,
                 cashier: str) -> dict:
    """
    cart: list of dicts -> {"name": str, "price": float, "qty": int}
    Returns a dict with full bill details (used for invoice generation).
    """
    subtotal = sum(item["price"] * item["qty"] for item in cart)
    discount_amount = round(subtotal * (discount_percent / 100), 2)
    taxable_amount = subtotal - discount_amount
    tax_amount = round(taxable_amount * (tax_percent / 100), 2)
    total = round(taxable_amount + tax_amount, 2)
    balance_returned = round(amount_received - total, 2) if amount_received >= total else 0

    bill_no = generate_bill_no()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO bills (bill_no, table_id, order_type, subtotal, tax_percent, tax_amount,
                            discount_percent, discount_amount, total, payment_mode,
                            amount_received, balance_returned, cashier, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (bill_no, table_id, order_type, subtotal, tax_percent, tax_amount,
          discount_percent, discount_amount, total, payment_mode,
          amount_received, balance_returned, cashier, created_at))
    bill_id = cur.lastrowid

    for item in cart:
        cur.execute("""
            INSERT INTO bill_items (bill_id, item_name, price, quantity, total)
            VALUES (?, ?, ?, ?, ?)
        """, (bill_id, item["name"], item["price"], item["qty"], item["price"] * item["qty"]))

    conn.commit()
    conn.close()

    if table_id:
        set_table_status(table_id, "Available")  # free the table once billed

    return {
        "bill_id": bill_id,
        "bill_no": bill_no,
        "order_type": order_type,
        "cart": cart,
        "subtotal": subtotal,
        "tax_percent": tax_percent,
        "tax_amount": tax_amount,
        "discount_percent": discount_percent,
        "discount_amount": discount_amount,
        "total": total,
        "payment_mode": payment_mode,
        "amount_received": amount_received,
        "balance_returned": balance_returned,
        "cashier": cashier,
        "created_at": created_at,
    }


def get_all_bills(date_filter: str = None):
    """date_filter format: 'YYYY-MM-DD'. Returns bill summary rows."""
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT id, bill_no, order_type, total, payment_mode, created_at FROM bills"
    params = []
    if date_filter:
        query += " WHERE created_at LIKE ?"
        params.append(f"{date_filter}%")
    query += " ORDER BY id DESC"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows


def get_bill_items(bill_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT item_name, price, quantity, total FROM bill_items WHERE bill_id = ?", (bill_id,))
    rows = cur.fetchall()
    conn.close()
    return rows
