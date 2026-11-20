import sqlite3
from pathlib import Path
from tkinter import messagebox
import customtkinter as ctk
from config.theme import COLORS
from ui.components import section_title, make_card
from database.attendance import (get_session_summary, finish_session, get_classes,
    get_sections, get_sessions, start_new_session)
from face.live_attendance import run_live_attendance

DB_PATH=Path(__file__).resolve().parent.parent/"database"/"attendance.db"

class Dashboard:
    def __init__(self, app, teacher):
        self.app,self.teacher=app,teacher
        self.session_map={}
        self._shell()
        self.show_home()

    def _shell(self):
        for w in self.app.winfo_children(): w.destroy()
        self.app.title("AI Smart Attendance")
        self.app.geometry("1280x800"); self.app.minsize(1050,680)
        self.app.configure(fg_color=COLORS["app"])
        side=ctk.CTkFrame(self.app,width=220,corner_radius=0,fg_color=COLORS["sidebar"])
        side.pack(side="left",fill="y"); side.pack_propagate(False)
        brand=ctk.CTkFrame(side,fg_color="transparent"); brand.pack(fill="x",padx=16,pady=(25,28))
        ctk.CTkLabel(brand,text="◆",text_color=COLORS["accent"],font=ctk.CTkFont(size=28)).pack(side="left")
        ctk.CTkLabel(brand,text="AI Attendance",text_color=COLORS["text"],
            font=ctk.CTkFont(size=18,weight="bold")).pack(side="left",padx=8)
        for label,fn in [("⌂   Dashboard",self.show_home),("◷   Attendance",self.show_attendance),
                         ("▤   Students",self.open_students),("▦   Reports",self.show_reports)]:
            ctk.CTkButton(side,text=label,anchor="w",height=43,fg_color="transparent",
                hover_color="#263D49",text_color=COLORS["text"],command=fn).pack(fill="x",padx=12,pady=4)
        ctk.CTkButton(side,text="⇥   Logout",anchor="w",height=42,fg_color="transparent",
            hover_color="#472B32",text_color="#F08B91",command=self.logout).pack(side="bottom",fill="x",padx=12,pady=18)
        main=ctk.CTkFrame(self.app,fg_color=COLORS["app"],corner_radius=0); main.pack(side="left",fill="both",expand=True)
        head=ctk.CTkFrame(main,height=68,fg_color=COLORS["header"],corner_radius=0); head.pack(fill="x"); head.pack_propagate(False)
        ctk.CTkLabel(head,text="Attendance Management",font=ctk.CTkFont(size=18,weight="bold"),
            text_color=COLORS["text"]).pack(side="left",padx=26)
        ctk.CTkLabel(head,text=f"Teacher  /  {self.teacher}",text_color=COLORS["muted"]).pack(side="right",padx=26)
        self.content=ctk.CTkFrame(main,fg_color=COLORS["app"],corner_radius=0)
        self.content.pack(fill="both",expand=True,padx=26,pady=22)

    def clear(self):
        for w in self.content.winfo_children(): w.destroy()

    def query(self,sql,args=()):
        with sqlite3.connect(DB_PATH) as con: return con.execute(sql,args).fetchall()

    def show_home(self):
        self.clear(); section_title(self.content,"Dashboard","Overview of your attendance activity")
        try:
            vals=[
              ("Total Students",self.query("SELECT COUNT(*) FROM students")[0][0],COLORS["blue"]),
              ("Present Today",self.query("SELECT COUNT(*) FROM attendance WHERE date=date('now','localtime') AND status='Present'")[0][0],COLORS["green"]),
              ("Absent Today",self.query("SELECT COUNT(*) FROM attendance WHERE date=date('now','localtime') AND status='Absent'")[0][0],COLORS["red"]),
              ("Today's Sessions",self.query("SELECT COUNT(*) FROM attendance_sessions WHERE date=date('now','localtime')")[0][0],COLORS["accent"])]
        except sqlite3.Error as e:
            messagebox.showerror("Database",str(e)); vals=[(x,0,c) for x,c in [("Total Students",COLORS["blue"]),("Present Today",COLORS["green"]),("Absent Today",COLORS["red"]),("Today's Sessions",COLORS["accent"])]]
        row=ctk.CTkFrame(self.content,fg_color="transparent"); row.pack(fill="x",pady=(14,20))
        for title,value,color in vals: make_card(row,title,value,color).pack(side="left",fill="x",expand=True,padx=(0,10))
        panel=ctk.CTkFrame(self.content,fg_color=COLORS["panel"],border_color=COLORS["border"],border_width=1,corner_radius=12)
        panel.pack(fill="both",expand=True)
        ctk.CTkLabel(panel,text="Recent Attendance Sessions",font=ctk.CTkFont(size=17,weight="bold")).pack(anchor="w",padx=18,pady=16)
        rows=self.query("SELECT class_name,section,session_name,date,status FROM attendance_sessions ORDER BY id DESC LIMIT 8")
        if not rows: ctk.CTkLabel(panel,text="No sessions yet.",text_color=COLORS["muted"]).pack(anchor="w",padx=18)
        for cls,sec,name,date,status in rows:
            ctk.CTkLabel(panel,text=f"{cls} · {sec}     {name}     {date}     {status}",
                text_color=COLORS["text"]).pack(anchor="w",padx=20,pady=7)

    def show_attendance(self):
        self.clear(); section_title(self.content,"Attendance","Create or resume an attendance session")
        box=ctk.CTkFrame(self.content,fg_color=COLORS["panel"],border_color=COLORS["border"],border_width=1,corner_radius=12)
        box.pack(fill="x",pady=10); box.grid_columnconfigure((0,1),weight=1)
        classes=get_classes() or []
        self.class_box=ctk.CTkComboBox(box,values=classes or ["No classes"])
        self.class_box.grid(row=0,column=0,padx=16,pady=(18,8),sticky="ew")
        if classes:self.class_box.set(classes[0])
        self.section_box=ctk.CTkComboBox(box,values=["Select class"])
        self.section_box.grid(row=0,column=1,padx=16,pady=(18,8),sticky="ew")
        self.name_entry=ctk.CTkEntry(box,placeholder_text="Session name (e.g. DBMS Lecture 1)")
        self.name_entry.grid(row=1,column=0,padx=16,pady=8,sticky="ew")
        self.session_box=ctk.CTkComboBox(box,values=["No sessions"])
        self.session_box.grid(row=1,column=1,padx=16,pady=8,sticky="ew")
        self.class_box.configure(command=self.update_sections)
        self.section_box.configure(command=lambda _:self.refresh_sessions())
        if classes:self.update_sections(classes[0])
        actions=ctk.CTkFrame(box,fg_color="transparent"); actions.grid(row=2,column=0,columnspan=2,sticky="ew",padx=16,pady=(8,18))
        ctk.CTkButton(actions,text="Create Session",command=self.create_session).pack(side="left",padx=4)
        ctk.CTkButton(actions,text="Refresh",fg_color="#344B58",command=self.refresh_sessions).pack(side="left",padx=4)
        ctk.CTkButton(actions,text="Finish Session",fg_color=COLORS["red"],command=self.finish_session).pack(side="right",padx=4)
        ctk.CTkButton(actions,text="Start Camera",fg_color=COLORS["green"],command=self.start_camera).pack(side="right",padx=4)

    def update_sections(self,cls):
        sections=get_sections(cls) or []
        self.section_box.configure(values=sections or ["No sections"])
        self.section_box.set(sections[0] if sections else "No sections")
        self.refresh_sessions()

    def refresh_sessions(self):
        if not hasattr(self,"session_box"): return
        self.session_map={}; cls=self.class_box.get().strip(); sec=self.section_box.get().strip()
        if not cls or cls=="No classes" or not sec or sec=="No sections":
            self.session_box.configure(values=["No sessions"]); self.session_box.set("No sessions"); return
        rows=get_sessions(cls,sec) or []; labels=[]
        for r in rows:
            label=f"#{r[0]} · {r[1]} · {r[2]} · {r[6]}"; labels.append(label)
            self.session_map[label]={"id":r[0],"name":r[1],"status":r[6]}
        self.session_box.configure(values=labels or ["No sessions"]); self.session_box.set(labels[0] if labels else "No sessions")

    def create_session(self):
        cls,sec,name=self.class_box.get().strip(),self.section_box.get().strip(),self.name_entry.get().strip()
        if not cls or cls=="No classes" or not sec or sec=="No sections" or not name:
            messagebox.showwarning("Missing details","Select class and section, then enter a session name."); return
        sid=start_new_session(cls,sec,name,self.teacher)
        if not sid: messagebox.showerror("Session","Could not create session."); return
        messagebox.showinfo("Created",f"Attendance session #{sid} created.")
        self.name_entry.delete(0,"end"); self.refresh_sessions()

    def selected(self): return self.session_map.get(self.session_box.get())

    def start_camera(self):
        s=self.selected()
        if not s: messagebox.showwarning("Select session","Choose a session first."); return
        if s["status"]!="Active": messagebox.showwarning("Completed","Select an Active session."); return
        if not messagebox.askyesno("Start camera",f"Start {s['name']}?"): return
        try:
            self.app.withdraw(); run_live_attendance(s["id"])
        except Exception as e: messagebox.showerror("Camera error",str(e))
        finally: self.app.deiconify(); self.app.lift(); self.refresh_sessions()

    def finish_session(self):
        s=self.selected()
        if not s: messagebox.showwarning("Select session","Choose a session first."); return
        if s["status"]!="Active": messagebox.showwarning("Completed","Session already completed."); return
        summary=get_session_summary(s["id"])
        prompt=f"Total: {summary['total']}\nPresent: {summary['present']}\nPending: {summary['pending']}\n\nMark pending students absent and finish?"
        if messagebox.askyesno("Finish attendance",prompt):
            if finish_session(s["id"]): messagebox.showinfo("Completed","Session completed."); self.refresh_sessions()
            else: messagebox.showerror("Error","Could not finish session.")

    def show_reports(self):
        self.clear(); section_title(self.content,"Reports","Recent session records")
        rows=self.query("SELECT id,class_name,section,session_name,date,status FROM attendance_sessions ORDER BY id DESC LIMIT 100")
        if not rows: ctk.CTkLabel(self.content,text="No sessions available.",text_color=COLORS["muted"]).pack(anchor="w"); return
        for sid,cls,sec,name,date,status in rows:
            line=ctk.CTkFrame(self.content,fg_color=COLORS["panel"],corner_radius=9); line.pack(fill="x",pady=4)
            ctk.CTkLabel(line,text=f"#{sid}  {cls}/{sec}  ·  {name}  ·  {date}  ·  {status}").pack(side="left",padx=14,pady=12)
            ctk.CTkButton(line,text="View",width=75,command=lambda i=sid:self.view_report(i)).pack(side="right",padx=10,pady=7)

    def view_report(self,sid):
        rows=self.query("SELECT roll_number,student_name,class_name,date,time,status FROM attendance WHERE session_id=? ORDER BY roll_number",(sid,))
        win=ctk.CTkToplevel(self.app); win.title(f"Report · {sid}"); win.geometry("850x500")
        text=ctk.CTkTextbox(win,font=ctk.CTkFont(family="Consolas",size=13)); text.pack(fill="both",expand=True,padx=16,pady=16)
        text.insert("end","ROLL       STUDENT                    CLASS             DATE         TIME       STATUS\n")
        for r in rows:text.insert("end",f"{str(r[0]):10} {str(r[1]):26} {str(r[2]):17} {str(r[3]):12} {str(r[4]):10} {r[5]}\n")
        text.configure(state="disabled")

    def open_students(self):
        try:
            from ui.student_registration import open_student_registration
            open_student_registration(self.app)
        except Exception as e: messagebox.showerror("Students",str(e))

    def logout(self):
        if messagebox.askyesno("Logout","Close the attendance system?"): self.app.destroy()

def open_dashboard(app,teacher_name): Dashboard(app,teacher_name)
