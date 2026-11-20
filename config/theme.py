import customtkinter as ctk
COLORS = {
 "app":"#101820","sidebar":"#172630","header":"#1B2D38","panel":"#17232D",
 "card":"#14212B","border":"#2B414D","text":"#F2F6F8","muted":"#A8B7C0",
 "accent":"#16C7C9","accent_hover":"#10AEB2","blue":"#268BD2",
 "green":"#20B879","red":"#D9535D","yellow":"#E5B94C"
}
def apply_theme():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
