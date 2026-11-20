import sqlite3
from pathlib import Path
from tkinter import messagebox
from datetime import datetime

import customtkinter as ctk

from config.theme import apply_theme
from ui.dashboard import open_dashboard


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "attendance.db"
CLASSROOM_IMAGE = BASE_DIR / "assets\CCTV Classroom Study Session.png"


# ---------------------------------------------------------
# DESIGN TOKENS
# ---------------------------------------------------------
NAVY_900 = "#071733"      # left panel background
NAVY_800 = "#0D2147"      # raised surfaces on the left
NAVY_700 = "#16305E"      # borders on the left
ACCENT = "#38BDF8"        # highlight on dark
PRIMARY = "#2563EB"       # buttons / links
PRIMARY_HOVER = "#1D4ED8"
INK = "#0F172A"           # main text
MUTED = "#64748B"         # secondary text
SUBTLE = "#94A3B8"        # placeholder / hints
LINE = "#E2E8F0"          # borders
FIELD_BG = "#F8FAFC"
WHITE = "#FFFFFF"

FONT = "Segoe UI"         # falls back automatically on other systems


def font(size, weight="normal"):
    return ctk.CTkFont(family=FONT, size=size, weight=weight)


# ---------------------------------------------------------
# DATABASE LOGIN (unchanged)
# ---------------------------------------------------------
def check_login(username, password):
    with sqlite3.connect(DB_PATH) as con:
        return con.execute(
            """
            SELECT id, username, name
            FROM teachers
            WHERE username = ? AND password = ?
            """,
            (username, password)
        ).fetchone()


# ---------------------------------------------------------
# IMAGE HELPERS
# ---------------------------------------------------------
def build_hero_image(size):
    """Cover-crop the classroom photo to `size` with rounded corners and a
    soft dark gradient at the bottom. Falls back to a generated gradient."""
    try:
        from PIL import Image, ImageDraw
    except Exception:
        return None

    w, h = size
    scale = 2  # render at 2x for crisp edges
    W, H = w * scale, h * scale

    img = None
    if CLASSROOM_IMAGE.exists():
        try:
            src = Image.open(CLASSROOM_IMAGE).convert("RGB")
            ratio = max(W / src.width, H / src.height)
            resized = src.resize(
                (int(src.width * ratio), int(src.height * ratio)),
                Image.LANCZOS
            )
            left = (resized.width - W) // 2
            top = (resized.height - H) // 2
            img = resized.crop((left, top, left + W, top + H))
        except Exception as error:
            print("Classroom image could not be loaded:", error)

    if img is None:
        img = Image.new("RGB", (W, H), "#123A7A")
        px = ImageDraw.Draw(img)
        for y in range(H):
            t = y / H
            r = int(18 + 20 * t)
            g = int(58 + 60 * t)
            b = int(122 + 60 * t)
            px.line([(0, y), (W, y)], fill=(r, g, b))

    # Bottom gradient overlay for depth
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    start = int(H * 0.45)
    for y in range(start, H):
        alpha = int(190 * ((y - start) / (H - start)) ** 1.6)
        od.line([(0, y), (W, y)], fill=(7, 23, 51, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), overlay)

    # Rounded corners
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, W, H), radius=22 * scale, fill=255
    )
    img.putalpha(mask)
    return ctk.CTkImage(light_image=img, dark_image=img, size=size)


