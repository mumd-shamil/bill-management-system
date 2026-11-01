"""
ui/admin_dashboard.py
Admin dashboard: menu management, inventory, reports, bill history, and POS access.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ui.components import apply_theme, card, primary_button, secondary_button, danger_button, ACCENT, BG, CARD_BG, TEXT_DARK, FONT_FAMILY
from ui.cashier_pos import CashierPOS
from menu import get_categories, add_category, get_menu_items, add_menu_item, update_menu_item, delete_menu_item
from inventory import get_inventory, add_inventory_item, update_stock, delete_inventory_item, get_low_stock_items
from reports import get_today_sales, get_total_sales, get_top_selling_items
from billing import get_all_bills, get_bill_items


class AdminDashboard(tk.Tk):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.title("Admin Dashboard - Tasty Treats")
        self.geometry("1150x680")
        self.minsize(1000, 600)
        apply_theme(self)
        self.configure(bg=BG)
        self._build_ui()

    def _build_ui(self):
        header = ttk.Frame(self, padding=(15, 12))
        header.pack(fill="x")
        tk.Label(header, text="🍽 Admin Dashboard", font=(FONT_FAMILY, 16, "bold"), bg=BG, fg=TEXT_DARK).pack(side="left")
        tk.Label(header, text=f"Welcome, {self.username}", font=(FONT_FAMILY, 9), bg=BG, fg="#666666").pack(side="right", padx=10)
        primary_button(header, "Open POS", self._open_pos).pack(side="right")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.overview_tab = ttk.Frame(notebook, padding=15)
        self.menu_tab = ttk.Frame(notebook, padding=15)
        self.inventory_tab = ttk.Frame(notebook, padding=15)
        self.bills_tab = ttk.Frame(notebook, padding=15)

        notebook.add(self.overview_tab, text="Overview")
        notebook.add(self.menu_tab, text="Menu Management")
        notebook.add(self.inventory_tab, text="Inventory")
        notebook.add(self.bills_tab, text="Bill History")

        notebook.bind("<<NotebookTabChanged>>", lambda e: self._on_tab_change(notebook, e))

        self._build_overview_tab()
        self._build_menu_tab()
        self._build_inventory_tab()
        self._build_bills_tab()

    def _on_tab_change(self, notebook, event):
        tab_text = notebook.tab(notebook.select(), "text")
        if tab_text == "Overview":
            self._refresh_overview()
        elif tab_text == "Inventory":
            self._refresh_inventory_table()
        elif tab_text == "Bill History":
            self._refresh_bills_table()

    def _open_pos(self):
        CashierPOS(self, self.username, "admin")

    # ================= OVERVIEW =================

    def _build_overview_tab(self):
        self.overview_tab.columnconfigure((0, 1, 2), weight=1)

        self.stat_today_count = self._stat_card(self.overview_tab, "Today's Orders", "0", 0, 0)
        self.stat_today_sales = self._stat_card(self.overview_tab, "Today's Sales", "₹0.00", 0, 1)
        self.stat_total_sales = self._stat_card(self.overview_tab, "All-Time Sales", "₹0.00", 0, 2)

        top_card = card(self.overview_tab)
        top_card.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(15, 0), padx=(0, 8))
        tk.Label(top_card, text="Top Selling Items", font=(FONT_FAMILY, 12, "bold"), bg=CARD_BG, fg=TEXT_DARK).pack(
            anchor="w", pady=(0, 8))
        self.top_items_tree = ttk.Treeview(top_card, columns=("name", "qty", "revenue"), show="headings", height=6)
        self.top_items_tree.heading("name", text="Item")
        self.top_items_tree.heading("qty", text="Qty Sold")
        self.top_items_tree.heading("revenue", text="Revenue")
        self.top_items_tree.pack(fill="both", expand=True)

        low_stock_card = card(self.overview_tab)
        low_stock_card.grid(row=1, column=2, sticky="nsew", pady=(15, 0))
        tk.Label(low_stock_card, text="⚠ Low Stock Alerts", font=(FONT_FAMILY, 12, "bold"), bg=CARD_BG, fg="#D13438").pack(
            anchor="w", pady=(0, 8))
        self.low_stock_list = tk.Listbox(low_stock_card, font=(FONT_FAMILY, 9), relief="flat", bg="#FFF8F0")
        self.low_stock_list.pack(fill="both", expand=True)

        self.overview_tab.rowconfigure(1, weight=1)
        self._refresh_overview()

    def _stat_card(self, parent, title, value, row, col):
        c = card(parent)
        c.grid(row=row, column=col, sticky="nsew", padx=8 if col else (0, 8), pady=(0, 0))
        tk.Label(c, text=title, font=(FONT_FAMILY, 9), bg=CARD_BG, fg="#666666").pack(anchor="w")
        value_label = tk.Label(c, text=value, font=(FONT_FAMILY, 22, "bold"), bg=CARD_BG, fg=ACCENT)
        value_label.pack(anchor="w", pady=(4, 0))
        return value_label

    def _refresh_overview(self):
        count, total = get_today_sales()
        self.stat_today_count.config(text=str(count))
        self.stat_today_sales.config(text=f"₹{total:.2f}")

        _, all_total = get_total_sales()
        self.stat_total_sales.config(text=f"₹{all_total:.2f}")

        self.top_items_tree.delete(*self.top_items_tree.get_children())
        for name, qty, revenue in get_top_selling_items():
            self.top_items_tree.insert("", "end", values=(name, int(qty), f"₹{revenue:.2f}"))

        self.low_stock_list.delete(0, tk.END)
        low_items = get_low_stock_items()
        if not low_items:
            self.low_stock_list.insert(tk.END, "All stock levels are healthy ✅")
        for name, qty, unit, threshold in low_items:
            self.low_stock_list.insert(tk.END, f"{name}: {qty} {unit} (threshold {threshold})")

    # ================= MENU MANAGEMENT =================

    def _build_menu_tab(self):
        self.menu_tab.columnconfigure(0, weight=1)
        self.menu_tab.rowconfigure(1, weight=1)

        form_card = card(self.menu_tab)
        form_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        tk.Label(form_card, text="Add Menu Item", font=(FONT_FAMILY, 12, "bold"), bg=CARD_BG).grid(
            row=0, column=0, columnspan=6, sticky="w", pady=(0, 10))

        tk.Label(form_card, text="Name", bg=CARD_BG, font=(FONT_FAMILY, 9)).grid(row=1, column=0, sticky="w")
        self.item_name_var = tk.StringVar()
        tk.Entry(form_card, textvariable=self.item_name_var, width=20, relief="flat", bg="#F0F0F0").grid(
            row=1, column=1, padx=6, ipady=4)

        tk.Label(form_card, text="Category", bg=CARD_BG, font=(FONT_FAMILY, 9)).grid(row=1, column=2, sticky="w")
        self.item_category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(form_card, textvariable=self.item_category_var, state="readonly", width=15)
        self.category_combo.grid(row=1, column=3, padx=6)

        tk.Label(form_card, text="Price (₹)", bg=CARD_BG, font=(FONT_FAMILY, 9)).grid(row=1, column=4, sticky="w")
        self.item_price_var = tk.StringVar()
        tk.Entry(form_card, textvariable=self.item_price_var, width=10, relief="flat", bg="#F0F0F0").grid(
            row=1, column=5, padx=6, ipady=4)

        self.item_veg_var = tk.BooleanVar(value=True)
        tk.Checkbutton(form_card, text="Vegetarian", variable=self.item_veg_var, bg=CARD_BG).grid(
            row=2, column=0, sticky="w", pady=(8, 0))

        primary_button(form_card, "Add Item", self._add_menu_item).grid(row=2, column=1, sticky="w", pady=(8, 0))

        new_cat_frame = ttk.Frame(form_card, style="Card.TFrame")
        new_cat_frame.grid(row=2, column=2, columnspan=4, sticky="w", pady=(8, 0))
        tk.Label(new_cat_frame, text="New Category:", bg=CARD_BG, font=(FONT_FAMILY, 9)).pack(side="left")
        self.new_category_var = tk.StringVar()
        tk.Entry(new_cat_frame, textvariable=self.new_category_var, width=15, relief="flat", bg="#F0F0F0").pack(
            side="left", padx=6, ipady=4)
        secondary_button(new_cat_frame, "Add Category", self._add_category).pack(side="left")

        list_card = card(self.menu_tab)
        list_card.grid(row=1, column=0, sticky="nsew")
        list_card.columnconfigure(0, weight=1)
        list_card.rowconfigure(1, weight=1)

        tk.Label(list_card, text="Menu Items", font=(FONT_FAMILY, 12, "bold"), bg=CARD_BG).grid(
            row=0, column=0, sticky="w", pady=(0, 8))

        columns = ("id", "name", "category", "price", "veg", "available")
        self.menu_tree = ttk.Treeview(list_card, columns=columns, show="headings", height=14)
        headers = {"id": "ID", "name": "Name", "category": "Category", "price": "Price",
                   "veg": "Veg/Non-Veg", "available": "Available"}
        for col in columns:
            self.menu_tree.heading(col, text=headers[col])
        self.menu_tree.column("id", width=40, anchor="center")
        self.menu_tree.column("price", width=80, anchor="e")
        self.menu_tree.column("veg", width=90, anchor="center")
        self.menu_tree.column("available", width=80, anchor="center")
        self.menu_tree.grid(row=1, column=0, sticky="nsew")

        btn_frame = ttk.Frame(list_card, style="Card.TFrame")
        btn_frame.grid(row=2, column=0, sticky="w", pady=(8, 0))
        secondary_button(btn_frame, "Toggle Availability", self._toggle_availability).pack(side="left", padx=(0, 6))
        danger_button(btn_frame, "Delete Item", self._delete_menu_item).pack(side="left")

        self._refresh_category_dropdown()
        self._refresh_menu_table()

    def _refresh_category_dropdown(self):
        self.categories = get_categories()
        self.category_combo["values"] = [name for _, name in self.categories]
        if self.categories:
            self.category_combo.current(0)

    def _refresh_menu_table(self):
        self.menu_tree.delete(*self.menu_tree.get_children())
        for item_id, name, cat, price, is_veg, available in get_menu_items():
            self.menu_tree.insert("", "end", values=(
                item_id, name, cat or "-", f"₹{price:.2f}",
                "Veg" if is_veg else "Non-Veg", "Yes" if available else "No"
            ))

    def _add_category(self):
        name = self.new_category_var.get().strip()
        success, msg = add_category(name)
        if success:
            self.new_category_var.set("")
            self._refresh_category_dropdown()
        else:
            messagebox.showwarning("Category", msg)

    def _add_menu_item(self):
        name = self.item_name_var.get().strip()
        category_name = self.item_category_var.get()
        category_id = None
        for cid, cname in self.categories:
            if cname == category_name:
                category_id = cid
                break

        try:
            price = float(self.item_price_var.get())
        except ValueError:
            messagebox.showwarning("Invalid Price", "Please enter a valid numeric price.")
            return

        success, msg = add_menu_item(name, category_id, price, self.item_veg_var.get())
        if success:
            self.item_name_var.set("")
            self.item_price_var.set("")
            self._refresh_menu_table()
        else:
            messagebox.showwarning("Menu Item", msg)

    def _get_selected_menu_item_id(self):
        selection = self.menu_tree.selection()
        if not selection:
            messagebox.showinfo("Select Item", "Please select a menu item first.")
            return None
        return self.menu_tree.item(selection[0])["values"][0]

    def _toggle_availability(self):
        item_id = self._get_selected_menu_item_id()
        if item_id is None:
            return
        for iid, name, cat, price, is_veg, available in get_menu_items():
            if iid == item_id:
                category_id = None
                for cid, cname in self.categories:
                    if cname == cat:
                        category_id = cid
                update_menu_item(iid, name, category_id, price, is_veg, not available)
                break
        self._refresh_menu_table()

    def _delete_menu_item(self):
        item_id = self._get_selected_menu_item_id()
        if item_id is None:
            return
        if messagebox.askyesno("Confirm Delete", "Delete this menu item permanently?"):
            delete_menu_item(item_id)
            self._refresh_menu_table()

    # ================= INVENTORY =================

    def _build_inventory_tab(self):
        self.inventory_tab.columnconfigure(0, weight=1)
        self.inventory_tab.rowconfigure(1, weight=1)

        form_card = card(self.inventory_tab)
        form_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        tk.Label(form_card, text="Add Inventory Item", font=(FONT_FAMILY, 12, "bold"), bg=CARD_BG).grid(
            row=0, column=0, columnspan=8, sticky="w", pady=(0, 10))

        tk.Label(form_card, text="Name", bg=CARD_BG, font=(FONT_FAMILY, 9)).grid(row=1, column=0, sticky="w")
        self.inv_name_var = tk.StringVar()
        tk.Entry(form_card, textvariable=self.inv_name_var, width=18, relief="flat", bg="#F0F0F0").grid(
            row=1, column=1, padx=6, ipady=4)

        tk.Label(form_card, text="Quantity", bg=CARD_BG, font=(FONT_FAMILY, 9)).grid(row=1, column=2, sticky="w")
        self.inv_qty_var = tk.StringVar()
        tk.Entry(form_card, textvariable=self.inv_qty_var, width=8, relief="flat", bg="#F0F0F0").grid(
            row=1, column=3, padx=6, ipady=4)

        tk.Label(form_card, text="Unit", bg=CARD_BG, font=(FONT_FAMILY, 9)).grid(row=1, column=4, sticky="w")
        self.inv_unit_var = tk.StringVar(value="kg")
        tk.Entry(form_card, textvariable=self.inv_unit_var, width=8, relief="flat", bg="#F0F0F0").grid(
            row=1, column=5, padx=6, ipady=4)

        tk.Label(form_card, text="Low Stock Alert", bg=CARD_BG, font=(FONT_FAMILY, 9)).grid(row=1, column=6, sticky="w")
        self.inv_threshold_var = tk.StringVar(value="5")
        tk.Entry(form_card, textvariable=self.inv_threshold_var, width=8, relief="flat", bg="#F0F0F0").grid(
            row=1, column=7, padx=6, ipady=4)

        primary_button(form_card, "Add to Inventory", self._add_inventory_item).grid(
            row=2, column=0, sticky="w", pady=(8, 0))

        list_card = card(self.inventory_tab)
        list_card.grid(row=1, column=0, sticky="nsew")
        list_card.columnconfigure(0, weight=1)
        list_card.rowconfigure(1, weight=1)

        tk.Label(list_card, text="Current Stock", font=(FONT_FAMILY, 12, "bold"), bg=CARD_BG).grid(
            row=0, column=0, sticky="w", pady=(0, 8))

        columns = ("id", "name", "qty", "unit", "threshold")
        self.inv_tree = ttk.Treeview(list_card, columns=columns, show="headings", height=12)
        headers = {"id": "ID", "name": "Item", "qty": "Quantity", "unit": "Unit", "threshold": "Low Stock Threshold"}
        for col in columns:
            self.inv_tree.heading(col, text=headers[col])
        self.inv_tree.column("id", width=40, anchor="center")
        self.inv_tree.grid(row=1, column=0, sticky="nsew")

        btn_frame = ttk.Frame(list_card, style="Card.TFrame")
        btn_frame.grid(row=2, column=0, sticky="w", pady=(8, 0))

        tk.Label(btn_frame, text="New Qty:", bg=CARD_BG, font=(FONT_FAMILY, 9)).pack(side="left")
        self.inv_update_qty_var = tk.StringVar()
        tk.Entry(btn_frame, textvariable=self.inv_update_qty_var, width=8, relief="flat", bg="#F0F0F0").pack(
            side="left", padx=6, ipady=2)
        secondary_button(btn_frame, "Update Stock", self._update_stock).pack(side="left", padx=(0, 6))
        danger_button(btn_frame, "Delete", self._delete_inventory_item).pack(side="left")

        self._refresh_inventory_table()

    def _refresh_inventory_table(self):
        self.inv_tree.delete(*self.inv_tree.get_children())
        for item_id, name, qty, unit, threshold in get_inventory():
            self.inv_tree.insert("", "end", values=(item_id, name, qty, unit, threshold))

    def _add_inventory_item(self):
        name = self.inv_name_var.get().strip()
        try:
            qty = float(self.inv_qty_var.get())
            threshold = float(self.inv_threshold_var.get())
        except ValueError:
            messagebox.showwarning("Invalid Input", "Quantity and threshold must be numbers.")
            return
        unit = self.inv_unit_var.get().strip() or "pcs"

        success, msg = add_inventory_item(name, qty, unit, threshold)
        if success:
            self.inv_name_var.set("")
            self.inv_qty_var.set("")
            self._refresh_inventory_table()
        else:
            messagebox.showwarning("Inventory", msg)

    def _get_selected_inventory_id(self):
        selection = self.inv_tree.selection()
        if not selection:
            messagebox.showinfo("Select Item", "Please select an inventory item first.")
            return None
        return self.inv_tree.item(selection[0])["values"][0]

    def _update_stock(self):
        item_id = self._get_selected_inventory_id()
        if item_id is None:
            return
        try:
            new_qty = float(self.inv_update_qty_var.get())
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid quantity.")
            return
        update_stock(item_id, new_qty)
        self.inv_update_qty_var.set("")
        self._refresh_inventory_table()

    def _delete_inventory_item(self):
        item_id = self._get_selected_inventory_id()
        if item_id is None:
            return
        if messagebox.askyesno("Confirm Delete", "Delete this inventory item?"):
            delete_inventory_item(item_id)
            self._refresh_inventory_table()

    # ================= BILL HISTORY =================

    def _build_bills_tab(self):
        self.bills_tab.columnconfigure(0, weight=1)
        self.bills_tab.rowconfigure(1, weight=1)

        list_card = card(self.bills_tab)
        list_card.grid(row=0, column=0, sticky="nsew", rowspan=2)
        list_card.columnconfigure(0, weight=1)
        list_card.rowconfigure(1, weight=1)

        tk.Label(list_card, text="Bill History", font=(FONT_FAMILY, 12, "bold"), bg=CARD_BG).grid(
            row=0, column=0, sticky="w", pady=(0, 8))

        columns = ("id", "bill_no", "order_type", "total", "payment", "date")
        self.bills_tree = ttk.Treeview(list_card, columns=columns, show="headings", height=16)
        headers = {"id": "ID", "bill_no": "Bill No", "order_type": "Type", "total": "Total",
                   "payment": "Payment", "date": "Date/Time"}
        for col in columns:
            self.bills_tree.heading(col, text=headers[col])
        self.bills_tree.column("id", width=40, anchor="center")
        self.bills_tree.grid(row=1, column=0, sticky="nsew")
        self.bills_tree.bind("<<TreeviewSelect>>", lambda e: self._show_bill_items())

        detail_card = card(self.bills_tab)
        detail_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        tk.Label(detail_card, text="Bill Items", font=(FONT_FAMILY, 12, "bold"), bg=CARD_BG).pack(anchor="w", pady=(0, 8))
        self.bill_items_tree = ttk.Treeview(detail_card, columns=("name", "price", "qty", "total"),
                                             show="headings", height=14)
        for col, text in zip(("name", "price", "qty", "total"), ("Item", "Price", "Qty", "Total")):
            self.bill_items_tree.heading(col, text=text)
        self.bill_items_tree.pack(fill="both", expand=True)

        self.bills_tab.columnconfigure(1, weight=1)
        self._refresh_bills_table()

    def _refresh_bills_table(self):
        self.bills_tree.delete(*self.bills_tree.get_children())
        for bill_id, bill_no, order_type, total, payment_mode, created_at in get_all_bills():
            self.bills_tree.insert("", "end", values=(bill_id, bill_no, order_type, f"₹{total:.2f}", payment_mode, created_at))

    def _show_bill_items(self):
        selection = self.bills_tree.selection()
        if not selection:
            return
        bill_id = self.bills_tree.item(selection[0])["values"][0]
        self.bill_items_tree.delete(*self.bill_items_tree.get_children())
        for name, price, qty, total in get_bill_items(bill_id):
            self.bill_items_tree.insert("", "end", values=(name, f"₹{price:.2f}", qty, f"₹{total:.2f}"))
