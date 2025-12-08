import os
import json
import shutil
import math
import datetime
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image

# Try importing optional libraries for Quick Look
try:
    import pandas as pd
except ImportError:
    pd = None

# --- Configuration ---
CONFIG_FILE = "dashboard_config.json"

# Professional Palette
ACCENT_COLORS = [
    "#0078D4", "#107C10", "#5C2D91", "#D83B01", "#C43E1C", "#004E8C", "#008272", "#986F0B", "#2B88D8"
]

THEMES = {
    "Dark": {"mode": "Dark", "bg": "#202020", "card": "#2c2c2c", "text": "#ffffff", "subtext": "#a0a0a0", "hover": "#3a3a3a"},
    "Light": {"mode": "Light", "bg": "#f3f3f3", "card": "#ffffff", "text": "#1a1a1a", "subtext": "#505050", "hover": "#e5e5e5"},
}

# File Type Colors for Analytics
TYPE_COLORS = {
    '.xlsx': '#107C10', '.xlsm': '#107C10', '.xls': '#107C10', '.csv': '#185118', # Excel (Green)
    '.pdf': '#D00000',                                                          # PDF (Red)
    '.docx': '#2B579A', '.doc': '#2B579A',                                      # Word (Blue)
    '.png': '#B146C2', '.jpg': '#B146C2', '.jpeg': '#B146C2',                   # Images (Purple)
    '.py': '#ECE05D', '.js': '#ECE05D', '.html': '#E34F26',                     # Code (Yellow/Orange)
    '.txt': '#888888', '.md': '#888888', '.log': '#AAAAAA'                      # Text (Gray)
}
DEFAULT_TYPE_COLOR = "#555555"

class ConfigManager:
    @staticmethod
    def load_config():
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f: return json.load(f)
            except: return {"workspaces": {}}
        return {"workspaces": {}}

    @staticmethod
    def save_config(data):
        try:
            with open(CONFIG_FILE, 'w') as f: json.dump(data, f)
        except Exception as e: print(f"Error saving config: {e}")

# --- Utilities ---
def open_path(path):
    try: os.startfile(path)
    except OSError as e: messagebox.showerror("Error", f"Could not open path:\n{e}")

def get_file_info(filepath):
    try:
        stats = os.stat(filepath)
        size_mb = stats.st_size / (1024 * 1024)
        mod_time = datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M')
        return stats.st_size, size_mb, mod_time
    except: return 0, 0.0, "Unknown"

# --- Quick Look Window ---
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
            if pd is None:
                ctk.CTkLabel(self.container, text="Install pandas/openpyxl to view Excel").pack(pady=50)
                return
            try:
                engine = 'openpyxl' if ext == '.xlsx' else None
                df = pd.read_excel(self.filepath, engine=engine, nrows=50)
                cols = list(df.columns)
                tree = ttk.Treeview(self.container, columns=cols, show="headings")
                for col in cols:
                    tree.heading(col, text=col)
                    tree.column(col, width=100)
                for index, row in df.iterrows():
                    tree.insert("", "end", values=list(row))
                tree.pack(fill="both", expand=True)
            except Exception as e: ctk.CTkLabel(self.container, text=str(e)).pack(pady=50)
        else:
            ctk.CTkButton(self.container, text="Open File", command=lambda: open_path(self.filepath)).pack(pady=50)

# --- Clipboard & Watchdog ---
class InternalClipboard:
    file_path = None; operation = None; source_panel = None
    @classmethod
    def set(cls, path, op, panel): cls.file_path = path; cls.operation = op; cls.source_panel = panel
    @classmethod
    def get(cls): return cls.file_path, cls.operation
    @classmethod
    def clear(cls): 
        if cls.source_panel: cls.source_panel.clear_clipboard_indicator()
        cls.file_path = None; cls.operation = None; cls.source_panel = None
    @classmethod
    def has_data(cls): return cls.file_path is not None

class FolderChangeHandler(FileSystemEventHandler):
    def __init__(self, callback): self.callback = callback; self.last_refresh = 0
    def on_any_event(self, event):
        if time.time() - self.last_refresh > 1.0: self.callback(); self.last_refresh = time.time()