# ---------------------------------------------------------
# LOGIN WINDOW
# ---------------------------------------------------------
def main():
    apply_theme()
    ctk.set_appearance_mode("light")

    app = ctk.CTk()
    app.title("AI Smart Attendance System | Teacher Login")
    app.geometry("1240x760")
    app.minsize(1040, 660)
    app.configure(fg_color=WHITE)

    root = ctk.CTkFrame(app, fg_color=WHITE, corner_radius=0)
    root.pack(fill="both", expand=True)
    root.grid_columnconfigure(0, weight=11, uniform="cols")
    root.grid_columnconfigure(1, weight=9, uniform="cols")
    root.grid_rowconfigure(0, weight=1)

    # =====================================================
    # LEFT PANEL - BRAND + HERO
    # =====================================================
    left = ctk.CTkFrame(root, fg_color=NAVY_900, corner_radius=0)
    left.grid(row=0, column=0, sticky="nsew")
    left.grid_columnconfigure(0, weight=1)
    left.grid_rowconfigure(2, weight=1)

    # Logo row
    logo_row = ctk.CTkFrame(left, fg_color="transparent")
    logo_row.grid(row=0, column=0, sticky="w", padx=52, pady=(44, 0))

    logo_mark = ctk.CTkFrame(
        logo_row, width=42, height=42, corner_radius=12, fg_color=PRIMARY
    )
    logo_mark.pack(side="left")
    logo_mark.pack_propagate(False)
    ctk.CTkLabel(
        logo_mark, text="◆", text_color=WHITE, font=font(18, "bold")
    ).place(relx=0.5, rely=0.5, anchor="center")

    logo_text = ctk.CTkFrame(logo_row, fg_color="transparent")
    logo_text.pack(side="left", padx=(12, 0))
    ctk.CTkLabel(
        logo_text, text="AI Smart Attendance",
        text_color=WHITE, font=font(15, "bold")
    ).pack(anchor="w")
    ctk.CTkLabel(
        logo_text, text="TEACHER PORTAL",
        text_color=ACCENT, font=font(9, "bold")
    ).pack(anchor="w")

    # Headline
    head = ctk.CTkFrame(left, fg_color="transparent")
    head.grid(row=1, column=0, sticky="w", padx=52, pady=(46, 0))

    ctk.CTkLabel(
        head, text="Attendance that\ntakes itself.",
        text_color=WHITE, font=font(40, "bold"), justify="left"
    ).pack(anchor="w")
    ctk.CTkLabel(
        head,
        text="Face recognition marks your class in seconds,\n"
             "so you can spend your time teaching.",
        text_color="#9FB3D1", font=font(14), justify="left"
    ).pack(anchor="w", pady=(14, 0))

    # Hero image
    hero_wrap = ctk.CTkFrame(left, fg_color="transparent")
    hero_wrap.grid(row=2, column=0, sticky="nsew", padx=52, pady=(30, 0))
    hero_wrap.grid_columnconfigure(0, weight=1)
    hero_wrap.grid_rowconfigure(0, weight=1)

    hero_img = build_hero_image((560, 250))
    if hero_img is not None:
        hero_label = ctk.CTkLabel(hero_wrap, text="", image=hero_img)
        hero_label.image = hero_img
        hero_label.grid(row=0, column=0, sticky="nw")

        # Floating "live" chip over the image
        chip = ctk.CTkFrame(
            hero_wrap, fg_color=NAVY_900, corner_radius=20,
            border_width=1, border_color=NAVY_700
        )
        chip.place(x=18, y=18)
        ctk.CTkLabel(
            chip, text="●  Live recognition",
            text_color="#4ADE80", font=font(11, "bold")
        ).pack(padx=14, pady=6)
    else:
        fallback = ctk.CTkFrame(
            hero_wrap, fg_color=NAVY_800, corner_radius=22,
            border_width=1, border_color=NAVY_700
        )
        fallback.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(
            fallback, text="🎓", font=font(72)
        ).place(relx=0.5, rely=0.5, anchor="center")

    # Feature trio
    features = ctk.CTkFrame(left, fg_color="transparent")
    features.grid(row=3, column=0, sticky="ew", padx=52, pady=(22, 40))
    features.grid_columnconfigure((0, 1, 2), weight=1, uniform="feat")

    for col, (icon, title, desc) in enumerate([
        ("◉", "Face Recognition", "Instant & accurate"),
        ("◷", "Live Attendance", "Updates in real time"),
        ("▤", "Detailed Reports", "Export anytime"),
    ]):
        tile = ctk.CTkFrame(
            features, fg_color=NAVY_800, corner_radius=14,
            border_width=1, border_color=NAVY_700
        )
        tile.grid(row=0, column=col, sticky="nsew",
                  padx=(0 if col == 0 else 6, 0 if col == 2 else 6))
        ctk.CTkLabel(
            tile, text=icon, text_color=ACCENT, font=font(18, "bold")
        ).pack(anchor="w", padx=16, pady=(14, 0))
        ctk.CTkLabel(
            tile, text=title, text_color=WHITE, font=font(12, "bold")
        ).pack(anchor="w", padx=16, pady=(6, 0))
        ctk.CTkLabel(
            tile, text=desc, text_color="#8CA3C7", font=font(10)
        ).pack(anchor="w", padx=16, pady=(1, 14))

    # =====================================================
    # RIGHT PANEL - SIGN IN
    # =====================================================
    right = ctk.CTkFrame(root, fg_color=WHITE, corner_radius=0)
    right.grid(row=0, column=1, sticky="nsew")
    right.grid_columnconfigure(0, weight=1)
    right.grid_rowconfigure(1, weight=1)

    # Top-right clock
    top = ctk.CTkFrame(right, fg_color="transparent", height=60)
    top.grid(row=0, column=0, sticky="ew", padx=44, pady=(26, 0))
    clock_label = ctk.CTkLabel(
        top, text="", text_color=SUBTLE, font=font(12)
    )
    clock_label.pack(side="right")

    def update_clock():
        if not app.winfo_exists():
            return
        clock_label.configure(
            text=datetime.now().strftime("%I:%M %p   ·   %d %b %Y")
        )
        app.after(1000, update_clock)

    update_clock()

    # Centered form column
    holder = ctk.CTkFrame(right, fg_color="transparent")
    holder.grid(row=1, column=0)
    form = ctk.CTkFrame(holder, fg_color="transparent", width=380)
    form.pack()

    ctk.CTkLabel(
        form, text="Welcome back 👋",
        text_color=INK, font=font(30, "bold")
    ).pack(anchor="w")
    ctk.CTkLabel(
        form, text="Sign in to manage your classes and attendance.",
        text_color=MUTED, font=font(13)
    ).pack(anchor="w", pady=(8, 34))

    # ---- Field factory: bordered wrapper with focus ring ----
    def make_field(parent, label, placeholder, secret=False):
        ctk.CTkLabel(
            parent, text=label, text_color="#334155", font=font(12, "bold")
        ).pack(anchor="w", pady=(0, 7))

        wrap = ctk.CTkFrame(
            parent, height=50, width=380, corner_radius=12,
            fg_color=FIELD_BG, border_width=1, border_color=LINE
        )
        wrap.pack(fill="x", pady=(0, 20))
        wrap.pack_propagate(False)

        entry = ctk.CTkEntry(
            wrap, height=46, corner_radius=10, border_width=0,
            fg_color="transparent", text_color=INK,
            placeholder_text=placeholder, placeholder_text_color=SUBTLE,
            font=font(14), show="•" if secret else ""
        )
        entry.pack(side="left", fill="both", expand=True, padx=(12, 4), pady=2)

        def focus_in(_e):
            wrap.configure(border_color=PRIMARY, fg_color=WHITE, border_width=2)

        def focus_out(_e):
            wrap.configure(border_color=LINE, fg_color=FIELD_BG, border_width=1)

        entry.bind("<FocusIn>", focus_in, add="+")
        entry.bind("<FocusOut>", focus_out, add="+")
        return wrap, entry

    # Username
    _, user = make_field(form, "Username", "Enter your username")

    # Password + show/hide inside the field
    pwd_wrap, pwd = make_field(
        form, "Password", "Enter your password", secret=True
    )

    password_visible = False

    def toggle_password():
        nonlocal password_visible
        password_visible = not password_visible
        pwd.configure(show="" if password_visible else "•")
        show_button.configure(text="Hide" if password_visible else "Show")

    show_button = ctk.CTkButton(
        pwd_wrap, text="Show", width=52, height=30, corner_radius=8,
        fg_color="transparent", hover_color=LINE, text_color=PRIMARY,
        font=font(12, "bold"), command=toggle_password
    )
    show_button.pack(side="right", padx=(0, 8))

    # Remember me + Forgot password
    options = ctk.CTkFrame(form, fg_color="transparent")
    options.pack(fill="x", pady=(0, 26))

    remember_var = ctk.BooleanVar(value=False)  # UI only, saves nothing
    ctk.CTkCheckBox(
        options, text="Remember me", variable=remember_var,
        text_color=MUTED, fg_color=PRIMARY, hover_color=PRIMARY_HOVER,
        border_color="#CBD5E1", border_width=2, corner_radius=5,
        checkbox_width=18, checkbox_height=18, font=font(12)
    ).pack(side="left")

    def forgot():
        messagebox.showinfo(
            "Forgot password",
            "Please contact your system administrator to reset "
            "your password.",
            parent=app
        )

    forgot_label = ctk.CTkLabel(
        options, text="Forgot password?", text_color=PRIMARY,
        font=font(12, "bold"), cursor="hand2"
    )
    forgot_label.pack(side="right")
    forgot_label.bind("<Button-1>", lambda e: forgot())

    # ---- Login action (logic unchanged) ----
    def login(event=None):
        username = user.get().strip()
        password = pwd.get()

        if not username or not password:
            messagebox.showwarning(
                "Missing details",
                "Please enter both username and password.",
                parent=app
            )
            return

        try:
            teacher = check_login(username, password)
        except sqlite3.Error as error:
            messagebox.showerror("Database error", str(error), parent=app)
            return

        if teacher:
            open_dashboard(app, teacher[2])
        else:
            messagebox.showerror(
                "Login failed", "Invalid username or password.", parent=app
            )
            pwd.delete(0, "end")
            pwd.focus()

    ctk.CTkButton(
        form, text="Sign in   →", height=52, corner_radius=12,
        fg_color=PRIMARY, hover_color=PRIMARY_HOVER, text_color=WHITE,
        font=font(15, "bold"), command=login
    ).pack(fill="x")

    # Security note
    note = ctk.CTkFrame(
        form, fg_color="#F1F5F9", corner_radius=12
    )
    note.pack(fill="x", pady=(24, 0))
    ctk.CTkLabel(
        note, text="🔒", font=font(14)
    ).pack(side="left", padx=(14, 8), pady=12)
    ctk.CTkLabel(
        note,
        text="Secure access. Your account is protected\n"
             "and activity is monitored.",
        text_color=MUTED, font=font(11), justify="left"
    ).pack(side="left", pady=10)

    # Footer
    footer = ctk.CTkLabel(
        right, text="Need help?  Contact your system administrator",
        text_color=SUBTLE, font=font(11)
    )
    footer.grid(row=2, column=0, pady=(0, 26))

    # Keyboard support
    app.bind("<Return>", login)
    user.focus()
    app.mainloop()


if __name__ == "__main__":
    main()