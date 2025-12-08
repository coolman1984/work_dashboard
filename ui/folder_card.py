import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from watchdog.observers import Observer

from ui.styles import TYPE_COLORS, DEFAULT_TYPE_COLOR, TAG_COLORS
from ui.quick_look import QuickLookWindow
from services.clipboard import InternalClipboard
from services.watchdog_service import FolderChangeHandler
from services.metadata_service import MetadataService
from utils.files import open_path, get_file_info
from utils.debounce import Debouncer

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

        # Load icon images
        self.icon_images = {}
        icon_paths = {
            'folder': 'icons/folder.png',
            'document': 'icons/document.png',
            'spreadsheet': 'icons/spreadsheet.png',
            'image': 'icons/image.png',
            'code': 'icons/code.png',
            'archive': 'icons/archive.png',
            'executable': 'icons/executable.png',
            'audio': 'icons/audio.png',
            'video': 'icons/video.png',
            'default': 'icons/file.png'
        }
        for name, path in icon_paths.items():
            try:
                self.icon_images[name] = tk.PhotoImage(file=path)
            except:
                self.icon_images[name] = None
        
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
        
        # Up Button
        self.btn_up = ctk.CTkButton(self.controls_frame, text="⬆", 
                                    command=self.go_up, 
                                    font=("Segoe UI", self.base_font_size, "bold"), 
                                    width=30, height=30, corner_radius=6,
                                    fg_color=self.theme_data["bg"], text_color=self.theme_data["text"],
                                    hover_color=self.theme_data["hover"])
        self.btn_up.pack(side="left", padx=2)

        self.btn_open_folder = ctk.CTkButton(self.controls_frame, text="↗ Open", 
                                             command=self.open_current_folder, 
                                             font=("Segoe UI", self.base_font_size), 
                                             height=30, corner_radius=6,
                                             fg_color=self.theme_data["bg"], text_color=self.theme_data["text"],
                                             hover_color=self.theme_data["hover"])
        self.btn_open_folder.pack(side="left")

        # Search with debouncing
        self.search_var = ctk.StringVar()
        self.search_debouncer = Debouncer(self, self.refresh_files, 300)
        self.search_var.trace_add("write", lambda *args: self.search_debouncer.trigger())
        
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

        # Content search toggle
        self.content_search_var = ctk.BooleanVar()
        self.content_search_cb = ctk.CTkCheckBox(self.controls_frame, text="Content",
                                                variable=self.content_search_var,
                                                command=self.refresh_files,
                                                font=("Segoe UI", self.base_font_size))
        self.content_search_cb.pack(side="right", padx=5)

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
            MetadataService.load_tags()
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
        self.tree.bind("<BackSpace>", lambda e: self.go_up())

    def update_font_size(self, new_size):
        self.base_font_size = new_size
        self.title_label.configure(font=("Segoe UI", new_size + 6, "bold"))
        self.path_label.configure(font=("Segoe UI", new_size - 2))
        self.btn_browse.configure(font=("Segoe UI", new_size, "bold"), height=int(new_size*2.0))
        self.btn_up.configure(font=("Segoe UI", new_size, "bold"), height=int(new_size*2.0))
        self.btn_open_folder.configure(font=("Segoe UI", new_size), height=int(new_size*2.0))
        self.search_entry.configure(font=("Segoe UI", new_size), height=int(new_size*2.0))
        self.filter_combo.configure(font=("Segoe UI", new_size), dropdown_font=("Segoe UI", new_size), height=int(new_size*2.0))
        self.btn_focus.configure(font=("Segoe UI", new_size, "bold"))
        self.stats_label.configure(font=("Segoe UI", new_size - 2, "bold"))

    def create_treeview_widget(self):
        # Use #0 for Name (tree column) to support icons
        columns = ("size", "date")
        self.tree = ttk.Treeview(self.tree_container, columns=columns, show="tree headings", selectmode="extended")
        
        # Configure #0 (Name)
        self.tree.heading("#0", text="Name", command=lambda: self.sort_tree("#0", False))
        self.tree.column("#0", width=300, stretch=True)
        
        self.tree.heading("size", text="Size", command=lambda: self.sort_tree("size", False))
        self.tree.heading("date", text="Date", command=lambda: self.sort_tree("date", False))

        self.tree.column("size", width=100, anchor="e", stretch=False)
        self.tree.column("date", width=160, anchor="center", stretch=False)

        vsb = ttk.Scrollbar(self.tree_container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        # Style the headings to match theme and fix hover issue
        style = ttk.Style()
        style.configure("Treeview.Heading", background=self.theme_data["bg"], foreground=self.theme_data["text"], relief="flat")
        style.map("Treeview.Heading", background=[("active", self.theme_data["hover"])], foreground=[("active", self.theme_data["text"])])

        # Configure Tag Colors
        normal_font = ("Segoe UI", self.base_font_size)
        for name, color in TAG_COLORS.items():
            # Apply both foreground and background so the entire row is highlighted
            # Use black text for better visibility
            self.tree.tag_configure(name, foreground="#000000", background=color, font=normal_font)

        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-3>", self.on_right_click)

    def quick_look(self):
        item = self.tree.selection()
        if item:
            fpath = self.tree.item(item, "tags")[0]
            if os.path.exists(fpath) and os.path.isfile(fpath): QuickLookWindow(self, fpath)

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
            self.set_path(folder)

    def go_up(self):
        if self.current_path and os.path.exists(self.current_path):
            parent = os.path.dirname(self.current_path)
            if parent and os.path.exists(parent):
                self.set_path(parent)

    def set_path(self, path):
        self.current_path = path
        self.config_data[self.panel_id] = path
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

    def get_file_icon(self, filename, is_folder=False):
        """Return appropriate icon image for file type"""
        if is_folder:
            return self.icon_images.get('folder')

        ext = os.path.splitext(filename)[1].lower()
        icon_map = {
            # Documents
            '.pdf': 'document', '.docx': 'document', '.doc': 'document', '.txt': 'document', '.md': 'document',
            # Spreadsheets
            '.xlsx': 'spreadsheet', '.xls': 'spreadsheet', '.csv': 'spreadsheet',
            # Images
            '.jpg': 'image', '.jpeg': 'image', '.png': 'image', '.gif': 'image', '.bmp': 'image',
            # Code
            '.py': 'code', '.js': 'code', '.html': 'code', '.css': 'code', '.json': 'code',
            # Archives
            '.zip': 'archive', '.rar': 'archive', '.7z': 'archive',
            # Executables
            '.exe': 'executable', '.msi': 'executable',
            # Audio/Video
            '.mp3': 'audio', '.wav': 'audio', '.mp4': 'video', '.avi': 'video',
        }
        icon_name = icon_map.get(ext, 'default')
        return self.icon_images.get(icon_name)

    def refresh_files(self, _=None):
        for item in self.tree.get_children(): self.tree.delete(item)
        if not self.current_path or not os.path.exists(self.current_path):
            self.update_header()
            self.update_analytics([])
            return
        self.update_header()
        valid_exts = self.get_extensions()
        search_term = self.search_var.get().lower()
        content_search = self.content_search_var.get()
        text_exts = ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.log', '.xml', '.ini', '.cfg']

        files_data = [] # Store for analytics: (name, size_str, date, size_bytes)

        try:
            # 1. Get all items
            all_items = os.listdir(self.current_path)
            all_items.sort(key=str.lower)

            # 2. Separate folders and files
            folders = []
            files = []

            for item in all_items:
                full_path = os.path.join(self.current_path, item)
                if os.path.isdir(full_path):
                    if not item.startswith('.'): # Skip hidden folders
                        folders.append(item)
                elif os.path.isfile(full_path):
                    files.append(item)

            # 3. Insert Folders
            for d in folders:
                if search_term and search_term not in d.lower(): continue
                full_path = os.path.join(self.current_path, d)
                icon = self.get_file_icon(d, is_folder=True)
                item_kwargs = {"text": d, "values": ["", ""], "tags": (full_path, "folder")}
                if icon: item_kwargs["image"] = icon
                self.tree.insert("", "end", **item_kwargs)

            # 4. Insert Files
            for f in files:
                full_path = os.path.join(self.current_path, f)
                ext = os.path.splitext(f)[1].lower()

                if valid_exts and ext not in valid_exts: continue

                # Search logic
                matches = True
                if search_term:
                    name_match = search_term in f.lower()
                    content_match = False
                    if content_search and ext in text_exts:
                        try:
                            with open(full_path, 'r', encoding='utf-8', errors='ignore') as file:
                                content = file.read(10000).lower()  # Read first 10KB
                                content_match = search_term in content
                        except:
                            content_match = False
                    matches = name_match or content_match

                if not matches: continue

                raw_size, size_mb, mod = get_file_info(full_path)
                size_str = f"{size_mb:.2f} MB"

                # Check for tags & notes
                tags = [full_path]
                meta = MetadataService.get_tag(full_path)

                icon = self.get_file_icon(f)
                display_name = f
                if "note" in meta and meta["note"]:
                    display_name += " 📝"

                if "color" in meta:
                    tags.append(meta["color"])

                files_data.append((f, size_str, mod, raw_size))
                
                item_kwargs = {"text": display_name, "values": [size_str, mod], "tags": tuple(tags)}
                if icon: item_kwargs["image"] = icon
                self.tree.insert("", "end", **item_kwargs)

        except OSError as e:
            print(f"Error reading directory {self.current_path}: {e}")

        self.update_analytics(files_data)

    def on_double_click(self, event):
        item = self.tree.selection()
        if item:
            fpath = self.tree.item(item, "tags")[0]
            if os.path.isdir(fpath):
                self.set_path(fpath)
            else:
                open_path(fpath)

    def on_right_click(self, event):
        item = self.tree.identify_row(event.y)
        selected_items = self.tree.selection()
        menu = tk.Menu(self, tearoff=0, font=("Segoe UI", 12))

        # Handle single item or multiple items
        if len(selected_items) > 1:
            # Bulk operations for multiple files
            file_paths = []
            for sel_item in selected_items:
                fpath = self.tree.item(sel_item, "tags")[0]
                if os.path.isfile(fpath):
                    file_paths.append(fpath)

            if file_paths:
                menu.add_command(label=f"Bulk Operations ({len(file_paths)} files)", state="disabled")
                menu.add_separator()
                menu.add_command(label="Copy All", command=lambda: self.bulk_copy(file_paths))
                menu.add_command(label="Delete All", command=lambda: self.bulk_delete(file_paths))

                # Bulk move menu
                move_menu = tk.Menu(menu, tearoff=0, font=("Segoe UI", 12))
                panels = self.get_panels_callback()
                added = False
                for p in panels:
                    if p != self and p.current_path:
                        move_menu.add_command(label=p.title_label.cget("text"), command=lambda t=p: self.bulk_move(file_paths, t))
                        added = True

                if added:
                    menu.add_separator()
                    menu.add_cascade(label="Move All To...", menu=move_menu)

        elif item:
            # Single item operations
            self.tree.selection_set(item)
            fpath = self.tree.item(item, "tags")[0]
            file_name = os.path.basename(fpath)

            menu.add_command(label="Open", command=lambda: open_path(fpath))

            if os.path.isfile(fpath):
                menu.add_separator()
                menu.add_command(label="Copy", command=lambda: self.copy_file(fpath))
                menu.add_command(label="Cut", command=lambda: self.cut_file(fpath))
                menu.add_separator()
                menu.add_command(label="Rename", command=lambda: self.rename_file(fpath))
                menu.add_command(label="Delete", command=lambda: self.delete_file(fpath))

                move_menu = tk.Menu(menu, tearoff=0, font=("Segoe UI", 12))
                panels = self.get_panels_callback()
                added = False
                for p in panels:
                    if p != self and p.current_path:
                        move_menu.add_command(label=p.title_label.cget("text"), command=lambda t=p: self.move_file(fpath, t))
                        added = True

                if not added:
                    move_menu.add_command(label="(No other folders open)", state="disabled")

                menu.add_separator()
                menu.add_cascade(label="Move To...", menu=move_menu)

                # Tagging Menu
                menu.add_separator()
                tag_menu = tk.Menu(menu, tearoff=0, font=("Segoe UI", 12))
                tag_menu.add_command(label="🔴 Very Important", command=lambda: self.set_file_tag(fpath, "red"))
                tag_menu.add_command(label="🟢 Important", command=lambda: self.set_file_tag(fpath, "green"))
                tag_menu.add_command(label="🟡 Review", command=lambda: self.set_file_tag(fpath, "yellow"))
                tag_menu.add_separator()
                tag_menu.add_command(label="📝 Add Note", command=lambda: self.add_file_note(fpath))
                tag_menu.add_command(label="❌ Clear Tags", command=lambda: self.clear_file_tags(fpath))
                menu.add_cascade(label="Tags & Notes", menu=tag_menu)

                # View Note if exists
                meta = MetadataService.get_tag(fpath)
                if "note" in meta and meta["note"]:
                    menu.add_command(label="📄 View Note", command=lambda: self.view_file_note(fpath))

        if InternalClipboard.has_data():
            if item or selected_items: menu.add_separator()
            path, op = InternalClipboard.get()
            fname = os.path.basename(path)
            menu.add_command(label=f"Paste '{fname}'", command=self.paste_file)
        menu.tk_popup(event.x_root, event.y_root)

    # Operations
    def copy_selected(self): 
        item = self.tree.selection()
        if item: self.copy_file(self.tree.item(item, "tags")[0])
    def cut_selected(self): 
        item = self.tree.selection()
        if item: self.cut_file(self.tree.item(item, "tags")[0])
    def delete_selected(self): 
        item = self.tree.selection()
        if item: self.delete_file(self.tree.item(item, "tags")[0])
        
    def copy_file(self, fpath): InternalClipboard.set(fpath, 'copy', self); self.show_indicator("Copied")
    def cut_file(self, fpath): InternalClipboard.set(fpath, 'cut', self); self.show_indicator("Cut")
    
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
            if op == 'copy':
                shutil.copy2(src, dest)
            elif op == 'cut':
                shutil.move(src, dest)
                InternalClipboard.clear()
        except (OSError, shutil.Error) as e:
            messagebox.showerror("Error", f"Cannot paste file: {e}")
            
    def rename_file(self, fpath):
        f = os.path.basename(fpath)
        dialog = ctk.CTkInputDialog(text="New name:", title="Rename")
        n = dialog.get_input()
        if n:
            try:
                os.rename(fpath, os.path.join(self.current_path, n))
                self.refresh_files()
            except OSError as e:
                messagebox.showerror("Error", f"Cannot rename file: {e}")
                
    def delete_file(self, fpath):
        f = os.path.basename(fpath)
        if messagebox.askyesno("Delete", f"Delete {f}?"):
            try:
                os.remove(fpath)
            except OSError as e:
                messagebox.showerror("Error", f"Cannot delete file: {e}")
                
    def move_file(self, fpath, t):
        try:
            shutil.move(fpath, os.path.join(t.current_path, os.path.basename(fpath)))
        except (OSError, shutil.Error) as e:
            messagebox.showerror("Error", f"Cannot move file: {e}")
            
    def sort_tree(self, c, r):
        l = [(self.tree.set(k, c), k) if c != "#0" else (self.tree.item(k, "text"), k) for k in self.tree.get_children('')]
        if c == "size": l.sort(key=lambda x: float(x[0].split()[0]) if x[0] else 0, reverse=r)
        else: l.sort(key=lambda x: x[0].lower(), reverse=r)
        for i, (v, k) in enumerate(l): self.tree.move(k, '', i)
        self.tree.heading(c, command=lambda: self.sort_tree(c, not r))
    def destroy(self):
        if self.observer: self.observer.stop(); self.observer.join()
        super().destroy()

    # Tagging Operations
    def set_file_tag(self, fpath, color):
        MetadataService.set_tag(fpath, color=color)
        self.refresh_files()

    def add_file_note(self, fpath):
        current_note = MetadataService.get_tag(fpath).get("note", "")
        dialog = ctk.CTkInputDialog(text="Enter note:", title="Add Note")
        note = dialog.get_input()
        if note is not None:
            MetadataService.set_tag(fpath, note=note)
            self.refresh_files()

    def clear_file_tags(self, fpath):
        MetadataService.remove_tag(fpath)
        self.refresh_files()

    def view_file_note(self, fpath):
        note = MetadataService.get_tag(fpath).get("note", "")
        messagebox.showinfo(f"Note for {os.path.basename(fpath)}", note)

    # Bulk Operations
    def bulk_copy(self, file_paths):
        for fpath in file_paths:
            self.copy_file(fpath)
        self.show_indicator("Bulk Copied")

    def bulk_delete(self, file_paths):
        count = len(file_paths)
        if messagebox.askyesno("Bulk Delete", f"Delete {count} selected files?"):
            for fpath in file_paths:
                try:
                    os.remove(fpath)
                except OSError as e:
                    messagebox.showerror("Error", f"Cannot delete {os.path.basename(fpath)}: {e}")
            self.refresh_files()
            self.show_indicator(f"Deleted {count} files")

    def bulk_move(self, file_paths, target_panel):
        for fpath in file_paths:
            self.move_file(fpath, target_panel)
        self.show_indicator("Bulk Moved")
