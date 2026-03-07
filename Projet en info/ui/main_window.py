import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageDraw, ImageTk

from utils.interfaces import list_interfaces
from ui.traffic_view import TrafficView
from ui.alerts_view import AlertsView
from controller.capture_controller import CaptureController


class IDSMainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mini IDS – Network Monitor")
        self.root.geometry("1400x850")
        self.root.configure(bg="#1e1e1e")

        # Counters
        self.packet_count = 0
        self.alert_count = 0
        self.info_count = 0

        # Graph data
        self.packet_history = []
        self.last_packet_total = 0

        # Stats panel visibility
        self.stats_visible = tk.BooleanVar(value=True)

        # Pillow image reference (for pie chart)
        self.pie_image = None

        self._style()
        self._build_ui()
        self._init_controller()
        self._build_menu()
        self._schedule_graph_update()

    # ----------------------------------------------------------------------
    # CONTROLLER INIT
    # ----------------------------------------------------------------------
    def _init_controller(self):

        def traffic_ui_update(text, color):
            self.activity_text.config(text=text, fg=color)
            self.activity_dot.config(fg=color)

        def packet_ui_callback(pkt):
            self.packet_count += 1
            self.stats_packets_label.config(text=f"Packets capturés : {self.packet_count}")
            self.traffic.add_packet(pkt)

        def alert_ui_callback(msg):
            self.alert_count += 1
            self.stats_alerts_label.config(text=f"Alertes détectées : {self.alert_count}")
            self.alerts.add_alert(msg)

        def info_ui_callback(msg):
            self.info_count += 1
            self.stats_info_label.config(text=f"Messages info : {self.info_count}")
            self.alerts.add_info(msg)

        self.controller = CaptureController(
            iface_getter=lambda: self.interfaces_map.get(self.iface_var.get()),
            ui_traffic_callback=packet_ui_callback,
            ui_monitor_callback=traffic_ui_update,
            ui_alert_callback=alert_ui_callback,
            ui_info_callback=info_ui_callback
        )

        def capture_status_update(is_running: bool):
            if is_running:
                self.capture_status.config(text="Running", fg="lime")
            else:
                self.capture_status.config(text="Stopped", fg="gray")

        self.controller.set_capture_status_callback(capture_status_update)

    # ----------------------------------------------------------------------
    # MENU
    # ----------------------------------------------------------------------
    def _build_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # FICHIER
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exporter trafic", command=self._export_traffic)
        file_menu.add_command(label="Exporter alertes", command=self._export_alerts)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        menubar.add_cascade(label="Fichier", menu=file_menu)

        # CAPTURE
        capture_menu = tk.Menu(menubar, tearoff=0)
        capture_menu.add_command(label="Démarrer", command=self.controller.start_capture)
        capture_menu.add_command(label="Arrêter", command=self.controller.stop_capture)
        capture_menu.add_separator()
        capture_menu.add_command(label="Tester règles IDS", command=self.controller.test_rules)
        menubar.add_cascade(label="Capture", menu=capture_menu)

        # AFFICHAGE
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Effacer trafic", command=self._clear_traffic)
        view_menu.add_command(label="Effacer messages", command=self._clear_messages)
        view_menu.add_separator()
        view_menu.add_checkbutton(
            label="Auto-scroll trafic",
            variable=self.traffic.auto_scroll_var,
            command=self.traffic.toggle_auto_scroll
        )
        view_menu.add_checkbutton(
            label="Statistiques",
            variable=self.stats_visible,
            command=self._toggle_stats_panel
        )
        menubar.add_cascade(label="Affichage", menu=view_menu)

        # OUTILS
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(
            label="Activer filtre trafic",
            command=lambda: self.traffic.filter_entry.focus()
        )
        tools_menu.add_command(label="Debug (à venir)")
        menubar.add_cascade(label="Outils", menu=tools_menu)

        # AIDE
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(
            label="À propos",
            command=lambda: self.alerts.add_info("Mini IDS v1.0 – par Olivier")
        )
        menubar.add_cascade(label="Aide", menu=help_menu)

    # ----------------------------------------------------------------------
    # STYLE
    # ----------------------------------------------------------------------
    def _style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TCombobox",
            fieldbackground="#2d2d30",
            background="#3c3c3c",
            foreground="white",
            arrowcolor="white"
        )

        style.configure(
            "Treeview",
            background="#252526",
            foreground="white",
            fieldbackground="#252526",
            rowheight=28,
            bordercolor="#3c3c3c",
            borderwidth=0
        )
        style.map("Treeview", background=[("selected", "#007acc")])

    # ----------------------------------------------------------------------
    # UI BUILD
    # ----------------------------------------------------------------------
    def _build_ui(self):
        # TOP BAR
        top = tk.Frame(self.root, bg="#1e1e1e")
        top.pack(fill="x", padx=12, pady=10)

        tk.Label(
            top, text="Interface :", bg="#1e1e1e", fg="white",
            font=("Segoe UI", 11)
        ).pack(side="left")

        self.iface_var = tk.StringVar()
        self.iface_combo = ttk.Combobox(
            top, textvariable=self.iface_var, state="readonly", width=45
        )
        self.iface_combo.pack(side="left", padx=10)

        self.interfaces_map = {}
        display = ["Any (auto)"]
        for label, device in list_interfaces():
            display.append(label)
            self.interfaces_map[label] = device

        self.iface_combo["values"] = display
        self.iface_combo.current(0)

        # Start / Stop buttons
        self._modern_button(
            top, "▶ Start", "#0e639c",
            lambda: self.controller.start_capture() if hasattr(self, "controller") else None
        ).pack(side="left", padx=6)

        self._modern_button(
            top, "⏹ Stop", "#c50f1f",
            lambda: self.controller.stop_capture() if hasattr(self, "controller") else None
        ).pack(side="left", padx=6)

        # Status
        status_frame = tk.Frame(top, bg="#1e1e1e")
        status_frame.pack(side="left", padx=20)

        self.activity_dot = tk.Label(
            status_frame, text="●", fg="red", bg="#1e1e1e",
            font=("Segoe UI", 18, "bold")
        )
        self.activity_dot.pack(side="left")

        self.activity_text = tk.Label(
            status_frame, text="No traffic", fg="gray", bg="#1e1e1e",
            font=("Segoe UI", 10)
        )
        self.activity_text.pack(side="left", padx=5)

        self.capture_status = tk.Label(
            status_frame, text="Stopped", fg="gray", bg="#1e1e1e",
            font=("Segoe UI", 10, "bold")
        )
        self.capture_status.pack(side="left", padx=10)

        ttk.Separator(self.root, orient="horizontal").pack(fill="x", pady=5)

        # MAIN AREA (GRID)
        self.main_container = tk.Frame(self.root, bg="#1e1e1e")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=0)

        # LEFT COLUMN
        self.left_col = tk.Frame(self.main_container, bg="#1e1e1e")
        self.left_col.grid(row=0, column=0, sticky="nsew")

        # RIGHT COLUMN (stats)
        self.right_col = tk.Frame(self.main_container, bg="#1e1e1e")
        self.right_col.grid(row=0, column=1, sticky="ns")

        # LEFT: TRAFFIC
        traffic_card = tk.Frame(self.left_col, bg="#252526", bd=1, relief="solid")
        traffic_card.pack(fill="both", expand=True, padx=5, pady=5)

        self.traffic = TrafficView(traffic_card)
        self.traffic.pack(fill="both", expand=True, padx=10, pady=10)

        # LEFT: ALERTS
        alerts_card = tk.Frame(self.left_col, bg="#252526", bd=1, relief="solid")
        alerts_card.pack(fill="x", padx=5, pady=5)

        self.alerts = AlertsView(alerts_card)
        self.alerts.pack(fill="x", padx=10, pady=10)

        # RIGHT: STATS PANEL
        self.stats_panel = tk.Frame(self.right_col, bg="#252526", bd=1, relief="solid")
        self.stats_panel.pack(fill="y", padx=5, pady=5)

        stats_title = tk.Label(
            self.stats_panel,
            text="Statistiques",
            bg="#252526",
            fg="white",
            font=("Segoe UI", 12, "bold")
        )
        stats_title.pack(anchor="w", padx=10, pady=(8, 4))

        self.stats_packets_label = tk.Label(
            self.stats_panel,
            text="Packets capturés : 0",
            bg="#252526",
            fg="#4da6ff",
            font=("Segoe UI", 10)
        )
        self.stats_packets_label.pack(anchor="w", padx=10, pady=2)

        self.stats_alerts_label = tk.Label(
            self.stats_panel,
            text="Alertes détectées : 0",
            bg="#252526",
            fg="#ff3333",
            font=("Segoe UI", 10)
        )
        self.stats_alerts_label.pack(anchor="w", padx=10, pady=2)

        self.stats_info_label = tk.Label(
            self.stats_panel,
            text="Messages info : 0",
            bg="#252526",
            fg="#ffaa00",
            font=("Segoe UI", 10)
        )
        self.stats_info_label.pack(anchor="w", padx=10, pady=2)

        # Graph inside stats panel
        self.graph_canvas = tk.Canvas(
            self.stats_panel,
            bg="#151515",
            height=160,
            highlightthickness=0
        )
        self.graph_canvas.pack(fill="x", padx=10, pady=10)

        # PIE CHART CANVAS
        self.pie_canvas = tk.Canvas(
            self.stats_panel,
            bg="#151515",
            height=220,
            highlightthickness=0
        )
        self.pie_canvas.pack(fill="x", padx=10, pady=10)

        # LEGEND FRAME (colored squares)
        self.legend_frame = tk.Frame(self.stats_panel, bg="#252526")
        self.legend_frame.pack(anchor="w", padx=10, pady=(0, 10))
            # ----------------------------------------------------------------------
    # BUTTON HELPERS
    # ----------------------------------------------------------------------
    def _modern_button(self, parent, text, color, command):
        btn = tk.Label(
            parent, text=text, bg=color, fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=14, pady=6, cursor="hand2"
        )
        btn.bind("<Button-1>", lambda e: command())
        btn.bind("<Enter>", lambda e: btn.config(bg=self._lighten(color)))
        btn.bind("<Leave>", lambda e: btn.config(bg=color))
        return btn

    def _lighten(self, color):
        c = int(color[1:], 16)
        r = min(255, (c >> 16) + 30)
        g = min(255, ((c >> 8) & 0xFF) + 30)
        b = min(255, (c & 0xFF) + 30)
        return f"#{r:02x}{g:02x}{b:02x}"

    # ----------------------------------------------------------------------
    # STATS PANEL TOGGLE
    # ----------------------------------------------------------------------
    def _toggle_stats_panel(self):
        if self.stats_visible.get():
            self.right_col.grid(row=0, column=1, sticky="ns")
        else:
            self.right_col.grid_forget()

        self.main_container.grid_columnconfigure(0, weight=1)

    # ----------------------------------------------------------------------
    # CLEAR / EXPORT
    # ----------------------------------------------------------------------
    def _clear_traffic(self):
        self.traffic.clear()
        self.packet_count = 0
        self.stats_packets_label.config(text="Packets capturés : 0")

    def _clear_messages(self):
        self.alerts.clear()
        self.alert_count = 0
        self.info_count = 0
        self.stats_alerts_label.config(text="Alertes détectées : 0")
        self.stats_info_label.config(text="Messages info : 0")

    def _export_traffic(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not path:
            return
        self.traffic.export_csv(path)

    def _export_alerts(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return
        self.alerts.export_alerts(path)

    # ----------------------------------------------------------------------
    # GRAPH UPDATE
    # ----------------------------------------------------------------------
    def _schedule_graph_update(self):
        self.root.after(1000, self._update_graph_data)

    def _update_graph_data(self):
        delta = self.packet_count - self.last_packet_total
        self.last_packet_total = self.packet_count

        self.packet_history.append(delta)
        if len(self.packet_history) > 50:
            self.packet_history.pop(0)

        self._draw_graph()
        self._draw_protocol_pie()

        self._schedule_graph_update()

    # ----------------------------------------------------------------------
    # DRAW VERTICAL GRAPH
    # ----------------------------------------------------------------------
    def _draw_graph(self):
        self.graph_canvas.delete("all")
        w = self.graph_canvas.winfo_width() or 200
        h = self.graph_canvas.winfo_height() or 160

        if not self.packet_history:
            return

        max_val = max(self.packet_history) or 1
        bar_width = max(2, w / max(50, len(self.packet_history)))

        for i, val in enumerate(self.packet_history):
            x0 = i * bar_width
            x1 = x0 + bar_width - 1
            height = (val / max_val) * (h - 30)
            y0 = h - height - 10
            y1 = h - 10
            self.graph_canvas.create_rectangle(
                x0, y0, x1, y1,
                fill="#4da6ff",
                outline=""
            )

        self.graph_canvas.create_text(
            10, 10,
            anchor="nw",
            fill="#cccccc",
            font=("Segoe UI", 9),
            text=f"Packets/s (dernières {len(self.packet_history)}s)"
        )

    # ----------------------------------------------------------------------
    # DRAW PIE CHART (PILLOW)
    # ----------------------------------------------------------------------
    def _draw_protocol_pie(self):
        self.pie_canvas.delete("all")

        items = self.traffic.table.get_children()
        if not items:
            return

        proto_counts = {}
        for item in items:
            row = self.traffic.table.item(item, "values")
            proto = row[2]
            proto_counts[proto] = proto_counts.get(proto, 0) + 1

        total = sum(proto_counts.values())
        if total == 0:
            return

        colors = {
            "TCP": "#4da6ff",
            "UDP": "#b366ff",
            "ICMP": "#66ff66"
        }

        img = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        start_angle = 0

        for proto, count in proto_counts.items():
            pct = (count / total) * 100
            extent = (count / total) * 360

            color = colors.get(proto, "#888888")

            draw.pieslice(
                [0, 0, 200, 200],
                start=start_angle,
                end=start_angle + extent,
                fill=color
            )

            start_angle += extent

        self.pie_image = ImageTk.PhotoImage(img)
        self.pie_canvas.create_image(100, 100, image=self.pie_image)

        self._update_legend(proto_counts, total)

    # ----------------------------------------------------------------------
    # LEGEND WITH COLORED SQUARES
    # ----------------------------------------------------------------------
    def _update_legend(self, proto_counts, total):
        for widget in self.legend_frame.winfo_children():
            widget.destroy()

        colors = {
            "TCP": "#4da6ff",
            "UDP": "#b366ff",
            "ICMP": "#66ff66"
        }

        ordered = ["TCP", "UDP", "ICMP"]
        for proto in proto_counts:
            if proto not in ordered:
                ordered.append(proto)

        for proto in ordered:
            count = proto_counts.get(proto, 0)
            pct = (count / total * 100) if total > 0 else 0
            color = colors.get(proto, "#888888")

            row = tk.Frame(self.legend_frame, bg="#252526")
            row.pack(anchor="w")

            # Color square
            box = tk.Canvas(row, width=12, height=12, bg="#252526", highlightthickness=0)
            box.create_rectangle(0, 0, 12, 12, fill=color, outline=color)
            box.pack(side="left", padx=(0, 6))

            # Text
            label = tk.Label(
                row,
                text=f"{proto} : {pct:.1f}%",
                bg="#252526",
                fg="white",
                font=("Segoe UI", 9)
            )
            label.pack(side="left")

                # ----------------------------------------------------------------------
    # RUN
    # ----------------------------------------------------------------------
    def run(self):
        self.root.mainloop()