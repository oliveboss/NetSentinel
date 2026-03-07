import tkinter as tk
from tkinter import ttk
import csv


class TrafficView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#1e1e1e")

        # --- Title ---
        label = tk.Label(
            self,
            text="Live Network Traffic",
            bg="#1e1e1e",
            fg="white",
            font=("Segoe UI", 12, "bold")
        )
        label.pack(anchor="w", padx=10, pady=(6, 2))

        # --- Filter bar ---
        filter_frame = tk.Frame(self, bg="#1e1e1e")
        filter_frame.pack(fill="x", padx=10, pady=(0, 4))

        tk.Label(
            filter_frame,
            text="Filter:",
            bg="#1e1e1e",
            fg="#cccccc",
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.filter_var = tk.StringVar()
        self.filter_entry = tk.Entry(
            filter_frame,
            textvariable=self.filter_var,
            bg="#252526",
            fg="white",
            insertbackground="white",
            relief="flat"
        )
        self.filter_entry.pack(side="left", fill="x", expand=True, padx=6)
        self.filter_entry.bind("<KeyRelease>", self._apply_filter)

        # --- Auto-scroll toggle variable ---
        self.auto_scroll_var = tk.BooleanVar(value=True)
        self.auto_scroll = True

        # --- Scrollbar ---
        self.scrollbar = tk.Scrollbar(self, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")

        # --- Table ---
        self.columns = ("src", "dst", "proto", "sport", "dport", "size")
        self.table = ttk.Treeview(
            self,
            columns=self.columns,
            show="headings",
            yscrollcommand=self.scrollbar.set,
            selectmode="extended"
        )
        self.table.pack(fill="both", expand=True, padx=10, pady=6)

        self.scrollbar.config(command=self.table.yview)

        # --- Column setup ---
        titles = ["Source IP", "Destination IP", "Proto", "Src Port", "Dst Port", "Size"]
        for col, title in zip(self.columns, titles):
            self.table.heading(col, text=title, command=lambda c=col: self._sort_column(c, False))
            self.table.column(col, width=140, anchor="center")

        # Data store for filtering
        self._all_rows = []

        # Detect user scrolling
        self.table.bind("<MouseWheel>", self._on_user_scroll)
        self.table.bind("<Button-4>", self._on_user_scroll)
        self.table.bind("<Button-5>", self._on_user_scroll)

        # Multi-selection fix
        self.table.bind("<Button-1>", self._select_row)

        # Copy selection with Ctrl+C
        self.table.bind("<Control-c>", self._copy_selection)

        # Right-click menu
        self.table.bind("<Button-3>", self._show_context_menu)

    # -------------------------
    # Toggle auto-scroll
    # -------------------------
    def toggle_auto_scroll(self):
        self.auto_scroll = self.auto_scroll_var.get()

    # -------------------------
    # Add packet + auto-scroll
    # -------------------------
    def add_packet(self, pkt):
        values = (
            pkt["src"],
            pkt["dst"],
            pkt["proto"],
            pkt["sport"],
            pkt["dport"],
            pkt["size"]
        )
        self._all_rows.append(values)

        if self._match_filter(values):
            self.table.insert("", "end", values=values)

        if self.auto_scroll:
            self.table.yview_moveto(1.0)

    # -------------------------
    # Clear table
    # -------------------------
    def clear(self):
        self._all_rows.clear()
        for item in self.table.get_children():
            self.table.delete(item)

    # -------------------------
    # Filter logic
    # -------------------------
    def _apply_filter(self, event=None):
        query = self.filter_var.get().strip().lower()
        # Clear view
        for item in self.table.get_children():
            self.table.delete(item)
        # Reinsert matching rows
        for row in self._all_rows:
            if not query or self._match_filter(row):
                self.table.insert("", "end", values=row)

    def _match_filter(self, values):
        query = self.filter_var.get().strip().lower()
        if not query:
            return True
        text = " ".join(str(v) for v in values).lower()
        return query in text

    # -------------------------
    # Export CSV
    # -------------------------
    def export_csv(self, filepath):
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["src", "dst", "proto", "sport", "dport", "size"])
            for row in self._all_rows:
                writer.writerow(row)

    # -------------------------
    # Detect manual scrolling
    # -------------------------
    def _on_user_scroll(self, event):
        first, last = self.table.yview()

        # Auto-scroll only reacts if user has enabled it
        if self.auto_scroll_var.get():
            self.auto_scroll = (last == 1.0)

    # -------------------------
    # Multi-selection handler
    # -------------------------
    def _select_row(self, event):
        row = self.table.identify_row(event.y)
        if not row:
            return

        if event.state & 0x0001:  # SHIFT
            self.table.selection_add(row)
        elif event.state & 0x0004:  # CTRL
            self.table.selection_toggle(row)
        else:
            self.table.selection_set(row)

    # -------------------------
    # Column sorting
    # -------------------------
    def _sort_column(self, col, reverse):
        data = []
        for item in self.table.get_children(""):
            value = self.table.set(item, col)
            try:
                value = int(value)
            except ValueError:
                pass
            data.append((value, item))

        data.sort(reverse=reverse)

        for index, (_, item) in enumerate(data):
            self.table.move(item, "", index)

        self.table.heading(col, command=lambda: self._sort_column(col, not reverse))

    # -------------------------
    # Copy selected rows
    # -------------------------
    def _copy_selection(self, event=None):
        selected = self.table.selection()
        if not selected:
            return

        rows = []
        for item in selected:
            values = self.table.item(item, "values")
            rows.append("\t".join(values))

        text = "\n".join(rows)

        self.clipboard_clear()
        self.clipboard_append(text)

    # -------------------------
    # Right-click context menu
    # -------------------------
    def _show_context_menu(self, event):
        iid = self.table.identify_row(event.y)
        if iid:
            self.table.selection_set(iid)

        menu = tk.Menu(self.table, tearoff=0)
        menu.add_command(label="Copier", command=self._copy_selection)
        menu.tk_popup(event.x_root, event.y_root)