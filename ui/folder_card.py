"""
FolderCard - File browser panel component.

This is the main panel component that coordinates file browsing, display,
and operations. It delegates to specialized modules for:
- File operations: services/file_operations.py
- Context menus: ui/context_menu.py
- Analytics display: ui/analytics_bar.py
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from watchdog.observers import Observer

from ui.styles import TAG_COLORS
from ui.quick_look import QuickLookWindow
from ui.context_menu import ContextMenuBuilder
from ui.analytics_bar import AnalyticsBar
from services.clipboard import InternalClipboard
from services.watchdog_service import FolderChangeHandler
from services.metadata_service import MetadataService
from services.file_operations import FileOperations
from utils.files import open_path, get_file_info
from utils.debounce import Debouncer


class FolderCard(ctk.CTkFrame):
    """A file browser panel with search, filtering, and file operations."""

    def __init__(self, parent, panel_id, accent_color, config_data, save_callback,
                 get_panels_callback, app_theme_data, base_font_size,
                 toggle_focus_callback, is_focused=False):
        super().__init__(parent, corner_radius=10, border_width=0, fg_color=app_theme_data["card"])

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

        # Initialize helpers
        self.menu_builder = ContextMenuBuilder(self, "Segoe UI", self.base_font_size)

        # Load icons
        self.icon_images = {}
        self._load_icons()

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Build UI
        self._create_accent_strip()
        self._create_header()
        self._create_controls()
        self._create_treeview()
        self._create_analytics_bar()

        # Initialize if path exists
        if self.current_path:
            MetadataService.load_tags()
            self.update_header()
            self.refresh_files()
            self.start_watchdog()

        # Keyboard bindings
        self.tree.bind("<Control-c>", lambda e: self._copy_selected())
        self.tree.bind("<Control-x>", lambda e: self._cut_selected())
        self.tree.bind("<Control-v>", lambda e: self._paste_file())
        self.tree.bind("<Delete>", lambda e: self._delete_selected())
        self.tree.bind("<F5>", lambda e: self.refresh_files())
        self.tree.bind("<space>", lambda e: self._quick_look())
        self.tree.bind("<BackSpace>", lambda e: self.go_up())

    # ========== Icon Loading ==========

    def _load_icons(self):
        """Load file type icons."""
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
            except Exception:
                self.icon_images[name] = None

    def _get_file_icon(self, filename, is_folder=False):
        """Get appropriate icon for file type."""
        if is_folder:
            return self.icon_images.get('folder')

        ext = os.path.splitext(filename)[1].lower()
        icon_map = {
            '.pdf': 'document', '.docx': 'document', '.doc': 'document',
            '.txt': 'document', '.md': 'document',
            '.xlsx': 'spreadsheet', '.xls': 'spreadsheet', '.csv': 'spreadsheet',
            '.jpg': 'image', '.jpeg': 'image', '.png': 'image',
            '.gif': 'image', '.bmp': 'image',
            '.py': 'code', '.js': 'code', '.html': 'code',
            '.css': 'code', '.json': 'code',
            '.zip': 'archive', '.rar': 'archive', '.7z': 'archive',
            '.exe': 'executable', '.msi': 'executable',
            '.mp3': 'audio', '.wav': 'audio',
            '.mp4': 'video', '.avi': 'video',
        }
        icon_name = icon_map.get(ext, 'default')
        return self.icon_images.get(icon_name)

    # ========== UI Creation ==========

    def _create_accent_strip(self):
        """Create the colored accent strip at the top."""
        self.accent_strip = ctk.CTkFrame(self, height=4, corner_radius=0,
                                          fg_color=self.accent_color)
        self.accent_strip.grid(row=0, column=0, sticky="ew")

    def _create_header(self):
        """Create the header with title and path."""
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=(6, 2))

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=f"Folder {self.panel_id}",
            text_color=self.accent_color,
            font=("Segoe UI", self.base_font_size + 6, "bold")
        )
        self.title_label.pack(side="left", anchor="w")

        self.path_label = ctk.CTkLabel(
            self.header_frame,
            text="Select a folder...",
            text_color=self.theme_data["subtext"],
            font=("Segoe UI", self.base_font_size - 2)
        )
        self.path_label.pack(side="left", padx=10, anchor="w")

        # Focus button
        btn_txt = "✕" if self.is_focused else "⛶"
        self.btn_focus = ctk.CTkButton(
            self.header_frame, text=btn_txt, width=30, height=24,
            command=lambda: self.toggle_focus_callback(self.panel_id),
            font=("Segoe UI", self.base_font_size, "bold"),
            fg_color="transparent", border_width=1,
            border_color=self.theme_data["subtext"],
            text_color=self.theme_data["text"]
        )
        self.btn_focus.pack(side="right", padx=0)

    def _create_controls(self):
        """Create the control buttons and search bar."""
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=(2, 5))

        # Browse button
        self.btn_browse = ctk.CTkButton(
            self.controls_frame, text="📂 Change",
            command=self.browse_folder,
            font=("Segoe UI", self.base_font_size, "bold"),
            height=32, corner_radius=8,
            fg_color=self.accent_color, text_color="#ffffff"
        )
        self.btn_browse.pack(side="left", padx=(0, 5))

        # Up button
        self.btn_up = ctk.CTkButton(
            self.controls_frame, text="⬆", command=self.go_up,
            font=("Segoe UI", self.base_font_size, "bold"),
            width=32, height=32, corner_radius=8,
            fg_color=self.theme_data["bg"], text_color=self.theme_data["text"],
            hover_color=self.theme_data["hover"]
        )
        self.btn_up.pack(side="left", padx=2)

        # Open folder button
        self.btn_open_folder = ctk.CTkButton(
            self.controls_frame, text="↗ Open",
            command=self._open_current_folder,
            font=("Segoe UI", self.base_font_size),
            height=32, corner_radius=8,
            fg_color=self.theme_data["bg"], text_color=self.theme_data["text"],
            hover_color=self.theme_data["hover"]
        )
        self.btn_open_folder.pack(side="left")

        # Search with debouncing
        self.search_var = ctk.StringVar()
        self.search_debouncer = Debouncer(self, self.refresh_files, 300)
        self.search_var.trace_add("write", lambda *args: self.search_debouncer.trigger())

        self.search_entry = ctk.CTkEntry(
            self.controls_frame, textvariable=self.search_var,
            width=140, height=32,
            placeholder_text="🔍 Search...",
            font=("Segoe UI", self.base_font_size),
            corner_radius=8, border_width=0
        )
        self.search_entry.pack(side="right")

        # Filter combo
        self.filter_var = ctk.StringVar(value="All Types")
        self.filter_combo = ctk.CTkComboBox(
            self.controls_frame, variable=self.filter_var,
            width=110, height=32,
            values=['All Types', 'Excel', 'PDF', 'Word', 'Images', 'Text'],
            command=self.refresh_files,
            font=("Segoe UI", self.base_font_size),
            dropdown_font=("Segoe UI", self.base_font_size),
            corner_radius=8, border_width=0
        )
        self.filter_combo.pack(side="right", padx=5)

        # Content search toggle
        self.content_search_var = ctk.BooleanVar()
        self.content_search_cb = ctk.CTkCheckBox(
            self.controls_frame, text="Content",
            variable=self.content_search_var,
            command=self.refresh_files,
            font=("Segoe UI", self.base_font_size)
        )
        self.content_search_cb.pack(side="right", padx=5)

    def _create_treeview(self):
        """Create the file list treeview."""
        self.tree_container = ctk.CTkFrame(self, fg_color="transparent")
        self.tree_container.grid(row=3, column=0, sticky="nsew", padx=2, pady=(0, 2))

        columns = ("size", "date")
        self.tree = ttk.Treeview(
            self.tree_container, columns=columns,
            show="tree headings", selectmode="extended"
        )

        self.tree.heading("#0", text="Name", command=lambda: self._sort_tree("#0", False))
        self.tree.column("#0", width=300, stretch=True)
        self.tree.heading("size", text="Size", command=lambda: self._sort_tree("size", False))
        self.tree.heading("date", text="Date", command=lambda: self._sort_tree("date", False))
        self.tree.column("size", width=100, anchor="e", stretch=False)
        self.tree.column("date", width=160, anchor="center", stretch=False)

        # Scrollbars
        vsb = ttk.Scrollbar(self.tree_container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        # Style
        style = ttk.Style()
        style.configure("Treeview.Heading",
                       background=self.theme_data["bg"],
                       foreground=self.theme_data["text"], relief="flat")
        style.map("Treeview.Heading",
                 background=[("active", self.theme_data["hover"])],
                 foreground=[("active", self.theme_data["text"])])

        # Configure tag colors
        normal_font = ("Segoe UI", self.base_font_size)
        for name, color in TAG_COLORS.items():
            self.tree.tag_configure(name, foreground="#000000", background=color, font=normal_font)

        # Event bindings
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Button-3>", self._on_right_click)

    def _create_analytics_bar(self):
        """Create the analytics bar widget."""
        self.analytics_bar = AnalyticsBar(self, self.theme_data, self.base_font_size)
        self.analytics_bar.grid(row=4, column=0, sticky="ew", padx=5, pady=(2, 5))

    # ========== Navigation ==========

    def update_header(self):
        """Update the header labels with current path info."""
        if self.current_path and os.path.exists(self.current_path):
            folder_name = os.path.basename(self.current_path) or self.current_path
            self.title_label.configure(text=folder_name)
            short_path = self.current_path if len(self.current_path) < 40 else "..." + self.current_path[-40:]
            self.path_label.configure(text=short_path)
        else:
            self.title_label.configure(text=f"Folder {self.panel_id}")
            self.path_label.configure(text="Empty")

    def browse_folder(self):
        """Open folder selection dialog."""
        folder = filedialog.askdirectory()
        if folder:
            self.set_path(folder)

    def go_up(self):
        """Navigate to parent directory."""
        if self.current_path and os.path.exists(self.current_path):
            parent = os.path.dirname(self.current_path)
            if parent and os.path.exists(parent):
                self.set_path(parent)

    def set_path(self, path):
        """Set current path and refresh."""
        self.current_path = path
        self.config_data[self.panel_id] = path
        self.save_callback()
        self.update_header()
        self.refresh_files()
        self.start_watchdog()

    def start_watchdog(self):
        """Start file system watcher for current path."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
        if self.current_path and os.path.exists(self.current_path):
            self.observer = Observer()
            event_handler = FolderChangeHandler(lambda: self.after(100, self.refresh_files))
            self.observer.schedule(event_handler, self.current_path, recursive=False)
            self.observer.start()

    def _open_current_folder(self):
        """Open current folder in system file manager."""
        if self.current_path and os.path.exists(self.current_path):
            open_path(self.current_path)

    def _quick_look(self):
        """Open QuickLook preview for selected file."""
        item = self.tree.selection()
        if item:
            fpath = self.tree.item(item, "tags")[0]
            if os.path.exists(fpath) and os.path.isfile(fpath):
                QuickLookWindow(self, fpath)

    # ========== File List Display ==========

    def _get_extensions(self):
        """Get file extensions for current filter."""
        selection = self.filter_var.get()
        filters = {
            "Excel": ['.xlsx', '.xlsm', '.xls', '.csv'],
            "PDF": ['.pdf'],
            "Word": ['.docx', '.doc'],
            "Images": ['.jpg', '.jpeg', '.png', '.gif'],
            "Text": ['.txt', '.md', '.log'],
        }
        return filters.get(selection, [])

    def refresh_files(self, _=None):
        """Refresh the file list."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self.current_path or not os.path.exists(self.current_path):
            self.update_header()
            self.analytics_bar.update([])
            return

        self.update_header()
        valid_exts = self._get_extensions()
        search_term = self.search_var.get().lower()
        content_search = self.content_search_var.get()
        text_exts = ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.log', '.xml', '.ini', '.cfg']

        files_data = []

        try:
            all_items = sorted(os.listdir(self.current_path), key=str.lower)

            # Separate and display folders first
            for item in all_items:
                full_path = os.path.join(self.current_path, item)
                if os.path.isdir(full_path) and not item.startswith('.'):
                    if search_term and search_term not in item.lower():
                        continue
                    icon = self._get_file_icon(item, is_folder=True)
                    item_kwargs = {"text": item, "values": ["", ""], "tags": (full_path, "folder")}
                    if icon:
                        item_kwargs["image"] = icon
                    self.tree.insert("", "end", **item_kwargs)

            # Then display files
            for item in all_items:
                full_path = os.path.join(self.current_path, item)
                if not os.path.isfile(full_path):
                    continue

                ext = os.path.splitext(item)[1].lower()
                if valid_exts and ext not in valid_exts:
                    continue

                # Search matching
                if search_term:
                    name_match = search_term in item.lower()
                    content_match = False
                    if content_search and ext in text_exts:
                        try:
                            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read(10000).lower()
                                content_match = search_term in content
                        except Exception:
                            content_match = False
                    if not (name_match or content_match):
                        continue

                raw_size, size_mb, mod = get_file_info(full_path)
                size_str = f"{size_mb:.2f} MB"

                # Check for tags & notes
                tags = [full_path]
                meta = MetadataService.get_tag(full_path)
                display_name = item
                if meta.get("note"):
                    display_name += " 📝"
                if meta.get("color"):
                    tags.append(meta["color"])

                files_data.append((item, size_str, mod, raw_size))

                icon = self._get_file_icon(item)
                item_kwargs = {"text": display_name, "values": [size_str, mod], "tags": tuple(tags)}
                if icon:
                    item_kwargs["image"] = icon
                self.tree.insert("", "end", **item_kwargs)

        except OSError as e:
            print(f"Error reading directory {self.current_path}: {e}")

        self.analytics_bar.update(files_data)

    def _sort_tree(self, col, reverse):
        """Sort treeview by column."""
        items = [(self.tree.set(k, col) if col != "#0" else self.tree.item(k, "text"), k)
                 for k in self.tree.get_children('')]
        if col == "size":
            items.sort(key=lambda x: float(x[0].split()[0]) if x[0] else 0, reverse=reverse)
        else:
            items.sort(key=lambda x: x[0].lower(), reverse=reverse)
        for i, (_, k) in enumerate(items):
            self.tree.move(k, '', i)
        self.tree.heading(col, command=lambda: self._sort_tree(col, not reverse))

    # ========== Event Handlers ==========

    def _on_double_click(self, event):
        """Handle double-click on tree item."""
        item = self.tree.selection()
        if item:
            fpath = self.tree.item(item, "tags")[0]
            if os.path.isdir(fpath):
                self.set_path(fpath)
            else:
                open_path(fpath)

    def _on_right_click(self, event):
        """Handle right-click context menu."""
        item = self.tree.identify_row(event.y)
        selected_items = self.tree.selection()
        panels = self.get_panels_callback()

        if len(selected_items) > 1:
            # Bulk operations
            file_paths = [
                self.tree.item(sel, "tags")[0]
                for sel in selected_items
                if os.path.isfile(self.tree.item(sel, "tags")[0])
            ]
            if file_paths:
                menu = self.menu_builder.build_bulk_menu(
                    file_paths=file_paths,
                    on_bulk_copy=lambda: self._bulk_copy(file_paths),
                    on_bulk_delete=lambda: self._bulk_delete(file_paths),
                    panels=panels,
                    current_panel=self,
                    on_bulk_move=self._bulk_move,
                    on_paste=self._paste_file
                )
                menu.tk_popup(event.x_root, event.y_root)
        elif item:
            self.tree.selection_set(item)
            fpath = self.tree.item(item, "tags")[0]

            menu = self.menu_builder.build_single_file_menu(
                fpath=fpath,
                on_open=lambda: open_path(fpath),
                on_copy=lambda: self._copy_file(fpath),
                on_cut=lambda: self._cut_file(fpath),
                on_rename=lambda: self._rename_file(fpath),
                on_delete=lambda: self._delete_file(fpath),
                panels=panels,
                current_panel=self,
                on_move=self._move_file,
                on_tag=self._set_file_tag,
                on_note=self._add_file_note,
                on_clear_tags=self._clear_file_tags,
                on_view_note=lambda: self._view_file_note(fpath),
                on_paste=self._paste_file
            )
            menu.tk_popup(event.x_root, event.y_root)

    # ========== File Operations ==========

    def _copy_selected(self):
        item = self.tree.selection()
        if item:
            self._copy_file(self.tree.item(item, "tags")[0])

    def _cut_selected(self):
        item = self.tree.selection()
        if item:
            self._cut_file(self.tree.item(item, "tags")[0])

    def _delete_selected(self):
        item = self.tree.selection()
        if item:
            self._delete_file(self.tree.item(item, "tags")[0])

    def _copy_file(self, fpath):
        InternalClipboard.set(fpath, 'copy', self)
        self._show_indicator("Copied")

    def _cut_file(self, fpath):
        InternalClipboard.set(fpath, 'cut', self)
        self._show_indicator("Cut")

    def _show_indicator(self, text):
        if self.clipboard_indicator:
            self.clipboard_indicator.destroy()
        self.clipboard_indicator = ctk.CTkLabel(
            self.header_frame, text=text, text_color=self.accent_color,
            font=("Segoe UI", self.base_font_size, "bold")
        )
        self.clipboard_indicator.pack(side="right", padx=5)

    def clear_clipboard_indicator(self):
        if self.clipboard_indicator:
            self.clipboard_indicator.destroy()
            self.clipboard_indicator = None

    def _paste_file(self):
        src, op = InternalClipboard.get()
        if not src or not os.path.exists(src):
            return
        try:
            if op == 'copy':
                FileOperations.copy_file(src, self.current_path)
            elif op == 'cut':
                FileOperations.move_file(src, self.current_path)
                InternalClipboard.clear()
        except (OSError, Exception) as e:
            messagebox.showerror("Error", f"Cannot paste file: {e}")

    def _rename_file(self, fpath):
        dialog = ctk.CTkInputDialog(text="New name:", title="Rename")
        new_name = dialog.get_input()
        if new_name:
            try:
                FileOperations.rename_file(fpath, new_name)
                self.refresh_files()
            except OSError as e:
                messagebox.showerror("Error", f"Cannot rename file: {e}")

    def _delete_file(self, fpath):
        fname = os.path.basename(fpath)
        if messagebox.askyesno("Delete", f"Delete {fname}?"):
            try:
                FileOperations.delete_file(fpath)
            except OSError as e:
                messagebox.showerror("Error", f"Cannot delete file: {e}")

    def _move_file(self, fpath, target_panel):
        try:
            FileOperations.move_file(fpath, target_panel.current_path)
        except (OSError, Exception) as e:
            messagebox.showerror("Error", f"Cannot move file: {e}")

    # ========== Tagging Operations ==========

    def _set_file_tag(self, fpath, color):
        MetadataService.set_tag(fpath, color=color)
        self.refresh_files()

    def _add_file_note(self, fpath):
        dialog = ctk.CTkInputDialog(text="Enter note:", title="Add Note")
        note = dialog.get_input()
        if note is not None:
            MetadataService.set_tag(fpath, note=note)
            self.refresh_files()

    def _clear_file_tags(self, fpath):
        MetadataService.remove_tag(fpath)
        self.refresh_files()

    def _view_file_note(self, fpath):
        note = MetadataService.get_tag(fpath).get("note", "")
        messagebox.showinfo(f"Note for {os.path.basename(fpath)}", note)

    # ========== Bulk Operations ==========

    def _bulk_copy(self, file_paths):
        for fpath in file_paths:
            self._copy_file(fpath)
        self._show_indicator("Bulk Copied")

    def _bulk_delete(self, file_paths):
        count = len(file_paths)
        if messagebox.askyesno("Bulk Delete", f"Delete {count} selected files?"):
            succeeded, failed = FileOperations.bulk_delete(file_paths)
            for path, error in failed:
                messagebox.showerror("Error", f"Cannot delete {os.path.basename(path)}: {error}")
            self.refresh_files()
            self._show_indicator(f"Deleted {len(succeeded)} files")

    def _bulk_move(self, file_paths, target_panel):
        succeeded, failed = FileOperations.bulk_move(file_paths, target_panel.current_path)
        for path, error in failed:
            messagebox.showerror("Error", f"Cannot move {os.path.basename(path)}: {error}")
        self._show_indicator("Bulk Moved")

    # ========== Utility ==========

    def update_font_size(self, new_size):
        """Update font sizes across the panel."""
        self.base_font_size = new_size
        self.title_label.configure(font=("Segoe UI", new_size + 6, "bold"))
        self.path_label.configure(font=("Segoe UI", new_size - 2))
        self.btn_browse.configure(font=("Segoe UI", new_size, "bold"), height=int(new_size * 2.0))
        self.btn_up.configure(font=("Segoe UI", new_size, "bold"), height=int(new_size * 2.0))
        self.btn_open_folder.configure(font=("Segoe UI", new_size), height=int(new_size * 2.0))
        self.search_entry.configure(font=("Segoe UI", new_size), height=int(new_size * 2.0))
        self.filter_combo.configure(font=("Segoe UI", new_size),
                                    dropdown_font=("Segoe UI", new_size),
                                    height=int(new_size * 2.0))
        self.btn_focus.configure(font=("Segoe UI", new_size, "bold"))
        self.analytics_bar.update_font_size(new_size)
        self.menu_builder = ContextMenuBuilder(self, "Segoe UI", new_size)

    def destroy(self):
        """Clean up resources on destroy."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
        super().destroy()
