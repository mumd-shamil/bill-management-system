# Tasty Treats — Restaurant Billing & Management System

A desktop restaurant billing (POS) application built with **Python, Tkinter, and SQLite**.

## Features

- **Login system** with role-based access (Admin / Cashier), passwords hashed with SHA-256
- **Admin Dashboard**
  - Overview: today's sales, all-time sales, top-selling items, low-stock alerts
  - Menu Management: add categories, add/edit/delete menu items, toggle availability, veg/non-veg tag
  - Inventory Management: track stock quantity, units, low-stock threshold, update/delete stock
  - Bill History: view every past bill and its line items
- **Cashier POS Screen**
  - Browse menu by category, search items
  - Add items to cart, adjust quantity, remove items
  - Select order type (Dine-in / Takeaway / Delivery) and table (for dine-in)
  - Apply discount % and tax % with live total calculation
  - Multiple payment modes (Cash, Card, UPI, Wallet), amount received / balance returned
  - **Generates a professional PDF invoice** automatically (opens after billing)
- Demo data is seeded automatically on first run (menu items, categories, tables, inventory)

## Requirements

- Python 3.9+
- `tkinter` (included with most Python installations; on Linux you may need `sudo apt install python3-tk`)
- `reportlab` (for PDF invoices)

## Setup (in VS Code)

1. Open this folder (`restaurant-billing`) in VS Code.
2. Open a terminal in VS Code (`Ctrl + ~` / `Cmd + ~`).
3. (Recommended) Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS/Linux
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run the application:
   ```
   python app.py
   ```

## Demo Login Credentials

| Role    | Username | Password   |
|---------|----------|------------|
| Admin   | admin    | admin123   |
| Cashier | cashier  | cashier123 |

You can change these later, or add new users via `auth_db.create_user(username, password, role)`.

## Project Structure

```
restaurant-billing/
├── app.py                 # Entry point — run this
├── database.py            # SQLite schema + demo data seeding
├── auth_db.py              # Login / password hashing
├── menu.py                 # Menu & category CRUD
├── billing.py               # Bill creation, table status, bill history
├── invoice.py                # PDF invoice generation (ReportLab)
├── inventory.py              # Stock tracking & low-stock alerts
├── reports.py                 # Sales reports
├── ui/
│   ├── components.py           # Shared styling/widgets
│   ├── login_window.py          # Login screen
│   ├── cashier_pos.py            # POS billing screen
│   └── admin_dashboard.py        # Admin dashboard (tabs)
├── invoices/                      # Generated PDF invoices land here
├── restaurant.db                   # SQLite database (created on first run)
└── requirements.txt
```

## Notes & Possible Extensions

This is a solid, working core system sized appropriately for a student/internship project.
If you want to extend it further, natural next steps include:
- Linking menu items to inventory ingredients so stock auto-deducts per order
- A Kitchen Display Screen (separate window showing live order status)
- Exporting reports to Excel/PDF
- Multi-day sales charts (e.g. with `matplotlib`)
- Packaging into a standalone `.exe` with PyInstaller (`app.spec` style, like the SEMS project)

## Troubleshooting

- **`ModuleNotFoundError: No module named 'tkinter'`** — Install it via your OS package manager
  (Linux: `sudo apt install python3-tk`; Tkinter ships by default with Python on Windows/macOS).
- **PDF doesn't open automatically** — It is still saved in the `invoices/` folder; open it manually.
- **Database looks empty/wrong** — Delete `restaurant.db` and re-run `app.py` to reseed demo data.
