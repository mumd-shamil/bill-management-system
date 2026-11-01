"""
invoice.py
Generates a professional PDF invoice for a completed bill using ReportLab.
"""

import os
from reportlab.lib.pagesizes import A5
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

INVOICE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "invoices")
os.makedirs(INVOICE_DIR, exist_ok=True)

RESTAURANT_NAME = "Tasty Treats Restaurant"
RESTAURANT_ADDRESS = "MG Road, Kochi, Kerala - 682001"
RESTAURANT_PHONE = "Phone: +91 98765 43210"
RESTAURANT_GST = "GSTIN: 32AAAAA0000A1Z5"


def generate_invoice_pdf(bill: dict) -> str:
    """Create a PDF invoice for the given bill dict and return the file path."""
    filename = f"{bill['bill_no']}.pdf"
    filepath = os.path.join(INVOICE_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A5,
                             topMargin=10 * mm, bottomMargin=10 * mm,
                             leftMargin=10 * mm, rightMargin=10 * mm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", parent=styles["Title"], fontSize=16, alignment=TA_CENTER)
    center_style = ParagraphStyle("center", parent=styles["Normal"], alignment=TA_CENTER, fontSize=9)
    normal = styles["Normal"]
    right_style = ParagraphStyle("right", parent=styles["Normal"], alignment=TA_RIGHT)

    elements = []
    elements.append(Paragraph(RESTAURANT_NAME, title_style))
    elements.append(Paragraph(RESTAURANT_ADDRESS, center_style))
    elements.append(Paragraph(RESTAURANT_PHONE, center_style))
    elements.append(Paragraph(RESTAURANT_GST, center_style))
    elements.append(Spacer(1, 8))

    meta_table = Table([
        [f"Bill No: {bill['bill_no']}", f"Date: {bill['created_at']}"],
        [f"Order Type: {bill['order_type']}", f"Cashier: {bill.get('cashier') or '-'}"],
    ], colWidths=[60 * mm, 60 * mm])
    meta_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 8))

    # Item table
    data = [["Item", "Price", "Qty", "Total"]]
    for item in bill["cart"]:
        data.append([
            item["name"],
            f"{item['price']:.2f}",
            str(item["qty"]),
            f"{item['price'] * item['qty']:.2f}",
        ])

    item_table = Table(data, colWidths=[55 * mm, 25 * mm, 15 * mm, 25 * mm])
    item_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0067C0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(item_table)
    elements.append(Spacer(1, 8))

    # Totals
    totals_data = [
        ["Subtotal", f"Rs. {bill['subtotal']:.2f}"],
        [f"Discount ({bill['discount_percent']}%)", f"- Rs. {bill['discount_amount']:.2f}"],
        [f"Tax / GST ({bill['tax_percent']}%)", f"+ Rs. {bill['tax_amount']:.2f}"],
        ["TOTAL", f"Rs. {bill['total']:.2f}"],
        ["Payment Mode", bill["payment_mode"]],
        ["Amount Received", f"Rs. {bill['amount_received']:.2f}"],
        ["Balance Returned", f"Rs. {bill['balance_returned']:.2f}"],
    ]
    totals_table = Table(totals_data, colWidths=[90 * mm, 30 * mm])
    totals_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("FONTNAME", (0, 3), (-1, 3), "Helvetica-Bold"),
        ("LINEABOVE", (0, 3), (-1, 3), 0.75, colors.black),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Thank you for dining with us! Visit again.", center_style))

    doc.build(elements)
    return filepath
