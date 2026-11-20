import customtkinter as ctk
from config.theme import COLORS

def section_title(parent, title, subtitle=""):
    ctk.CTkLabel(parent, text=title, text_color=COLORS["text"],
        font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", pady=(0,4))
    if subtitle:
        ctk.CTkLabel(parent, text=subtitle, text_color=COLORS["muted"],
            font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0,16))

def make_card(parent, title, value, accent):
    card=ctk.CTkFrame(parent, fg_color=COLORS["card"], border_color=COLORS["border"],
        border_width=1, corner_radius=12)
    ctk.CTkLabel(card,text=title,text_color=COLORS["muted"],
        font=ctk.CTkFont(size=13)).pack(anchor="w",padx=16,pady=(14,3))
    ctk.CTkLabel(card,text=str(value),text_color=accent,
        font=ctk.CTkFont(size=27,weight="bold")).pack(anchor="w",padx=16,pady=(0,14))
    return card
