"""
app.py
Entry point for the Restaurant Billing & Management System.
Run this file to start the application: python app.py
"""

import tkinter as tk
from database import init_db, seed_demo_data
from auth_db import ensure_default_admin
from ui.login_window import LoginWindow
from ui.admin_dashboard import AdminDashboard
from ui.cashier_pos import CashierPOS


def launch_main_window(username, role):
    if role == "admin":
        app = AdminDashboard(username)
        app.mainloop()
    else:
        # Cashier goes straight into the POS screen, wrapped in a root window
        root = tk.Tk()
        root.withdraw()  # hide the empty root; POS Toplevel is the real window

        def on_pos_close():
            root.destroy()

        pos = CashierPOS(root, username, role, on_close=on_pos_close)
        pos.mainloop()


def main():
    init_db()
    seed_demo_data()
    ensure_default_admin()

    LoginWindow(on_success=launch_main_window).mainloop()


if __name__ == "__main__":
    main()
