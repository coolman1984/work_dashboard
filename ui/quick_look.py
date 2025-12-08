import os
import customtkinter as ctk
from tkinter import ttk
from PIL import Image
from utils.files import open_path
from services.preview.excel_preview import get_excel_data

class QuickLookWindow(ctk.CTkToplevel):
    def __init__(self, parent, filepath):
        super().__init__(parent)
        self.title("Quick Look")
        self.geometry("900x600")
        self.filepath = filepath
        
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.lbl_title = ctk.CTkLabel(self.container, text=os.path.basename(filepath), font=("Segoe UI", 16, "bold"))
        self.lbl_title.pack(pady=(10, 5))
        
        self.load_preview()
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<space>", lambda e: self.destroy())
        self.focus_force()

    def load_preview(self):
        ext = os.path.splitext(self.filepath)[1].lower()
        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico']:
            try:
                img = Image.open(self.filepath)
                ratio = min(800 / img.width, 500 / img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                ctk_img = ctk.CTkImage(img, size=new_size)
                lbl = ctk.CTkLabel(self.container, text="", image=ctk_img)
                lbl.pack(fill="both", expand=True, pady=10)
            except Exception as e: ctk.CTkLabel(self.container, text=f"Error: {e}").pack()
        elif ext in ['.txt', '.py', '.json', '.md', '.csv', '.log', '.xml']:
            textbox = ctk.CTkTextbox(self.container, font=("Consolas", 14))
            textbox.pack(fill="both", expand=True)
            try:
                with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    textbox.insert("0.0", f.read(10000))
            except Exception as e: textbox.insert("0.0", str(e))
            textbox.configure(state="disabled")
        elif ext in ['.xlsx', '.xls']:
            try:
                cols, rows = get_excel_data(self.filepath)
                tree = ttk.Treeview(self.container, columns=cols, show="headings")
                for col in cols:
                    tree.heading(col, text=col)
                    tree.column(col, width=100)
                for row in rows:
                    tree.insert("", "end", values=row)
                tree.pack(fill="both", expand=True)
            except ImportError:
                ctk.CTkLabel(self.container, text="Install pandas/openpyxl to view Excel").pack(pady=50)
            except Exception as e:
                ctk.CTkLabel(self.container, text=str(e)).pack(pady=50)
        else:
            ctk.CTkButton(self.container, text="Open File", command=lambda: open_path(self.filepath)).pack(pady=50)
