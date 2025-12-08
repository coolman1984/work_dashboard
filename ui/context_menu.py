"""
Context Menu Builder - Constructs right-click menus for file operations.

This module separates menu construction logic from the FolderCard class,
making the UI code cleaner and menus easier to customize.
"""

import os
import tkinter as tk
from typing import Callable, List, Any, Optional

from services.metadata_service import MetadataService
from services.clipboard import InternalClipboard


class ContextMenuBuilder:
    """Builds context menus for file operations."""

    def __init__(self, parent: Any, font_family: str = "Segoe UI", font_size: int = 12):
        """Initialize the menu builder.
        
        Args:
            parent: Parent widget for menu
            font_family: Font family for menu items
            font_size: Font size for menu items
        """
        self.parent = parent
        self.font = (font_family, font_size)

    def build_single_file_menu(
        self,
        fpath: str,
        on_open: Callable,
        on_copy: Callable,
        on_cut: Callable,
        on_rename: Callable,
        on_delete: Callable,
        panels: List[Any],
        current_panel: Any,
        on_move: Callable,
        on_tag: Callable,
        on_note: Callable,
        on_clear_tags: Callable,
        on_view_note: Callable,
        on_paste: Optional[Callable] = None
    ) -> tk.Menu:
        """Build context menu for a single file.
        
        Args:
            fpath: Full path to the file
            on_open: Callback for Open action
            on_copy: Callback for Copy action
            on_cut: Callback for Cut action
            on_rename: Callback for Rename action
            on_delete: Callback for Delete action
            panels: List of all panels for Move To submenu
            current_panel: Current panel (to exclude from Move To)
            on_move: Callback for Move action, receives (fpath, target_panel)
            on_tag: Callback for tag action, receives (fpath, color)
            on_note: Callback for Add Note action
            on_clear_tags: Callback for Clear Tags action
            on_view_note: Callback for View Note action
            on_paste: Optional callback for Paste action
            
        Returns:
            Configured tk.Menu
        """
        menu = tk.Menu(self.parent, tearoff=0, font=self.font)
        
        menu.add_command(label="Open", command=on_open)
        
        if os.path.isfile(fpath):
            menu.add_separator()
            menu.add_command(label="Copy", command=on_copy)
            menu.add_command(label="Cut", command=on_cut)
            menu.add_separator()
            menu.add_command(label="Rename", command=on_rename)
            menu.add_command(label="Delete", command=on_delete)
            
            # Move To submenu
            move_menu = self._build_move_submenu(fpath, panels, current_panel, on_move)
            menu.add_separator()
            menu.add_cascade(label="Move To...", menu=move_menu)
            
            # Tags submenu
            tag_menu = self._build_tag_submenu(fpath, on_tag, on_note, on_clear_tags)
            menu.add_separator()
            menu.add_cascade(label="Tags & Notes", menu=tag_menu)
            
            # View Note if exists
            meta = MetadataService.get_tag(fpath)
            if meta.get("note"):
                menu.add_command(label="📄 View Note", command=on_view_note)
        
        # Paste option if clipboard has data
        if InternalClipboard.has_data():
            menu.add_separator()
            path, op = InternalClipboard.get()
            fname = os.path.basename(path)
            if on_paste:
                menu.add_command(label=f"Paste '{fname}'", command=on_paste)
        
        return menu

    def build_bulk_menu(
        self,
        file_paths: List[str],
        on_bulk_copy: Callable,
        on_bulk_delete: Callable,
        panels: List[Any],
        current_panel: Any,
        on_bulk_move: Callable,
        on_paste: Optional[Callable] = None
    ) -> tk.Menu:
        """Build context menu for multiple selected files.
        
        Args:
            file_paths: List of selected file paths
            on_bulk_copy: Callback for Copy All action
            on_bulk_delete: Callback for Delete All action
            panels: List of all panels
            current_panel: Current panel (to exclude from Move To)
            on_bulk_move: Callback for bulk move, receives (file_paths, target_panel)
            on_paste: Optional callback for Paste action
            
        Returns:
            Configured tk.Menu
        """
        menu = tk.Menu(self.parent, tearoff=0, font=self.font)
        
        menu.add_command(label=f"Bulk Operations ({len(file_paths)} files)", state="disabled")
        menu.add_separator()
        menu.add_command(label="Copy All", command=on_bulk_copy)
        menu.add_command(label="Delete All", command=on_bulk_delete)
        
        # Bulk move submenu
        move_menu = tk.Menu(menu, tearoff=0, font=self.font)
        added = False
        for p in panels:
            if p != current_panel and p.current_path:
                move_menu.add_command(
                    label=p.title_label.cget("text"),
                    command=lambda t=p: on_bulk_move(file_paths, t)
                )
                added = True
        
        if added:
            menu.add_separator()
            menu.add_cascade(label="Move All To...", menu=move_menu)
        
        # Paste option if clipboard has data
        if InternalClipboard.has_data() and on_paste:
            menu.add_separator()
            path, op = InternalClipboard.get()
            fname = os.path.basename(path)
            menu.add_command(label=f"Paste '{fname}'", command=on_paste)
        
        return menu

    def _build_move_submenu(
        self,
        fpath: str,
        panels: List[Any],
        current_panel: Any,
        on_move: Callable
    ) -> tk.Menu:
        """Build the 'Move To...' submenu."""
        move_menu = tk.Menu(self.parent, tearoff=0, font=self.font)
        added = False
        
        for p in panels:
            if p != current_panel and p.current_path:
                move_menu.add_command(
                    label=p.title_label.cget("text"),
                    command=lambda t=p: on_move(fpath, t)
                )
                added = True
        
        if not added:
            move_menu.add_command(label="(No other folders open)", state="disabled")
        
        return move_menu

    def _build_tag_submenu(
        self,
        fpath: str,
        on_tag: Callable,
        on_note: Callable,
        on_clear_tags: Callable
    ) -> tk.Menu:
        """Build the 'Tags & Notes' submenu."""
        tag_menu = tk.Menu(self.parent, tearoff=0, font=self.font)
        
        tag_menu.add_command(label="🔴 Very Important", command=lambda: on_tag(fpath, "red"))
        tag_menu.add_command(label="🟢 Important", command=lambda: on_tag(fpath, "green"))
        tag_menu.add_command(label="🟡 Review", command=lambda: on_tag(fpath, "yellow"))
        tag_menu.add_separator()
        tag_menu.add_command(label="📝 Add Note", command=lambda: on_note(fpath))
        tag_menu.add_command(label="❌ Clear Tags", command=lambda: on_clear_tags(fpath))
        
        return tag_menu
