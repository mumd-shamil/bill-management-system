"""
ui/components.py
Shared style constants and small reusable widgets for a consistent look.
"""

import tkinter as tk
from tkinter import ttk

ACCENT = "#0067C0"
ACCENT_DARK = "#004C8C"
BG = "#F3F3F3"
CARD_BG = "#FFFFFF"
TEXT_DARK = "#1A1A1A"
FONT_FAMILY = "Segoe UI"


def apply_theme(root: tk.Tk):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    root.configure(bg=BG)

    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=CARD_BG, relief="flat")
    style.configure("TLabel", background=BG, foreground=TEXT_DARK, font=(FONT_FAMILY, 10))
    style.configure("Card.TLabel", background=CARD_BG, foreground=TEXT_DARK, font=(FONT_FAMILY, 10))
    style.configure("Heading.TLabel", background=BG, foreground=TEXT_DARK, font=(FONT_FAMILY, 18, "bold"))
    style.configure("CardHeading.TLabel", background=CARD_BG, foreground=TEXT_DARK, font=(FONT_FAMILY, 13, "bold"))
    style.configure("Accent.TButton", font=(FONT_FAMILY, 10, "bold"))
    style.configure("Treeview", font=(FONT_FAMILY, 9), rowheight=26)
    style.configure("Treeview.Heading", font=(FONT_FAMILY, 9, "bold"))
    style.configure("TNotebook.Tab", font=(FONT_FAMILY, 10, "bold"), padding=(12, 6))


def card(parent, **kwargs):
    frame = ttk.Frame(parent, style="Card.TFrame", padding=15, **kwargs)
    return frame


def primary_button(parent, text, command):
    btn = tk.Button(
        parent, text=text, command=command,
        bg=ACCENT, fg="white", activebackground=ACCENT_DARK, activeforeground="white",
        font=(FONT_FAMILY, 10, "bold"), relief="flat", padx=14, pady=8, cursor="hand2",
        borderwidth=0,
    )
    return btn


def secondary_button(parent, text, command):
    btn = tk.Button(
        parent, text=text, command=command,
        bg="#E5E5E5", fg=TEXT_DARK, activebackground="#D0D0D0",
        font=(FONT_FAMILY, 10), relief="flat", padx=14, pady=8, cursor="hand2",
        borderwidth=0,
    )
    return btn


def danger_button(parent, text, command):
    btn = tk.Button(
        parent, text=text, command=command,
        bg="#D13438", fg="white", activebackground="#A4262C", activeforeground="white",
        font=(FONT_FAMILY, 10, "bold"), relief="flat", padx=14, pady=8, cursor="hand2",
        borderwidth=0,
    )
    return btn
