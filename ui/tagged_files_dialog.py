
import os
import sys
import datetime
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox

from services.metadata_service import MetadataService
from utils.files import open_path, get_file_info
from ui.styles import THEMES, TAG_COLORS


class TaggedFilesDialog(ctk.CTkToplevel):
    """Tagged Files Manager with category grouping, selection, and bulk delete."""
    
    def __init__(self, parent, theme_name="Light", font_size=14):
        super().__init__(parent)
        self.parent = parent
        self.theme_name = theme_name
        self.base_font_size = font_size
        self.theme = THEMES[theme_name]
        
        self.title("Tagged Files")
        
        # Position on left side of screen, full height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        dialog_width = 550
        dialog_height = screen_height - 80  # Leave space for taskbar
        x_position = 0  # Left edge
        y_position = 0  # Top edge
        
        self.geometry(f"{dialog_width}x{dialog_height}+{x_position}+{y_position}")
        self.minsize(300, 400)
        self.after(10, lambda: self.lift())
        self.attributes('-topmost', True)
        
        # Category styling
        self.category_styles = {
            "red": {
                "header_text": "#C62828",
                "bg": "#FFEBEE",
                "hover": "#FFCDD2",
                "text": "#B71C1C",
                "border": "#EF5350"
            },
            "green": {
                "header_text": "#2E7D32",
                "bg": "#E8F5E9",
                "hover": "#C8E6C9",
                "text": "#1B5E20",
                "border": "#66BB6A"
            },
            "yellow": {
                "header_text": "#F57F17",
                "bg": "#FFF8E1",
                "hover": "#FFECB3",
                "text": "#E65100",
                "border": "#FFCA28"
            }
        }
        
        self.category_labels = {
            "red": "Red · Very Important",
            "green": "Green · Important",
            "yellow": "Yellow · Review"
        }
        
        # Data
        self.tagged_files = {}
        self.selected_paths = {}  # {path: BooleanVar}
        
        # State
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._on_filter_change)
        self.filter_color_var = ctk.StringVar(value="All")
        self.sort_var = ctk.StringVar(value="Name (A-Z)")
        
        # UI Setup
        self.configure(fg_color=self.theme["bg"])
        self._setup_ui()
        self.refresh_data()

    def _setup_ui(self):
        # --- Header ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 8))
        
        ctk.CTkLabel(
            header_frame, 
            text="Tagged Files", 
            font=("Segoe UI", 20, "bold"), 
            text_color=self.theme["text"]
        ).pack(side="left")
        
        # Close button
        ctk.CTkButton(
            header_frame, text="✕", width=32, height=32,
            command=self.destroy,
            fg_color="transparent", hover_color=self.theme["hover"],
            text_color=self.theme["subtext"], font=("Segoe UI", 16)
        ).pack(side="right")
        
        # --- Toolbar ---
        toolbar = ctk.CTkFrame(self, fg_color=self.theme["card"], corner_radius=8)
        toolbar.pack(fill="x", padx=15, pady=5)
        
        # Search label and entry
        ctk.CTkLabel(toolbar, text="Search:", font=("Segoe UI", 12), text_color=self.theme["subtext"]).pack(side="left", padx=(10, 5))
        self.search_entry = ctk.CTkEntry(
            toolbar, 
            textvariable=self.search_var, 
            placeholder_text="🔍 Type to search...", 
            width=160, height=32,
            border_width=0, 
            fg_color=self.theme["bg"],
            font=("Segoe UI", 12)
        )
        self.search_entry.pack(side="left", padx=5, pady=8)
        
        # Filter Color
        ctk.CTkLabel(toolbar, text="Filter:", font=("Segoe UI", 12), text_color=self.theme["subtext"]).pack(side="left", padx=(5, 3))
        self.color_filter = ctk.CTkOptionMenu(
            toolbar, 
            variable=self.filter_color_var, 
            values=["All", "Red", "Green", "Yellow"],
            command=self._on_filter_change, 
            width=80, height=28,
            fg_color=self.theme["bg"], 
            button_color=self.theme["hover"],
            text_color=self.theme["text"],
            font=("Segoe UI", 11)
        )
        self.color_filter.pack(side="left", padx=3)
        
        # Sort
        ctk.CTkLabel(toolbar, text="Sort:", font=("Segoe UI", 12), text_color=self.theme["subtext"]).pack(side="left", padx=(5, 3))
        self.sort_menu = ctk.CTkOptionMenu(
            toolbar, 
            variable=self.sort_var, 
            values=["Name (A-Z)", "Name (Z-A)", "Date (Newest)", "Date (Oldest)"],
            command=self._on_filter_change, 
            width=110, height=28,
            fg_color=self.theme["bg"], 
            button_color=self.theme["hover"],
            text_color=self.theme["text"],
            font=("Segoe UI", 11)
        )
        self.sort_menu.pack(side="left", padx=3)

        # Refresh button
        ctk.CTkButton(
            toolbar, text="↻", width=32, height=28,
            command=self.refresh_data, 
            fg_color="transparent", 
            text_color=self.theme["text"],
            hover_color=self.theme["hover"],
            font=("Segoe UI", 16)
        ).pack(side="right", padx=5)

        # --- Action Bar ---
        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.pack(fill="x", padx=15, pady=(5, 0))
        
        # Select All checkbox
        self.select_all_var = ctk.BooleanVar(value=False)
        self.select_all_cb = ctk.CTkCheckBox(
            action_bar, 
            text="Select All",
            variable=self.select_all_var,
            command=self._toggle_select_all,
            font=("Segoe UI", 12),
            checkbox_width=20,
            checkbox_height=20
        )
        self.select_all_cb.pack(side="left", padx=5)
        
        # Delete All button
        ctk.CTkButton(
            action_bar, text="🗑 Delete All", 
            width=100, height=28,
            command=self._delete_all_tags,
            fg_color="#FFCDD2", hover_color="#EF9A9A",
            text_color="#C62828",
            font=("Segoe UI", 11)
        ).pack(side="right", padx=5)
        
        # Delete Selected button - prominent blue style
        self.delete_selected_btn = ctk.CTkButton(
            action_bar, text="🗑 Delete Selected", 
            width=130, height=28,
            command=self._delete_selected,
            fg_color="#2196F3", hover_color="#1976D2",
            text_color="#FFFFFF",
            font=("Segoe UI", 11, "bold")
        )
        self.delete_selected_btn.pack(side="right", padx=5)
        
        # --- Color Change Bar ---
        color_bar = ctk.CTkFrame(self, fg_color="transparent")
        color_bar.pack(fill="x", padx=15, pady=(3, 0))
        
        ctk.CTkLabel(
            color_bar, text="Move selected to:", 
            font=("Segoe UI", 11), text_color=self.theme["subtext"]
        ).pack(side="left", padx=5)
        
        # Move to Red button
        ctk.CTkButton(
            color_bar, text="🔴 Red",
            width=70, height=26,
            command=lambda: self._change_selected_color("red"),
            fg_color="#FFEBEE", hover_color="#FFCDD2",
            text_color="#C62828",
            font=("Segoe UI", 10)
        ).pack(side="left", padx=3)
        
        # Move to Green button
        ctk.CTkButton(
            color_bar, text="🟢 Green",
            width=80, height=26,
            command=lambda: self._change_selected_color("green"),
            fg_color="#E8F5E9", hover_color="#C8E6C9",
            text_color="#2E7D32",
            font=("Segoe UI", 10)
        ).pack(side="left", padx=3)
        
        # Move to Yellow button
        ctk.CTkButton(
            color_bar, text="🟡 Yellow",
            width=80, height=26,
            command=lambda: self._change_selected_color("yellow"),
            fg_color="#FFF8E1", hover_color="#FFECB3",
            text_color="#F57F17",
            font=("Segoe UI", 10)
        ).pack(side="left", padx=3)

        # --- List Area ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # --- Footer ---
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=15, pady=(5, 10))
        
        self.status_label = ctk.CTkLabel(
            footer, text="0 files", 
            font=("Segoe UI", 12),
            text_color=self.theme["subtext"]
        )
        self.status_label.pack(side="left")
        
        self.selected_label = ctk.CTkLabel(
            footer, text="", 
            font=("Segoe UI", 12),
            text_color=self.theme["text"]
        )
        self.selected_label.pack(side="right")

    def _on_filter_change(self, *args):
        self._render_list()

    def refresh_data(self):
        MetadataService.load_tags()
        self.tagged_files = MetadataService.get_all_tags()
        self.selected_paths.clear()
        self.select_all_var.set(False)
        self._render_list()

    def _render_list(self):
        # Clear existing widgets
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        # Clear selections for paths that no longer match filter
        self.selected_paths.clear()

        search_term = self.search_var.get().lower()
        color_filter = self.filter_color_var.get().lower()
        sort_mode = self.sort_var.get()
        
        # Group files by color
        grouped = {"red": [], "green": [], "yellow": []}
        
        for path, meta in self.tagged_files.items():
            if not os.path.exists(path):
                continue
                
            tag_color = meta.get("color", "").lower()
            if tag_color not in grouped:
                continue
                
            if color_filter != "all" and tag_color != color_filter:
                continue
                
            name = os.path.basename(path)
            note = meta.get("note", "").lower()
            if search_term and (search_term not in name.lower() and search_term not in note):
                continue
            
            try:
                mtime = os.path.getmtime(path)
                size = os.path.getsize(path)
                size_str = f"{size / (1024*1024):.2f} MB" if size >= 1024*1024 else f"{size / 1024:.1f} KB"
            except OSError:
                mtime = 0
                size_str = "Unknown"
                
            grouped[tag_color].append({
                "path": path,
                "name": name,
                "note": meta.get("note", ""),
                "mtime": mtime,
                "color": tag_color,
                "size_str": size_str,
                "folder_path": os.path.dirname(path)
            })
            
            # Initialize selection variable
            self.selected_paths[path] = ctk.BooleanVar(value=False)

        # Sort within each group
        for color in grouped:
            if "Name (A-Z)" in sort_mode:
                grouped[color].sort(key=lambda x: x["name"].lower())
            elif "Name (Z-A)" in sort_mode:
                grouped[color].sort(key=lambda x: x["name"].lower(), reverse=True)
            elif "Date (Newest)" in sort_mode:
                grouped[color].sort(key=lambda x: x["mtime"], reverse=True)
            elif "Date (Oldest)" in sort_mode:
                grouped[color].sort(key=lambda x: x["mtime"])

        total_count = sum(len(items) for items in grouped.values())
        
        if total_count == 0:
            ctk.CTkLabel(
                self.scroll_frame, 
                text="No tagged files found", 
                font=("Segoe UI", 14), 
                text_color=self.theme["subtext"]
            ).pack(pady=50)
        else:
            for color in ["red", "green", "yellow"]:
                items = grouped[color]
                if not items:
                    continue
                self._create_category_section(color, items)
            
        self.status_label.configure(text=f"{total_count} tagged files")
        self._update_selected_count()

    def _create_category_section(self, color, items):
        """Create a category section with header, delete button, and file rows."""
        style = self.category_styles[color]
        
        section = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        section.pack(fill="x", pady=(0, 15))
        
        # Header row with label and delete category button
        header_row = ctk.CTkFrame(section, fg_color="transparent")
        header_row.pack(fill="x", pady=(0, 6))
        
        ctk.CTkLabel(
            header_row, 
            text=self.category_labels[color],
            font=("Segoe UI", 14, "bold"),
            text_color=style["header_text"]
        ).pack(side="left")
        
        # Delete category button
        ctk.CTkButton(
            header_row, 
            text=f"Delete All {color.capitalize()}", 
            width=120, height=24,
            command=lambda c=color: self._delete_category(c),
            fg_color=style["bg"], hover_color=style["hover"],
            text_color=style["text"],
            font=("Segoe UI", 10)
        ).pack(side="right")
        
        # File rows
        for item in items:
            self._create_file_row(section, item, style)

    def _create_file_row(self, parent, item, style):
        """Create a file row with checkbox, file info, and folder button."""
        row = ctk.CTkFrame(parent, fg_color=style["bg"], corner_radius=6)
        row.pack(fill="x", pady=2)
        
        # Checkbox
        cb = ctk.CTkCheckBox(
            row, 
            text="",
            variable=self.selected_paths[item["path"]],
            command=self._update_selected_count,
            width=24,
            checkbox_width=18,
            checkbox_height=18,
            fg_color=style["border"],
            hover_color=style["hover"]
        )
        cb.pack(side="left", padx=(8, 5), pady=8)
        
        # File info container
        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, pady=5)
        
        # File name (clickable) - regular weight font, not bold
        name_btn = ctk.CTkButton(
            info_frame,
            text=item["name"],
            anchor="w",
            command=lambda p=item["path"]: self._open_file(p),
            fg_color="transparent",
            hover_color=style["hover"],
            text_color=style["text"],
            height=24,
            font=("Segoe UI", 13)  # Regular font, slightly larger
        )
        name_btn.pack(fill="x", anchor="w")
        name_btn.bind("<Button-3>", lambda e, p=item["path"]: self._show_context_menu(e, p))
        
        # Note display (if exists) - elegant italic style
        if item["note"]:
            note_label = ctk.CTkLabel(
                info_frame,
                text=f"📝 {item['note']}",
                font=("Segoe UI", 11, "italic"),
                text_color="#5D4037",  # Warm brown color
                anchor="w"
            )
            note_label.pack(fill="x", anchor="w", padx=5)
        
        # File details: size and path in small font
        details_text = f"{item['size_str']} • {item['folder_path']}"
        details_label = ctk.CTkLabel(
            info_frame,
            text=details_text,
            font=("Segoe UI", 9),  # Smaller details
            text_color=self.theme["subtext"],
            anchor="w"
        )
        details_label.pack(fill="x", anchor="w", padx=5)
        
        # Open Folder button
        folder_btn = ctk.CTkButton(
            row,
            text="📂",
            width=36, height=36,
            command=lambda p=item["folder_path"]: open_path(p),
            fg_color="transparent",
            hover_color=style["hover"],
            text_color=style["text"],
            font=("Segoe UI", 16)
        )
        folder_btn.pack(side="right", padx=5, pady=5)

    def _toggle_select_all(self):
        """Toggle all checkboxes."""
        select = self.select_all_var.get()
        for var in self.selected_paths.values():
            var.set(select)
        self._update_selected_count()

    def _update_selected_count(self):
        """Update the selected count label."""
        count = sum(1 for var in self.selected_paths.values() if var.get())
        if count > 0:
            self.selected_label.configure(text=f"{count} selected")
        else:
            self.selected_label.configure(text="")

    def _get_selected_paths(self):
        """Get list of selected file paths."""
        return [path for path, var in self.selected_paths.items() if var.get()]

    def _delete_selected(self):
        """Delete tags from selected files."""
        selected = self._get_selected_paths()
        if not selected:
            messagebox.showinfo("No Selection", "Please select files to delete.")
            return
            
        if messagebox.askyesno("Delete Selected", f"Remove tags from {len(selected)} selected files?"):
            for path in selected:
                MetadataService.remove_tag(path)
            self.refresh_data()

    def _change_selected_color(self, new_color):
        """Change the color category of selected files."""
        selected = self._get_selected_paths()
        if not selected:
            return
            
        for path in selected:
            MetadataService.set_tag(path, color=new_color)
        
        self.refresh_data()

    def _delete_category(self, color):
        """Delete all tags in a category."""
        paths_to_delete = [
            path for path, meta in self.tagged_files.items()
            if meta.get("color", "").lower() == color and os.path.exists(path)
        ]
        
        if not paths_to_delete:
            return
            
        if messagebox.askyesno("Delete Category", f"Remove all {len(paths_to_delete)} {color} tags?"):
            for path in paths_to_delete:
                MetadataService.remove_tag(path)
            self.refresh_data()

    def _delete_all_tags(self):
        """Delete all tags."""
        total = len([p for p in self.tagged_files if os.path.exists(p)])
        if total == 0:
            return
            
        if messagebox.askyesno("Delete All", f"Remove ALL {total} tags? This cannot be undone."):
            for path in list(self.tagged_files.keys()):
                MetadataService.remove_tag(path)
            self.refresh_data()

    def _show_context_menu(self, event, path):
        """Show context menu for file actions."""
        menu = tk.Menu(self, tearoff=0, font=("Segoe UI", 11))
        menu.add_command(label="Open File", command=lambda: self._open_file(path))
        menu.add_command(label="Open Folder", command=lambda: open_path(os.path.dirname(path)))
        menu.add_separator()
        menu.add_command(label="Remove Tag", command=lambda: self._remove_tag(path))
        menu.tk_popup(event.x_root, event.y_root)

    def _open_file(self, path):
        try:
            open_path(path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}")

    def _remove_tag(self, path):
        if messagebox.askyesno("Remove Tag", f"Remove tag from '{os.path.basename(path)}'?"):
            MetadataService.remove_tag(path)
            self.refresh_data()

