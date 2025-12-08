import customtkinter as ctk
from ui.dashboard import WorkDashboard

if __name__ == "__main__":
    app = WorkDashboard()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
