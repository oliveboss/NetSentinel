import time
from collections import defaultdict
from ..rules_config import PORTSCAN_TIME_WINDOW, PORTSCAN_PORT_THRESHOLD

class PortScanRule:

    def __init__(self):
        # IP → {port: timestamp}
        self.ip_ports = defaultdict(dict)

        # Paramètres depuis le fichier de config
        self.time_window = PORTSCAN_TIME_WINDOW
        self.port_threshold = PORTSCAN_PORT_THRESHOLD

    def check(self, pkt):

        # On accepte TCP et UDP
        if pkt["proto"] not in ["TCP", "UDP"]:
            return None

        src_ip = pkt["src"]
        dst_port = pkt["dport"]
        now = time.time()

        # Enregistrer le port avec timestamp
        self.ip_ports[src_ip][dst_port] = now

        # Nettoyage des anciens ports
        expired_ports = [
            port for port, ts in self.ip_ports[src_ip].items()
            if now - ts > self.time_window
        ]

        for port in expired_ports:
            del self.ip_ports[src_ip][port]

        # Détection
        if len(self.ip_ports[src_ip]) >= self.port_threshold:
            self.ip_ports[src_ip].clear()
            return f"⚠ Possible Port Scan (TCP/UDP) détecté depuis {src_ip}"

        return None