# --- The Modern Folder Card ---
class FolderCard(ctk.CTkFrame):
    def __init__(self, parent, panel_id, accent_color, config_data, save_callback, get_panels_callback, app_theme_data, base_font_size, toggle_focus_callback, is_focused=False):
        # ZERO WASTE: Corner radius reduced, border 0
        super().__init__(parent, corner_radius=4, border_width=0, fg_color=app_theme_data["card"])
        
        self.panel_id = str(panel_id)
        self.config_data = config_data
        self.save_callback = save_callback
        self.get_panels_callback = get_panels_callback
        self.current_path = self.config_data.get(self.panel_id, "")
        self.accent_color = accent_color
        self.theme_data = app_theme_data
        self.base_font_size = base_font_size
        self.toggle_focus_callback = toggle_focus_callback
        self.is_focused = is_focused
        self.observer = None
        self.clipboard_indicator = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1) 

        # 1. Accent
        self.accent_strip = ctk.CTkFrame(self, height=4, corner_radius=0, fg_color=self.accent_color)
        self.accent_strip.grid(row=0, column=0, sticky="ew")

        # 2. Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=(6, 2))
        
        self.title_label = ctk.CTkLabel(self.header_frame, text=f"Folder {panel_id}", 
                                        text_color=self.accent_color, 
                                        font=("Segoe UI", self.base_font_size + 6, "bold"))
        self.title_label.pack(side="left", anchor="w")
        
        self.path_label = ctk.CTkLabel(self.header_frame, text="Select a folder...", 
                                       text_color=self.theme_data["subtext"], 
                                       font=("Segoe UI", self.base_font_size - 2))
        self.path_label.pack(side="left", padx=10, anchor="w")

        # Focus Button
        btn_txt = "✕" if self.is_focused else "⛶"
        self.btn_focus = ctk.CTkButton(self.header_frame, text=btn_txt, width=30, height=24,
                                       command=lambda: self.toggle_focus_callback(self.panel_id),
                                       font=("Segoe UI", self.base_font_size, "bold"),
                                       fg_color="transparent", border_width=1, 
                                       border_color=self.theme_data["subtext"], text_color=self.theme_data["text"])
        self.btn_focus.pack(side="right", padx=0)

        # 3. Controls
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=(2, 5))
        
        self.btn_browse = ctk.CTkButton(self.controls_frame, text="📂 Change", 
                                      command=self.browse_folder, 
                                      font=("Segoe UI", self.base_font_size, "bold"), 
                                      height=30, corner_radius=6,
                                      fg_color=self.accent_color, text_color="#ffffff")
        self.btn_browse.pack(side="left", padx=(0, 5))
        
        self.btn_open_folder = ctk.CTkButton(self.controls_frame, text="↗ Open", 
                                             command=self.open_current_folder, 
                                             font=("Segoe UI", self.base_font_size), 
                                             height=30, corner_radius=6,
                                             fg_color=self.theme_data["bg"], text_color=self.theme_data["text"],
                                             hover_color=self.theme_data["hover"])
        self.btn_open_folder.pack(side="left")

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_files())
        self.search_entry = ctk.CTkEntry(self.controls_frame, textvariable=self.search_var, 
                                       width=140, height=30, 
                                       placeholder_text="🔍 Search...", 
                                       font=("Segoe UI", self.base_font_size), 
                                       corner_radius=6, border_width=1)
        self.search_entry.pack(side="right")

        self.filter_var = ctk.StringVar(value="All Types")
        self.filter_combo = ctk.CTkComboBox(self.controls_frame, variable=self.filter_var, 
                                          width=110, height=30,
                                          values=['All Types', 'Excel', 'PDF', 'Word', 'Images', 'Text'],
                                          command=self.refresh_files, 
                                          font=("Segoe UI", self.base_font_size), 
                                          dropdown_font=("Segoe UI", self.base_font_size),
                                          corner_radius=6, border_width=1)
        self.filter_combo.pack(side="right", padx=5)

        # 4. Treeview
        self.tree_container = ctk.CTkFrame(self, fg_color="transparent")
        self.tree_container.grid(row=3, column=0, sticky="nsew", padx=2, pady=(0, 2))
        
        self.create_treeview_widget()
        
        # 5. Analytics / Stats Bar (IMPROVED)
        self.analytics_frame = ctk.CTkFrame(self, height=40, corner_radius=0, fg_color="transparent")
        self.analytics_frame.grid(row=4, column=0, sticky="ew", padx=5, pady=(2, 5))
        
        # Thicker Canvas for better visibility (8px)
        self.stats_canvas = tk.Canvas(self.analytics_frame, height=8, bg=self.theme_data["bg"], highlightthickness=0)
        self.stats_canvas.pack(fill="x", pady=(0, 4))
        
        # Larger Font for readability
        self.stats_label = ctk.CTkLabel(self.analytics_frame, text="--", 
                                        font=("Segoe UI", self.base_font_size - 2, "bold"), 
                                        text_color=self.theme_data["subtext"])
        self.stats_label.pack(anchor="e")

        if self.current_path:
            self.update_header()
            self.refresh_files()
            self.start_watchdog()

        # Bindings
        self.tree.bind("<Control-c>", lambda e: self.copy_selected())
        self.tree.bind("<Control-x>", lambda e: self.cut_selected())
        self.tree.bind("<Control-v>", lambda e: self.paste_file())
        self.tree.bind("<Delete>", lambda e: self.delete_selected())
        self.tree.bind("<F5>", lambda e: self.refresh_files())
        self.tree.bind("<space>", lambda e: self.quick_look())

    def update_font_size(self, new_size):
        self.base_font_size = new_size
        self.title_label.configure(font=("Segoe UI", new_size + 6, "bold"))
        self.path_label.configure(font=("Segoe UI", new_size - 2))
        self.btn_browse.configure(font=("Segoe UI", new_size, "bold"), height=int(new_size*2.0))
        self.btn_open_folder.configure(font=("Segoe UI", new_size), height=int(new_size*2.0))
        self.search_entry.configure(font=("Segoe UI", new_size), height=int(new_size*2.0))
        self.filter_combo.configure(font=("Segoe UI", new_size), dropdown_font=("Segoe UI", new_size), height=int(new_size*2.0))
        self.btn_focus.configure(font=("Segoe UI", new_size, "bold"))
        self.stats_label.configure(font=("Segoe UI", new_size - 2, "bold"))

    def create_treeview_widget(self):
        columns = ("name", "size", "date")
        self.tree = ttk.Treeview(self.tree_container, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("name", text="Name", command=lambda: self.sort_tree("name", False))
        self.tree.heading("size", text="Size", command=lambda: self.sort_tree("size", False))
        self.tree.heading("date", text="Date", command=lambda: self.sort_tree("date", False))
        
        self.tree.column("name", width=300, stretch=True) 
        self.tree.column("size", width=100, anchor="e", stretch=False)
        self.tree.column("date", width=160, anchor="center", stretch=False)
        
        vsb = ttk.Scrollbar(self.tree_container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-3>", self.on_right_click)

    def quick_look(self):
        item = self.tree.selection()
        if item:
            fname = self.tree.item(item, "values")[0]
            fpath = os.path.join(self.current_path, fname)
            if os.path.exists(fpath): QuickLookWindow(self, fpath)

    def update_header(self):
        if self.current_path and os.path.exists(self.current_path):
            folder_name = os.path.basename(self.current_path)
            if not folder_name: folder_name = self.current_path
            self.title_label.configure(text=folder_name)
            short_path = self.current_path if len(self.current_path) < 40 else "..." + self.current_path[-40:]
            self.path_label.configure(text=short_path)
        else:
            self.title_label.configure(text=f"Folder {self.panel_id}")
            self.path_label.configure(text="Empty")

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.current_path = folder
            self.config_data[self.panel_id] = folder
            self.save_callback()
            self.update_header()
            self.refresh_files()
            self.start_watchdog()

    def start_watchdog(self):
        if self.observer: self.observer.stop(); self.observer.join()
        if self.current_path and os.path.exists(self.current_path):
            self.observer = Observer()
            event_handler = FolderChangeHandler(lambda: self.after(100, self.refresh_files))
            self.observer.schedule(event_handler, self.current_path, recursive=False)
            self.observer.start()

    def open_current_folder(self):
        if self.current_path and os.path.exists(self.current_path): open_path(self.current_path)

    def get_extensions(self):
        selection = self.filter_var.get()
        if "Excel" in selection: return ['.xlsx', '.xlsm', '.xls', '.csv']
        if "PDF" in selection: return ['.pdf']
        if "Word" in selection: return ['.docx', '.doc']
        if "Images" in selection: return ['.jpg', '.jpeg', '.png', '.gif']
        if "Text" in selection: return ['.txt', '.md', '.log']
        return []

    def update_analytics(self, files_data):
        # Calculate stats
        total_files = len(files_data)
        total_size_bytes = sum(f[3] for f in files_data) # f[3] is raw bytes
        total_size_mb = total_size_bytes / (1024 * 1024)
        
        # Type distribution
        type_counts = {}
        for f in files_data:
            ext = os.path.splitext(f[0])[1].lower()
            type_counts[ext] = type_counts.get(ext, 0) + 1

        # --- IMPROVED MEANING: Create a descriptive string ---
        # Sort types by frequency to show top items
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Build text: "X Files (Y MB) • 5 Excel, 3 PDF..."
        # Now showing ALL types instead of just top 3
        type_str = ", ".join([f"{count} {ext.replace('.', '').upper()}" for ext, count in sorted_types])
        
        # Added separators for thousands (e.g., 6,485.10 MB)
        display_text = f"{total_files} Files ({total_size_mb:,.2f} MB)"
        if type_str:
            display_text += f"  •  {type_str}"

        self.stats_label.configure(text=display_text)
        
        # Update Visual Bar
        self.stats_canvas.delete("all")
        if total_files == 0: return

        width = self.stats_canvas.winfo_width()
        # Fallback if not yet drawn
        if width < 10: width = 300 
        
        current_x = 0
        # Draw segments matching the sorted top types
        for ext, count in sorted_types:
            color = TYPE_COLORS.get(ext, DEFAULT_TYPE_COLOR)
            segment_width = (count / total_files) * width
            # Draw rectangle with 8px height
            self.stats_canvas.create_rectangle(current_x, 0, current_x + segment_width, 8, fill=color, outline="")
            current_x += segment_width

    def refresh_files(self, _=None):
        for item in self.tree.get_children(): self.tree.delete(item)
        if not self.current_path or not os.path.exists(self.current_path):
            self.update_header()
            self.update_analytics([])
            return
        self.update_header()
        valid_exts = self.get_extensions()
        search_term = self.search_var.get().lower()
        
        files_data = [] # Store for analytics: (name, size_str, date, size_bytes)
        
        try:
            files = os.listdir(self.current_path)
            files.sort(key=str.lower)
            for f in files:
                full_path = os.path.join(self.current_path, f)
                if os.path.isfile(full_path):
                    ext = os.path.splitext(f)[1].lower()
                    if valid_exts and ext not in valid_exts: continue
                    if search_term and search_term not in f.lower(): continue
                    
                    raw_size, size_mb, mod = get_file_info(full_path)
                    size_str = f"{size_mb:.2f} MB"
                    
                    files_data.append((f, size_str, mod, raw_size))
                    self.tree.insert("", "end", values=(f, size_str, mod), tags=(full_path,))
        except: pass
        
        self.update_analytics(files_data)

    def on_double_click(self, event):
        item = self.tree.selection()
        if item: open_path(os.path.join(self.current_path, self.tree.item(item, "values")[0]))

    def on_right_click(self, event):
        item = self.tree.identify_row(event.y)
        menu = tk.Menu(self, tearoff=0, font=("Segoe UI", 12))
        if item:
            self.tree.selection_set(item)
            file_name = self.tree.item(item, "values")[0]
            menu.add_command(label="Open", command=lambda: open_path(os.path.join(self.current_path, file_name)))
            menu.add_separator()
            menu.add_command(label="Copy", command=lambda: self.copy_file(file_name))
            menu.add_command(label="Cut", command=lambda: self.cut_file(file_name))
            menu.add_separator()
            menu.add_command(label="Rename", command=lambda: self.rename_file(file_name))
            menu.add_command(label="Delete", command=lambda: self.delete_file(file_name))
            
            move_menu = tk.Menu(menu, tearoff=0, font=("Segoe UI", 12))
            panels = self.get_panels_callback()
            added = False
            for p in panels:
                if p != self and p.current_path:
                    move_menu.add_command(label=p.title_label.cget("text"), command=lambda t=p: self.move_file(file_name, t))
                    added = True
            if added:
                menu.add_separator()
                menu.add_cascade(label="Move To...", menu=move_menu)
        
        if InternalClipboard.has_data():
            if item: menu.add_separator()
            path, op = InternalClipboard.get()
            fname = os.path.basename(path)
            menu.add_command(label=f"Paste '{fname}'", command=self.paste_file)
        menu.tk_popup(event.x_root, event.y_root)

    # Operations
    def copy_selected(self): self.copy_file(self.tree.item(self.tree.selection(), "values")[0])
    def cut_selected(self): self.cut_file(self.tree.item(self.tree.selection(), "values")[0])
    def delete_selected(self): self.delete_file(self.tree.item(self.tree.selection(), "values")[0])
    def copy_file(self, f): InternalClipboard.set(os.path.join(self.current_path, f), 'copy', self); self.show_indicator("Copied")
    def cut_file(self, f): InternalClipboard.set(os.path.join(self.current_path, f), 'cut', self); self.show_indicator("Cut")
    def show_indicator(self, t):
        if self.clipboard_indicator: self.clipboard_indicator.destroy()
        self.clipboard_indicator = ctk.CTkLabel(self.header_frame, text=t, text_color=self.accent_color, font=("Segoe UI", self.base_font_size, "bold"))
        self.clipboard_indicator.pack(side="right", padx=5)
    def clear_clipboard_indicator(self):
        if self.clipboard_indicator: self.clipboard_indicator.destroy(); self.clipboard_indicator = None
    def paste_file(self):
        src, op = InternalClipboard.get()
        if not src or not os.path.exists(src): return
        try:
            dest = os.path.join(self.current_path, os.path.basename(src))
            if op == 'copy': shutil.copy2(src, dest)
            elif op == 'cut': shutil.move(src, dest); InternalClipboard.clear()
        except Exception as e: messagebox.showerror("Error", str(e))
    def rename_file(self, f):
        dialog = ctk.CTkInputDialog(text="New name:", title="Rename")
        n = dialog.get_input()
        if n:
            try: os.rename(os.path.join(self.current_path, f), os.path.join(self.current_path, n)); self.refresh_files()
            except Exception as e: messagebox.showerror("Error", str(e))
    def delete_file(self, f):
        if messagebox.askyesno("Delete", f"Delete {f}?"):
            try: os.remove(os.path.join(self.current_path, f))
            except Exception as e: messagebox.showerror("Error", str(e))
    def move_file(self, f, t):
        try: shutil.move(os.path.join(self.current_path, f), os.path.join(t.current_path, f))
        except Exception as e: messagebox.showerror("Error", str(e))
    def sort_tree(self, c, r):
        l = [(self.tree.set(k, c), k) for k in self.tree.get_children('')]
        if c == "size": l.sort(key=lambda x: float(x[0].split()[0]) if x[0] else 0, reverse=r)
        else: l.sort(reverse=r)
        for i, (v, k) in enumerate(l): self.tree.move(k, '', i)
        self.tree.heading(c, command=lambda: self.sort_tree(c, not r))
    def destroy(self):
        if self.observer: self.observer.stop(); self.observer.join()
        super().destroy()

# --- Main App ---
class WorkDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Professional Work Dashboard")
        self.state('zoomed')
        self.after(100, lambda: self.state('zoomed'))
        
        self.config_data = ConfigManager.load_config()
        self.num_panels = self.config_data.get("num_panels", 6)
        self.current_theme = self.config_data.get("theme_name", "Light")
        self.layout_mode = self.config_data.get("layout_mode", "G")
        self.base_font_size = self.config_data.get("font_size", 16)
        
        self.focused_panel_id = None 
        
        self.apply_theme(self.current_theme)
        
        # Main Grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # --- Top Toolbar ---
        tb_color = THEMES[self.current_theme]["bg"]
        self.toolbar = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color=tb_color)
        self.toolbar.grid(row=0, column=0, sticky="ew")
        
        self.logo_label = ctk.CTkLabel(self.toolbar, text="DashBoard Pro", font=("Segoe UI", 26, "bold"), text_color=THEMES[self.current_theme]["text"])
        self.logo_label.pack(side="left", padx=25, pady=15)
        
        # Global Search
        self.global_search_var = ctk.StringVar()
        self.global_search_var.trace_add("write", self.on_global_search)
        self.global_search_entry = ctk.CTkEntry(self.toolbar, textvariable=self.global_search_var,
                                                width=250, height=36, placeholder_text="🔎 Global Search...",
                                                font=("Segoe UI", 14))
        self.global_search_entry.pack(side="left", padx=20)

        # Controls
        self.theme_var = ctk.StringVar(value=self.current_theme)
        self.theme_combo = ctk.CTkOptionMenu(self.toolbar, variable=self.theme_var, values=["Light", "Dark"], 
                                             command=self.change_theme, width=120, height=36, font=("Segoe UI", 14))
        self.theme_combo.pack(side="right", padx=20)
        
        self.btn_f_inc = ctk.CTkButton(self.toolbar, text="A+", command=self.inc_font, width=50, height=36, font=("Segoe UI", 14, "bold"))
        self.btn_f_inc.pack(side="right", padx=3)
        self.btn_f_dec = ctk.CTkButton(self.toolbar, text="A-", command=self.dec_font, width=50, height=36, font=("Segoe UI", 14, "bold"))
        self.btn_f_dec.pack(side="right", padx=3)
        
        self.btn_ws = ctk.CTkButton(self.toolbar, text="Workspaces", command=self.open_workspace_menu, width=120, height=36, font=("Segoe UI", 14))
        self.btn_ws.pack(side="right", padx=15)

        self.btn_layout = ctk.CTkButton(self.toolbar, text="Layout", command=self.change_layout, width=100, height=36, font=("Segoe UI", 14))
        self.btn_layout.pack(side="right", padx=3)

        self.btn_refresh = ctk.CTkButton(self.toolbar, text="Refresh", command=self.refresh_all, width=100, height=36, font=("Segoe UI", 14))
        self.btn_refresh.pack(side="right", padx=3)

        # Main Container (ZERO PADDING)
        self.main_container = ctk.CTkFrame(self, fg_color=THEMES[self.current_theme]["bg"])
        self.main_container.grid(row=1, column=0, sticky="nsew")
        
        self.panels = []
        self.update_global_styles()
        self.setup_layout(self.num_panels, self.layout_mode)

    def on_global_search(self, *args):
        term = self.global_search_var.get()
        for panel in self.panels:
            panel.search_var.set(term)
            # refresh_files is triggered automatically by the trace on panel.search_var

    def apply_theme(self, t_name):
        t = THEMES[t_name]
        ctk.set_appearance_mode(t["mode"])
        ctk.set_default_color_theme("blue")

    def change_theme(self, new_t):
        self.current_theme = new_t
        self.config_data["theme_name"] = new_t
        self.save_config()
        messagebox.showinfo("Restart", "Restart app to apply.")

    def inc_font(self):
        if self.base_font_size < 28:
            self.base_font_size += 2; self.update_global_styles(); self.save_font()
    def dec_font(self):
        if self.base_font_size > 10:
            self.base_font_size -= 2; self.update_global_styles(); self.save_font()
    def save_font(self):
        self.config_data["font_size"] = self.base_font_size; self.save_config()

    def update_global_styles(self):
        style = ttk.Style(); style.theme_use("clam")
        row_height = int(self.base_font_size * 2.5)
        font_spec = ("Segoe UI", self.base_font_size)
        head_font = ("Segoe UI", self.base_font_size + 1, "bold")
        t = THEMES[self.current_theme]
        bg = t["card"]; fg = t["text"]
        style.configure("Treeview", background=bg, foreground=fg, fieldbackground=bg, bordercolor=t["bg"], font=font_spec, rowheight=row_height)
        style.map('Treeview', background=[('selected', '#0078D4')], foreground=[('selected', 'white')])
        style.configure("Treeview.Heading", background=t["bg"], foreground=fg, relief="flat", font=head_font, padding=(10, 12))
        for p in self.panels: p.update_font_size(self.base_font_size)

    # --- WORKSPACES ---
    def open_workspace_menu(self):
        ws_window = ctk.CTkToplevel(self)
        ws_window.title("Workspaces")
        ws_window.geometry("400x400")
        ws_window.attributes('-topmost', True)
        ctk.CTkLabel(ws_window, text="Workspaces", font=("Segoe UI", 18, "bold")).pack(pady=15)
        ctk.CTkButton(ws_window, text="Save Current", command=lambda: self.save_workspace(ws_window)).pack(pady=10)
        scroll = ctk.CTkScrollableFrame(ws_window)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        workspaces = self.config_data.get("workspaces", {})
        for name in workspaces:
            f = ctk.CTkFrame(scroll)
            f.pack(fill="x", pady=2)
            ctk.CTkLabel(f, text=name).pack(side="left", padx=10)
            ctk.CTkButton(f, text="X", width=30, fg_color="red", command=lambda n=name: self.delete_workspace(n, ws_window)).pack(side="right", padx=2)
            ctk.CTkButton(f, text="Load", width=60, command=lambda n=name: self.load_workspace(n, ws_window)).pack(side="right", padx=2)

    def save_workspace(self, w):
        name = ctk.CTkInputDialog(text="Name:", title="Save").get_input()
        if name:
            ws_data = {"num_panels": self.num_panels, "layout_mode": self.layout_mode, "paths": {str(i+1): self.config_data.get(str(i+1), "") for i in range(self.num_panels)}}
            if "workspaces" not in self.config_data: self.config_data["workspaces"] = {}
            self.config_data["workspaces"][name] = ws_data
            self.save_config()
            w.destroy()

    def load_workspace(self, name, w):
        ws = self.config_data["workspaces"][name]
        self.num_panels = ws["num_panels"]
        self.layout_mode = ws["layout_mode"]
        for k, v in ws["paths"].items(): self.config_data[k] = v
        self.save_config()
        self.setup_layout(self.num_panels, self.layout_mode)
        w.destroy()

    def delete_workspace(self, name, w):
        del self.config_data["workspaces"][name]
        self.save_config()
        w.destroy()
        self.open_workspace_menu()

    # --- FOCUS MODE FIX ---
    def toggle_focus_mode(self, panel_id):
        if self.focused_panel_id:
            # Exiting Focus Mode
            self.focused_panel_id = None
            self.setup_layout(self.num_panels, self.layout_mode)
        else:
            # Entering Focus Mode
            self.focused_panel_id = panel_id
            
            # 1. DESTROY the old container completely to wipe grid weights
            if self.main_container:
                self.main_container.destroy()
            
            # 2. Recreate the container
            self.main_container = ctk.CTkFrame(self, fg_color=THEMES[self.current_theme]["bg"])
            self.main_container.grid(row=1, column=0, sticky="nsew")
            
            self.panels.clear()

            # 3. Setup a clean 1x1 Grid
            self.main_container.grid_rowconfigure(0, weight=1)
            self.main_container.grid_columnconfigure(0, weight=1)
            
            # 4. Create the single focused panel
            idx = int(panel_id) - 1
            accent = ACCENT_COLORS[idx % len(ACCENT_COLORS)]
            
            p = FolderCard(self.main_container, panel_id, accent, self.config_data, self.save_config, self.get_panels, 
                           THEMES[self.current_theme], self.base_font_size, self.toggle_focus_mode, is_focused=True)
            p.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
            self.panels.append(p)

    def _create_panel(self, idx, r, c, padx=2, pady=2):
        accent = ACCENT_COLORS[idx % len(ACCENT_COLORS)]
        p = FolderCard(self.main_container, idx+1, accent, self.config_data, self.save_config, self.get_panels, 
                       THEMES[self.current_theme], self.base_font_size, self.toggle_focus_mode)
        p.grid(row=r, column=c, sticky="nsew", padx=padx, pady=pady)
        self.panels.append(p)

    def setup_layout(self, num, mode):
        if self.main_container: self.main_container.destroy()
        self.main_container = ctk.CTkFrame(self, fg_color=THEMES[self.current_theme]["bg"])
        self.main_container.grid(row=1, column=0, sticky="nsew")
        for p in self.panels: p.destroy()
        self.panels.clear()

        # --- UNIFIED SMART GRID ---
        # For standard numbers, use simple single-parent grid (Robust)
        if mode == "G" and num in [4, 6, 8, 9]:
            cols = 2 if num == 4 else 3 if num in [6, 9] else 4 if num == 8 else 3
            rows = math.ceil(num / cols)
            
            for r in range(rows): self.main_container.grid_rowconfigure(r, weight=1)
            for c in range(cols): self.main_container.grid_columnconfigure(c, weight=1)
            
            for i in range(num):
                r = i // cols; c = i % cols
                self._create_panel(i, r, c, padx=2, pady=2)
                
        # Vertical / Horizontal Modes
        elif mode == "V" and 2 <= num <= 4:
            self.main_container.grid_rowconfigure(0, weight=1)
            for i in range(num): self.main_container.grid_columnconfigure(i, weight=1)
            for i in range(num): self._create_panel(i, 0, i, padx=2, pady=2)
        elif mode == "H" and 2 <= num <= 4:
            self.main_container.grid_columnconfigure(0, weight=1)
            for i in range(num): self.main_container.grid_rowconfigure(i, weight=1)
            for i in range(num): self._create_panel(i, i, 0, padx=2, pady=2)
            
        # Odd numbers (5, 7) use Flex Rows
        else:
            if num <= 3: rows = 1
            elif num <= 8: rows = 2
            else: rows = 3
            
            base = num // rows
            extra = num % rows
            counts = [base + (1 if i < extra else 0) for i in range(rows)]

            for r in range(rows): self.main_container.grid_rowconfigure(r, weight=1)
            self.main_container.grid_columnconfigure(0, weight=1)

            p_idx = 0
            for r, count in enumerate(counts):
                row_f = ctk.CTkFrame(self.main_container, fg_color="transparent")
                row_f.grid(row=r, column=0, sticky="nsew", padx=2, pady=2)
                for c in range(count): row_f.grid_columnconfigure(c, weight=1)
                row_f.grid_rowconfigure(0, weight=1)
                for c in range(count):
                    if p_idx >= num: break
                    accent = ACCENT_COLORS[p_idx % len(ACCENT_COLORS)]
                    p = FolderCard(row_f, p_idx+1, accent, self.config_data, self.save_config, self.get_panels, 
                                   THEMES[self.current_theme], self.base_font_size, self.toggle_focus_mode)
                    p.grid(row=0, column=c, sticky="nsew", padx=2, pady=0)
                    self.panels.append(p)
                    p_idx += 1

    def change_layout(self):
        dialog = ctk.CTkInputDialog(text="Panels (2-9):", title="Layout")
        res = dialog.get_input()
        if res:
            try:
                n = int(res)
                if 2 <= n <= 9:
                    if 2 <= n <= 4:
                        mode_d = ctk.CTkInputDialog(text="Mode:\nV=Vertical, H=Horizontal, G=Grid\nEnter V, H, or G:", title="Layout Mode")
                        m = mode_d.get_input()
                        if m and m.upper() in ['V', 'H', 'G']: self.layout_mode = m.upper()
                        else: self.layout_mode = 'G'
                    else: self.layout_mode = 'G'
                    self.num_panels = n
                    self.config_data["num_panels"] = n
                    self.config_data["layout_mode"] = self.layout_mode
                    self.save_config()
                    self.setup_layout(n, self.layout_mode)
            except: pass

    def get_panels(self): return self.panels
    def refresh_all(self): 
        for p in self.panels: p.refresh_files()
    def save_config(self): ConfigManager.save_config(self.config_data)
    def on_closing(self):
        for p in self.panels: 
            if p.observer: p.observer.stop()
        self.destroy()

if __name__ == "__main__":
    app = WorkDashboard()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()