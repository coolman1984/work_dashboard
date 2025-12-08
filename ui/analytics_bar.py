"""
Analytics Bar Widget - Displays file statistics and type distribution.

This is a self-contained widget that can be embedded in any panel.
It shows file count, total size, and a visual bar of file type distribution.
"""

import os
import tkinter as tk
from typing import List, Tuple, Dict
import customtkinter as ctk

from ui.styles import TYPE_COLORS, DEFAULT_TYPE_COLOR


class AnalyticsBar(ctk.CTkFrame):
    """Widget displaying file analytics and type distribution."""

    def __init__(
        self,
        parent: ctk.CTkFrame,
        theme_data: Dict[str, str],
        base_font_size: int = 14
    ):
        """Initialize the analytics bar.
        
        Args:
            parent: Parent widget
            theme_data: Theme configuration dictionary
            base_font_size: Base font size for text
        """
        super().__init__(parent, height=40, corner_radius=0, fg_color="transparent")
        
        self.theme_data = theme_data
        self.base_font_size = base_font_size
        
        # Canvas for distribution bar (8px height)
        self.stats_canvas = tk.Canvas(
            self,
            height=8,
            bg=theme_data["bg"],
            highlightthickness=0
        )
        self.stats_canvas.pack(fill="x", pady=(0, 4))
        
        # Label for text stats
        self.stats_label = ctk.CTkLabel(
            self,
            text="--",
            font=("Segoe UI", base_font_size - 2, "bold"),
            text_color=theme_data["subtext"]
        )
        self.stats_label.pack(anchor="e")

    def update(self, files_data: List[Tuple[str, str, str, int]]) -> None:
        """Update analytics with new file data.
        
        Args:
            files_data: List of tuples (name, size_str, date, size_bytes)
        """
        total_files = len(files_data)
        total_size_bytes = sum(f[3] for f in files_data)
        total_size_mb = total_size_bytes / (1024 * 1024)
        
        # Calculate type distribution
        type_counts: Dict[str, int] = {}
        for f in files_data:
            ext = os.path.splitext(f[0])[1].lower()
            type_counts[ext] = type_counts.get(ext, 0) + 1
        
        # Sort by frequency
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Build display text
        type_str = ", ".join([
            f"{count} {ext.replace('.', '').upper()}"
            for ext, count in sorted_types
        ])
        
        display_text = f"{total_files} Files ({total_size_mb:,.2f} MB)"
        if type_str:
            display_text += f"  •  {type_str}"
        
        self.stats_label.configure(text=display_text)
        
        # Update visual bar
        self._draw_distribution_bar(type_counts, total_files)

    def _draw_distribution_bar(self, type_counts: Dict[str, int], total_files: int) -> None:
        """Draw the colored distribution bar.
        
        Args:
            type_counts: Dictionary of extension -> count
            total_files: Total number of files
        """
        self.stats_canvas.delete("all")
        
        if total_files == 0:
            return
        
        width = self.stats_canvas.winfo_width()
        if width < 10:
            width = 300  # Fallback if not yet rendered
        
        current_x = 0
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        
        for ext, count in sorted_types:
            color = TYPE_COLORS.get(ext, DEFAULT_TYPE_COLOR)
            segment_width = (count / total_files) * width
            self.stats_canvas.create_rectangle(
                current_x, 0,
                current_x + segment_width, 8,
                fill=color,
                outline=""
            )
            current_x += segment_width

    def update_font_size(self, new_size: int) -> None:
        """Update the font size.
        
        Args:
            new_size: New base font size
        """
        self.base_font_size = new_size
        self.stats_label.configure(font=("Segoe UI", new_size - 2, "bold"))
