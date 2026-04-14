import time
from collections import defaultdict
from ..rules_config import SYNFLOOD_TIME_WINDOW, SYNFLOOD_SYN_THRESHOLD

class SynFloodRule:
    def __init__(self):
        self.ip_syn_times = defaultdict(list)
        self.time_window = SYNFLOOD_TIME_WINDOW
        self.syn_threshold = SYNFLOOD_SYN_THRESHOLD

    def check(self, pkt):
        if pkt["proto"] != "TCP":
            return None

        if not pkt.get("flags") or "S" not in pkt["flags"]:
            return None

        src_ip = pkt["src"]
        now = time.time()
        self.ip_syn_times[src_ip].append(now)

        # Nettoyer les timestamps vieux de plus que time_window
        self.ip_syn_times[src_ip] = [t for t in self.ip_syn_times[src_ip] if now - t <= self.time_window]

        print(f"DEBUG SYN: IP {src_ip}, flags: '{pkt.get('flags', 'NO_FLAGS')}', count: {len(self.ip_syn_times[src_ip])}/{self.syn_threshold}")

        if len(self.ip_syn_times[src_ip]) >= self.syn_threshold:
            self.ip_syn_times[src_ip].clear()
            return f"⚠ Possible SYN Flood détecté depuis {src_ip}"

        return None