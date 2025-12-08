import math
import os
import customtkinter as ctk
from tkinter import ttk, messagebox

from config.manager import ConfigManager
from ui.styles import THEMES, ACCENT_COLORS, TAG_COLORS
from ui.folder_card import FolderCard
import json
from utils.files import open_path

class WorkDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Professional Work Dashboard")
        self.state('zoomed')
        self.after(100, lambda: self.state('zoomed'))

        # Set application icon
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icon.png")
            if os.path.exists(icon_path):
                self.iconphoto(False, tk.PhotoImage(file=icon_path))
        except Exception as e:
            print(f"Could not load icon: {e}")
        
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
        
        # Global Search with debouncing
        self.global_search_var = ctk.StringVar()
        self.global_search_after_id = None
        self.global_search_var.trace_add("write", self._on_global_search_change)
        
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

        self.btn_tagged = ctk.CTkButton(self.toolbar, text="Tagged Files", command=self.show_tagged_files, width=140, height=36, font=("Segoe UI", 14))
        self.btn_tagged.pack(side="right", padx=3)

        # Main Container (ZERO PADDING)
        self.main_container = ctk.CTkFrame(self, fg_color=THEMES[self.current_theme]["bg"])
        self.main_container.grid(row=1, column=0, sticky="nsew")
        
        self.panels = []
        self.update_global_styles()
        self.setup_layout(self.num_panels, self.layout_mode)

    def _on_global_search_change(self, *args):
        """Debounced global search handler - waits 300ms after user stops typing"""
        if self.global_search_after_id:
            self.after_cancel(self.global_search_after_id)
        self.global_search_after_id = self.after(300, self.on_global_search)

    def on_global_search(self):
        """Apply global search term to all panels"""
        term = self.global_search_var.get()
        for panel in self.panels:
            panel.search_var.set(term)
            # refresh_files is triggered automatically by the trace on panel.search_var

    def apply_theme(self, t_name):
        t = THEMES[t_name]
        ctk.set_appearance_mode(t["mode"])
        ctk.set_default_color_theme("blue")

    def change_theme(self, new_t):
        """Change theme dynamically without restart"""
        self.current_theme = new_t
        self.config_data["theme_name"] = new_t
        self.save_config()
        
        # Apply theme immediately
        self.apply_theme(new_t)
        self.reload_theme_for_all_widgets()

    def reload_theme_for_all_widgets(self):
        """Update all existing widgets with new theme colors"""
        t = THEMES[self.current_theme]
        
        # Update toolbar
        self.toolbar.configure(fg_color=t["bg"])
        self.logo_label.configure(text_color=t["text"])
        
        # Update main container
        self.main_container.configure(fg_color=t["bg"])
        
        # Update all panels
        for panel in self.panels:
            panel.configure(fg_color=t["card"])
            panel.path_label.configure(text_color=t["subtext"])
            panel.btn_open_folder.configure(fg_color=t["bg"], text_color=t["text"], hover_color=t["hover"])
            panel.btn_focus.configure(border_color=t["subtext"], text_color=t["text"])
            # Update analytics bar theme
            if hasattr(panel, 'analytics_bar') and panel.analytics_bar:
                panel.analytics_bar.stats_label.configure(text_color=t["subtext"])
                panel.analytics_bar.stats_canvas.configure(bg=t["bg"])
        
        # Update treeview styles
        self.update_global_styles()

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
            
            # 1. Properly cleanup observers before destroying panels
            for p in self.panels:
                p.destroy()  # Ensures observers are stopped
            
            # 2. DESTROY the old container completely to wipe grid weights
            if self.main_container:
                self.main_container.destroy()
            
            # 3. Recreate the container
            self.main_container = ctk.CTkFrame(self, fg_color=THEMES[self.current_theme]["bg"])
            self.main_container.grid(row=1, column=0, sticky="nsew")
            
            self.panels.clear()

            # 4. Setup a clean 1x1 Grid
            self.main_container.grid_rowconfigure(0, weight=1)
            self.main_container.grid_columnconfigure(0, weight=1)
            
            # 5. Create the single focused panel
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
            except ValueError:
                messagebox.showerror("Error", "Please enter a number between 2 and 9")

    def get_panels(self): return self.panels
    def refresh_all(self): 
        for p in self.panels: p.refresh_files()

    def load_tagged_files(self):
        """
        Load tagged file data from file_tags.json.
        Returns a dict mapping file paths to metadata dicts.
        """
        tags_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "file_tags.json")
        try:
            with open(tags_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError("file_tags.json must contain a JSON object")
                return data
        except FileNotFoundError:
            messagebox.showerror("Error", f"Tag file not found: {tags_path}")
            return {}
        except (json.JSONDecodeError, ValueError) as e:
            messagebox.showerror("Error", f"Failed to parse tag file: {e}")
            return {}
    
    def open_tagged_file(self, path: str):
        """
        Open a tagged file. Uses os.startfile on Windows,
        falling back to utils.files.open_path if needed.
        """
        try:
            if os.name == "nt":
                os.startfile(path)
            else:
                open_path(path)
        except Exception as e:
            messagebox.showerror("Error", f"Unable to open file: {e}")
    
    def show_tagged_files(self):
        tags = self.load_tagged_files()
        if not tags:
            messagebox.showinfo("Tagged Files", "No tagged files available.")
            return
    
        # Group by color
        grouped = {"red": [], "green": [], "yellow": []}
        for path, meta in tags.items():
            color = meta.get("color")
            if color in grouped:
                grouped[color].append((path, meta.get("note", "")))
    
        if not any(grouped.values()):
            messagebox.showinfo("Tagged Files", "No red/green/yellow tags available yet.")
            return
    
        modal = ctk.CTkToplevel(self)
        modal.title("Tagged Files")
        modal.geometry("520x520")
        modal.transient(self)
        modal.attributes('-topmost', True)
    
        scroll = ctk.CTkScrollableFrame(modal)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
    
        color_info = [("red", "Red · Very Important"), ("green", "Green · Important"), ("yellow", "Yellow · Review")]
        for color, label_text in color_info:
            entries = grouped[color]
            if not entries:
                continue
            section = ctk.CTkFrame(scroll, fg_color="transparent")
            section.pack(fill="x", pady=(0, 8))
            ctk.CTkLabel(section, text=label_text, text_color=TAG_COLORS.get(color, "#ffffff"),
                          font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=2)
            for path, note in entries:
                row = ctk.CTkFrame(section, fg_color="transparent")
                row.pack(fill="x", pady=1)
                btn = ctk.CTkButton(row, text=os.path.basename(path) or path, anchor="w",
                                    command=lambda p=path: self.open_tagged_file(p),
                                    fg_color=THEMES[self.current_theme]["card"],
                                    hover_color=THEMES[self.current_theme]["hover"],
                                    text_color=THEMES[self.current_theme]["text"],
                                    corner_radius=6)
                btn.pack(side="left", fill="x", expand=True)
                if note:
                    ctk.CTkLabel(row, text=f"({note})", text_color=THEMES[self.current_theme]["subtext"],
                                  font=("Segoe UI", 10)).pack(side="right", padx=(8, 0))
    
        ctk.CTkButton(modal, text="Close", command=modal.destroy).pack(pady=(8, 10))

    def save_config(self): ConfigManager.save_config(self.config_data)
    def on_closing(self):
        for p in self.panels: 
            if p.observer: p.observer.stop()
        self.destroy()
