"""
reports.py
Sales reporting: daily totals, top-selling items.
"""

from datetime import datetime
from database import get_connection


def get_today_sales():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM bills WHERE created_at LIKE ?", (f"{today}%",))
    count, total = cur.fetchone()
    conn.close()
    return count, total


def get_total_sales():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM bills")
    count, total = cur.fetchone()
    conn.close()
    return count, total


def get_top_selling_items(limit: int = 5):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT item_name, SUM(quantity) as qty_sold, SUM(total) as revenue
        FROM bill_items
        GROUP BY item_name
        ORDER BY qty_sold DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_sales_by_date(date_str: str):
    """date_str format: 'YYYY-MM-DD'"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM bills WHERE created_at LIKE ?", (f"{date_str}%",))
    count, total = cur.fetchone()
    conn.close()
    return count, total
