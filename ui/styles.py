# Professional Modern Palette
ACCENT_COLORS = [
    "#007AFF",  # iOS Blue
    "#28CD41",  # iOS Green
    "#AF52DE",  # iOS Purple
    "#FF3B30",  # iOS Red
    "#FF9500",  # iOS Orange
    "#5856D6",  # Indigo
    "#00C7BE",  # Teal
    "#FF2D55",  # Pink
    "#0A84FF"   # Bright Blue
]

THEMES = {
    "Dark": {
        "mode": "Dark",
        "bg": "#121212",        # Material Dark Background
        "card": "#1E1E1E",      # Elevated Surface
        "text": "#E0E0E0",      # High Emphasis Text
        "subtext": "#A0A0A0",   # Medium Emphasis Text
        "hover": "#2D2D2D"      # Hover State
    },
    "Light": {
        "mode": "Light",
        "bg": "#F5F5F7",        # Apple-style Light Gray
        "card": "#FFFFFF",      # Pure White Card
        "text": "#1D1D1F",      # Near Black Text
        "subtext": "#86868B",   # Gray Subtext
        "hover": "#F5F5F5"      # Subtle Hover
    },
}

# File Type Colors for Analytics
TYPE_COLORS = {
    '.xlsx': '#1D6F42', '.xlsm': '#1D6F42', '.xls': '#1D6F42', '.csv': '#217346', # Excel (Modern Green)
    '.pdf': '#F40F02',                                                          # PDF (Adobe Red)
    '.docx': '#2B579A', '.doc': '#2B579A',                                      # Word (Blue)
    '.png': '#B146C2', '.jpg': '#B146C2', '.jpeg': '#B146C2',                   # Images (Purple)
    '.py': '#FFD43B', '.js': '#F7DF1E', '.html': '#E34F26',                     # Code (Yellow/Orange)
    '.txt': '#888888', '.md': '#888888', '.log': '#AAAAAA'                      # Text (Gray)
}
DEFAULT_TYPE_COLOR = "#6E6E73"

TAG_COLORS = {
    "red": "#FF3B30",
    "green": "#34C759",
    "yellow": "#FFCC00"
}
