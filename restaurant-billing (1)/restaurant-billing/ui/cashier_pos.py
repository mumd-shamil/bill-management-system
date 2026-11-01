"""
ui/cashier_pos.py
The main Point-of-Sale billing screen used by cashiers (and accessible by admin).
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ui.components import apply_theme, card, primary_button, secondary_button, ACCENT, BG, CARD_BG, TEXT_DARK, FONT_FAMILY
from menu import get_categories, get_menu_items
from billing import get_tables, set_table_status, create_bill
from invoice import generate_invoice_pdf
import os
import subprocess
import sys

DEFAULT_TAX_PERCENT = 5.0


class CashierPOS(tk.Toplevel):
    def __init__(self, master, username, role, on_close=None):
        super().__init__(master)
        self.username = username
        self.role = role
        self.on_close = on_close
        self.title("Cashier POS - Tasty Treats")
        self.geometry("1100x650")
        self.minsize(1000, 600)
        apply_theme(self)
        self.configure(bg=BG)

        self.cart = []  # list of {"name", "price", "qty"}
        self.selected_table_id = None
        self.order_type_var = tk.StringVar(value="Dine-in")

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._handle_close)

    # ---------- UI construction ----------

    def _build_ui(self):
        header = ttk.Frame(self, padding=(15, 10))
        header.pack(fill="x")
        tk.Label(header, text="Point of Sale", font=(FONT_FAMILY, 16, "bold"), bg=BG, fg=TEXT_DARK).pack(side="left")
        tk.Label(header, text=f"Logged in as: {self.username} ({self.role})", font=(FONT_FAMILY, 9),
                 bg=BG, fg="#666666").pack(side="right")

        body = ttk.Frame(self, padding=(15, 0, 15, 15))
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        # ---- Left: menu browsing ----
        left = card(body)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(2, weight=1)

        tk.Label(left, text="Menu", font=(FONT_FAMILY, 13, "bold"), bg=CARD_BG, fg=TEXT_DARK).grid(
            row=0, column=0, sticky="w", pady=(0, 8))

        cat_frame = ttk.Frame(left, style="Card.TFrame")
        cat_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        self.category_var = tk.StringVar(value="All")
        categories = ["All"] + [name for _, name in get_categories()]
        self.category_combo = ttk.Combobox(cat_frame, textvariable=self.category_var, values=categories,
                                            state="readonly", width=20)
        self.category_combo.pack(side="left")
        self.category_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_menu_grid())

        search_var = tk.StringVar()
        self.search_var = search_var
        search_entry = tk.Entry(cat_frame, textvariable=search_var, font=(FONT_FAMILY, 10), relief="flat", bg="#F0F0F0")
        search_entry.pack(side="left", padx=(10, 0), ipady=4, fill="x", expand=True)
        search_entry.insert(0, "")
        search_entry.bind("<KeyRelease>", lambda e: self._refresh_menu_grid())
        tk.Label(cat_frame, text="🔍", bg=CARD_BG).pack(side="left", padx=(4, 0))

        self.menu_canvas_frame = ttk.Frame(left, style="Card.TFrame")
        self.menu_canvas_frame.grid(row=2, column=0, sticky="nsew")
        self.menu_canvas_frame.columnconfigure(0, weight=1)
        self.menu_canvas_frame.rowconfigure(0, weight=1)

        self.menu_canvas = tk.Canvas(self.menu_canvas_frame, bg=CARD_BG, highlightthickness=0)
        self.menu_scroll = ttk.Scrollbar(self.menu_canvas_frame, orient="vertical", command=self.menu_canvas.yview)
        self.menu_inner = ttk.Frame(self.menu_canvas, style="Card.TFrame")
        self.menu_inner.bind("<Configure>", lambda e: self.menu_canvas.configure(scrollregion=self.menu_canvas.bbox("all")))

        self.menu_canvas.create_window((0, 0), window=self.menu_inner, anchor="nw")
        self.menu_canvas.configure(yscrollcommand=self.menu_scroll.set)
        self.menu_canvas.grid(row=0, column=0, sticky="nsew")
        self.menu_scroll.grid(row=0, column=1, sticky="ns")

        self._refresh_menu_grid()

        # ---- Right: cart & checkout ----
        right = card(body)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(3, weight=1)

        tk.Label(right, text="Current Order", font=(FONT_FAMILY, 13, "bold"), bg=CARD_BG, fg=TEXT_DARK).grid(
            row=0, column=0, sticky="w")

        meta_frame = ttk.Frame(right, style="Card.TFrame")
        meta_frame.grid(row=1, column=0, sticky="ew", pady=8)

        tk.Label(meta_frame, text="Order Type:", bg=CARD_BG, font=(FONT_FAMILY, 9)).grid(row=0, column=0, sticky="w")
        order_combo = ttk.Combobox(meta_frame, textvariable=self.order_type_var,
                                    values=["Dine-in", "Takeaway", "Delivery"], state="readonly", width=12)
        order_combo.grid(row=0, column=1, sticky="w", padx=6)
        order_combo.bind("<<ComboboxSelected>>", lambda e: self._toggle_table_selector())

        tk.Label(meta_frame, text="Table:", bg=CARD_BG, font=(FONT_FAMILY, 9)).grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.table_var = tk.StringVar()
        self.table_combo = ttk.Combobox(meta_frame, textvariable=self.table_var, state="readonly", width=12)
        self.table_combo.grid(row=1, column=1, sticky="w", padx=6, pady=(6, 0))
        self._refresh_tables()

        # Cart list
        cart_columns = ("name", "price", "qty", "total")
        self.cart_tree = ttk.Treeview(right, columns=cart_columns, show="headings", height=10)
        self.cart_tree.heading("name", text="Item")
        self.cart_tree.heading("price", text="Price")
        self.cart_tree.heading("qty", text="Qty")
        self.cart_tree.heading("total", text="Total")
        self.cart_tree.column("name", width=140)
        self.cart_tree.column("price", width=60, anchor="e")
        self.cart_tree.column("qty", width=50, anchor="center")
        self.cart_tree.column("total", width=70, anchor="e")
        self.cart_tree.grid(row=3, column=0, sticky="nsew", pady=(8, 8))

        cart_btns = ttk.Frame(right, style="Card.TFrame")
        cart_btns.grid(row=4, column=0, sticky="ew")
        secondary_button(cart_btns, "− Qty", self._decrease_qty).pack(side="left", padx=(0, 4))
        secondary_button(cart_btns, "+ Qty", self._increase_qty).pack(side="left", padx=(0, 4))
        secondary_button(cart_btns, "Remove", self._remove_item).pack(side="left")

        # Totals + checkout
        totals_frame = ttk.Frame(right, style="Card.TFrame")
        totals_frame.grid(row=5, column=0, sticky="ew", pady=(10, 0))

        tk.Label(totals_frame, text="Discount %:", bg=CARD_BG, font=(FONT_FAMILY, 9)).grid(row=0, column=0, sticky="w")
        self.discount_var = tk.StringVar(value="0")
        tk.Entry(totals_frame, textvariable=self.discount_var, width=6, relief="flat", bg="#F0F0F0").grid(
            row=0, column=1, sticky="w", padx=6)

        tk.Label(totals_frame, text="Tax %:", bg=CARD_BG, font=(FONT_FAMILY, 9)).grid(row=0, column=2, sticky="w", padx=(10, 0))
        self.tax_var = tk.StringVar(value=str(DEFAULT_TAX_PERCENT))
        tk.Entry(totals_frame, textvariable=self.tax_var, width=6, relief="flat", bg="#F0F0F0").grid(
            row=0, column=3, sticky="w", padx=6)

        self.total_label = tk.Label(totals_frame, text="Total: ₹0.00", font=(FONT_FAMILY, 14, "bold"),
                                     bg=CARD_BG, fg=ACCENT)
        self.total_label.grid(row=1, column=0, columnspan=4, sticky="w", pady=(10, 0))

        tk.Label(totals_frame, text="Payment Mode:", bg=CARD_BG, font=(FONT_FAMILY, 9)).grid(
            row=2, column=0, sticky="w", pady=(8, 0))
        self.payment_var = tk.StringVar(value="Cash")
        payment_combo = ttk.Combobox(totals_frame, textvariable=self.payment_var,
                                      values=["Cash", "Card", "UPI", "Wallet"], state="readonly", width=10)
        payment_combo.grid(row=2, column=1, columnspan=2, sticky="w", padx=6, pady=(8, 0))

        tk.Label(totals_frame, text="Amount Received:", bg=CARD_BG, font=(FONT_FAMILY, 9)).grid(
            row=3, column=0, sticky="w", pady=(8, 0))
        self.received_var = tk.StringVar(value="")
        tk.Entry(totals_frame, textvariable=self.received_var, width=10, relief="flat", bg="#F0F0F0").grid(
            row=3, column=1, sticky="w", padx=6, pady=(8, 0))

        for var in (self.discount_var, self.tax_var):
            var.trace_add("write", lambda *a: self._update_total_label())

        action_frame = ttk.Frame(right, style="Card.TFrame")
        action_frame.grid(row=6, column=0, sticky="ew", pady=(14, 0))
        primary_button(action_frame, "Generate Bill", self._checkout).pack(fill="x")

        self._toggle_table_selector()

    # ---------- Menu grid ----------

    def _refresh_menu_grid(self):
        for widget in self.menu_inner.winfo_children():
            widget.destroy()

        category_name = self.category_var.get()
        category_id = None
        if category_name != "All":
            for cid, name in get_categories():
                if name == category_name:
                    category_id = cid
                    break

        items = get_menu_items(category_id=category_id, available_only=True)
        search_text = self.search_var.get().strip().lower()
        if search_text:
            items = [i for i in items if search_text in i[1].lower()]

        cols_per_row = 3
        for idx, (item_id, name, cat, price, is_veg, available) in enumerate(items):
            row, col = divmod(idx, cols_per_row)
            tile = tk.Frame(self.menu_inner, bg="#FAFAFA", highlightbackground="#DDDDDD",
                             highlightthickness=1, width=160, height=80)
            tile.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            tile.grid_propagate(False)

            veg_tag = "🟢" if is_veg else "🔴"
            tk.Label(tile, text=f"{veg_tag} {name}", font=(FONT_FAMILY, 10, "bold"), bg="#FAFAFA",
                     wraplength=140, justify="left").pack(anchor="w", padx=8, pady=(8, 0))
            tk.Label(tile, text=f"₹{price:.2f}", font=(FONT_FAMILY, 9), bg="#FAFAFA", fg="#555555").pack(
                anchor="w", padx=8)

            add_btn = tk.Button(tile, text="+ Add", bg=ACCENT, fg="white", relief="flat", font=(FONT_FAMILY, 8, "bold"),
                                 cursor="hand2", borderwidth=0,
                                 command=lambda n=name, p=price: self._add_to_cart(n, p))
            add_btn.pack(anchor="e", padx=8, pady=(4, 8))

        self.menu_inner.update_idletasks()
        self.menu_canvas.configure(scrollregion=self.menu_canvas.bbox("all"))

    # ---------- Cart logic ----------

    def _add_to_cart(self, name, price):
        for item in self.cart:
            if item["name"] == name:
                item["qty"] += 1
                self._refresh_cart_view()
                return
        self.cart.append({"name": name, "price": price, "qty": 1})
        self._refresh_cart_view()

    def _get_selected_cart_item(self):
        selection = self.cart_tree.selection()
        if not selection:
            return None
        index = self.cart_tree.index(selection[0])
        return self.cart[index]

    def _increase_qty(self):
        item = self._get_selected_cart_item()
        if item:
            item["qty"] += 1
            self._refresh_cart_view()

    def _decrease_qty(self):
        item = self._get_selected_cart_item()
        if item:
            item["qty"] -= 1
            if item["qty"] <= 0:
                self.cart.remove(item)
            self._refresh_cart_view()

    def _remove_item(self):
        item = self._get_selected_cart_item()
        if item:
            self.cart.remove(item)
            self._refresh_cart_view()

    def _refresh_cart_view(self):
        self.cart_tree.delete(*self.cart_tree.get_children())
        for item in self.cart:
            self.cart_tree.insert("", "end", values=(
                item["name"], f"{item['price']:.2f}", item["qty"], f"{item['price'] * item['qty']:.2f}"
            ))
        self._update_total_label()

    def _calculate_totals(self):
        try:
            discount_percent = float(self.discount_var.get() or 0)
        except ValueError:
            discount_percent = 0
        try:
            tax_percent = float(self.tax_var.get() or 0)
        except ValueError:
            tax_percent = 0

        subtotal = sum(i["price"] * i["qty"] for i in self.cart)
        discount_amount = subtotal * (discount_percent / 100)
        taxable = subtotal - discount_amount
        tax_amount = taxable * (tax_percent / 100)
        total = taxable + tax_amount
        return subtotal, discount_percent, discount_amount, tax_percent, tax_amount, total

    def _update_total_label(self):
        *_, total = self._calculate_totals()
        self.total_label.config(text=f"Total: ₹{total:.2f}")

    # ---------- Table handling ----------

    def _toggle_table_selector(self):
        if self.order_type_var.get() == "Dine-in":
            self.table_combo.configure(state="readonly")
        else:
            self.table_var.set("")
            self.table_combo.configure(state="disabled")

    def _refresh_tables(self):
        tables = get_tables()
        self.table_map = {f"{no} ({status})": tid for tid, no, status in tables if status == "Available"}
        self.table_combo["values"] = list(self.table_map.keys())

    # ---------- Checkout ----------

    def _checkout(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Please add at least one item before generating a bill.")
            return

        order_type = self.order_type_var.get()
        table_id = None
        if order_type == "Dine-in":
            selected_table = self.table_var.get()
            if not selected_table:
                messagebox.showwarning("Table Required", "Please select a table for dine-in orders.")
                return
            table_id = self.table_map.get(selected_table)

        subtotal, discount_percent, discount_amount, tax_percent, tax_amount, total = self._calculate_totals()

        try:
            amount_received = float(self.received_var.get() or total)
        except ValueError:
            messagebox.showwarning("Invalid Amount", "Please enter a valid amount received.")
            return

        if amount_received < total:
            confirm = messagebox.askyesno(
                "Insufficient Amount",
                f"Amount received (₹{amount_received:.2f}) is less than total (₹{total:.2f}). Proceed anyway?"
            )
            if not confirm:
                return

        if table_id:
            set_table_status(table_id, "Occupied")

        bill = create_bill(
            cart=self.cart,
            table_id=table_id,
            order_type=order_type,
            tax_percent=tax_percent,
            discount_percent=discount_percent,
            payment_mode=self.payment_var.get(),
            amount_received=amount_received,
            cashier=self.username,
        )

        pdf_path = generate_invoice_pdf(bill)
        messagebox.showinfo(
            "Bill Generated",
            f"Bill {bill['bill_no']} created successfully.\nTotal: ₹{bill['total']:.2f}\n"
            f"Invoice saved to:\n{pdf_path}"
        )

        self._open_pdf(pdf_path)
        self._reset_order()

    def _open_pdf(self, path):
        try:
            if sys.platform.startswith("win"):
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
        except Exception:
            pass  # silently ignore if no viewer available

    def _reset_order(self):
        self.cart = []
        self.discount_var.set("0")
        self.tax_var.set(str(DEFAULT_TAX_PERCENT))
        self.received_var.set("")
        self.table_var.set("")
        self._refresh_cart_view()
        self._refresh_tables()

    def _handle_close(self):
        if self.on_close:
            self.on_close()
        self.destroy()
