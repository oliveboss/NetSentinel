import threading
import time
from capture.sniffer import start_sniffing, stop_sniffing
from utils.network_monitor import NetworkMonitor
from detection.rules_engine import RulesEngine
import state.runtime_state as state


class CaptureController:
    def __init__(self, iface_getter, ui_traffic_callback, ui_monitor_callback,
                 ui_alert_callback=None, ui_info_callback=None):

        """
        iface_getter : fonction qui retourne l'interface sélectionnée
        ui_traffic_callback : fonction(pkt) pour afficher paquet dans l'UI
        ui_monitor_callback : fonction(text, color) pour indicateur trafic
        ui_alert_callback : fonction(msg) pour afficher alertes IDS
        ui_info_callback : fonction(msg) pour afficher messages système
        """

        # Tous les paquets passent par cette méthode maintenant
        state.packet_callback = self._handle_packet

        self.iface_getter = iface_getter
        self.capture_status_callback = None

        self.ui_traffic_callback = ui_traffic_callback
        self.ui_alert_callback = ui_alert_callback
        self.ui_info_callback = ui_info_callback

        # 🔥 Moteur de détection
        self.rules_engine = RulesEngine()

        # --- Network monitor ---
        self.monitor = NetworkMonitor(
            iface_getter=iface_getter,
            ui_callback=ui_monitor_callback
        )
        self.monitor.start()

    # ------------------------------------------------------------------
    # POINT CENTRAL DES PAQUETS
    # ------------------------------------------------------------------
    def _handle_packet(self, pkt):
        # 1️⃣ Affichage trafic
        if self.ui_traffic_callback:
            self.ui_traffic_callback(pkt)

        # 2️⃣ Analyse IDS
        alerts = self.rules_engine.process_packet(pkt)

        # 3️⃣ Affichage alertes IDS
        if self.ui_alert_callback:
            for alert in alerts:
                self.ui_alert_callback(alert)

    # ------------------------------------------------------------------
    # MÉTHODE DE TEST DES RÈGLES
    # ------------------------------------------------------------------
    def test_rules(self):
        if self.ui_info_callback:
            self.ui_info_callback("🧪 Test des règles IDS lancé")

        test_packets = [
            # PortScan (10 ports différents)
            *[
                {
                    "src": "192.168.1.10",
                    "dst": "192.168.1.100",
                    "proto": "TCP",
                    "sport": 5000 + i,
                    "dport": 1000 + i,
                    "size": 60
                }
                for i in range(10)
            ],
            # SYN Flood (25 SYN)
            *[
                {
                    "src": "192.168.1.20",
                    "dst": "192.168.1.100",
                    "proto": "TCP",
                    "sport": 4000 + i,
                    "dport": 80,
                    "size": 60,
                    "flags": "S"
                }
                for i in range(25)
            ],
            # ICMP Scan
            *[
                {
                    "src": "192.168.1.30",
                    "dst": "192.168.1.100",
                    "proto": "ICMP",
                    "sport": 0,
                    "dport": 0,
                    "size": 64
                }
                for _ in range(10)
            ],
            # Ports interdits
            *[
                {
                    "src": "192.168.1.40",
                    "dst": "192.168.1.100",
                    "proto": "TCP",
                    "sport": 3333,
                    "dport": port,
                    "size": 60
                }
                for port in [22, 23, 3389]
            ]
        ]

        for pkt in test_packets:
            self._handle_packet(pkt)

        if self.ui_info_callback:
            self.ui_info_callback("🧪 Test des règles terminé")

    # ------------------------------------------------------------------
    # CAPTURE STATUS CALLBACK
    # ------------------------------------------------------------------
    def set_capture_status_callback(self, callback):
        self.capture_status_callback = callback

    # ------------------------------------------------------------------
    # START CAPTURE
    # ------------------------------------------------------------------
    def start_capture(self):
        if state.capturing:
            if self.ui_info_callback:
                self.ui_info_callback("⚠ Capture déjà en cours")
            return

        iface = self.iface_getter()

        if self.ui_info_callback:
            self.ui_info_callback(f"▶ Démarrage de la capture sur {iface or 'Any'}")

        thread = threading.Thread(
            target=start_sniffing,
            args=(iface,),
            daemon=True
        )
        thread.start()

        if self.capture_status_callback:
            self.capture_status_callback(True)

    # ------------------------------------------------------------------
    # STOP CAPTURE
    # ------------------------------------------------------------------
    def stop_capture(self):
        stop_sniffing()

        if self.ui_info_callback:
            self.ui_info_callback("⏹ Capture arrêtée")

        if self.capture_status_callback:
            self.capture_status_callback(False)