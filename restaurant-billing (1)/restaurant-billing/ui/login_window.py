"""
ui/login_window.py
Login screen shown at application startup.
"""

import tkinter as tk
from tkinter import messagebox
from ui.components import apply_theme, card, primary_button, ACCENT, BG, CARD_BG, TEXT_DARK, FONT_FAMILY
from auth_db import verify_login


class LoginWindow(tk.Tk):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.title("Tasty Treats - Login")
        self.geometry("420x460")
        self.resizable(False, False)
        apply_theme(self)
        self.configure(bg=BG)
        self._build_ui()
        self.eval('tk::PlaceWindow . center')

    def _build_ui(self):
        container = card(self)
        container.place(relx=0.5, rely=0.5, anchor="center", width=340, height=380)

        tk.Label(container, text="🍽", font=(FONT_FAMILY, 36), bg=CARD_BG).pack(pady=(10, 0))
        tk.Label(container, text="Tasty Treats Restaurant", font=(FONT_FAMILY, 15, "bold"),
                 bg=CARD_BG, fg=TEXT_DARK).pack(pady=(2, 0))
        tk.Label(container, text="Billing & Management System", font=(FONT_FAMILY, 9),
                 bg=CARD_BG, fg="#666666").pack(pady=(0, 20))

        tk.Label(container, text="Username", font=(FONT_FAMILY, 9), bg=CARD_BG, fg=TEXT_DARK).pack(
            anchor="w", padx=10)
        self.username_entry = tk.Entry(container, font=(FONT_FAMILY, 11), relief="flat", bg="#F0F0F0")
        self.username_entry.pack(fill="x", padx=10, pady=(2, 12), ipady=6)

        tk.Label(container, text="Password", font=(FONT_FAMILY, 9), bg=CARD_BG, fg=TEXT_DARK).pack(
            anchor="w", padx=10)
        self.password_entry = tk.Entry(container, font=(FONT_FAMILY, 11), relief="flat", bg="#F0F0F0", show="*")
        self.password_entry.pack(fill="x", padx=10, pady=(2, 20), ipady=6)
        self.password_entry.bind("<Return>", lambda e: self._attempt_login())

        login_btn = primary_button(container, "Login", self._attempt_login)
        login_btn.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(container, text="Demo: admin / admin123  |  cashier / cashier123",
                 font=(FONT_FAMILY, 8), bg=CARD_BG, fg="#999999").pack(pady=(10, 0))

        self.username_entry.focus()

    def _attempt_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Missing info", "Please enter both username and password.")
            return

        result = verify_login(username, password)
        if result is None:
            messagebox.showerror("Login Failed", "Invalid username or password.")
            return

        user_id, role = result
        self.destroy()
        self.on_success(username, role)
