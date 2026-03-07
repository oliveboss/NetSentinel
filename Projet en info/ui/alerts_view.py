# ui/alerts_view.py

import tkinter as tk
from tkinter import ttk
from datetime import datetime


class AlertsView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#1e1e1e")

        title = tk.Label(
            self,
            text="Messages IDS",
            font=("Segoe UI", 12, "bold"),
            fg="#ff4d4d",
            bg="#1e1e1e"
        )
        title.pack(anchor="w", padx=5, pady=(0, 4))

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True)

        # ALERTS TAB
        self.alerts_frame = tk.Frame(self.tabs, bg="#1e1e1e")
        self.alerts_text = self._make_text_widget(self.alerts_frame, "#ff3333")
        self.tabs.add(self.alerts_frame, text="Alerts")

        # INFO TAB
        self.info_frame = tk.Frame(self.tabs, bg="#1e1e1e")
        self.info_text = self._make_text_widget(self.info_frame, "#4da6ff")
        self.tabs.add(self.info_frame, text="Info")

    def _make_text_widget(self, parent, color):
        box = tk.Frame(parent, bg="#1e1e1e")
        box.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(box, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        text = tk.Text(
            box,
            height=10,
            bg="#151515",
            fg=color,
            insertbackground="white",
            font=("Consolas", 10),
            relief="flat",
            wrap="word",
            yscrollcommand=scrollbar.set
        )
        text.pack(fill="both", expand=True)

        scrollbar.config(command=text.yview)

        text.bind("<Key>", lambda e: "break")
        text.bind("<Control-c>", lambda e, t=text: self._copy_selection(t))
        text.bind("<Button-3>", lambda e, t=text: self._show_context_menu(e, t))

        return text

    def add_alert(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.alerts_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.alerts_text.see(tk.END)

    def add_info(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.info_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.info_text.see(tk.END)

    def clear(self):
        self.alerts_text.delete("1.0", tk.END)
        self.info_text.delete("1.0", tk.END)

    # --- Export ---
    def export_alerts(self, filepath):
        content = self.alerts_text.get("1.0", tk.END)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    def export_info(self, filepath):
        content = self.info_text.get("1.0", tk.END)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    def _copy_selection(self, widget):
        try:
            selected = widget.get("sel.first", "sel.last")
        except tk.TclError:
            return
        widget.clipboard_clear()
        widget.clipboard_append(selected)

    def _show_context_menu(self, event, widget):
        menu = tk.Menu(widget, tearoff=0)
        menu.add_command(label="Copier", command=lambda: self._copy_selection(widget))
        menu.add_command(label="Effacer", command=self.clear)
        menu.tk_popup(event.x_root, event.y_root)