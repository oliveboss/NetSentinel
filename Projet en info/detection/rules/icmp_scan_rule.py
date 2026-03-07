import time
from collections import defaultdict
from ..rules_config import ICMP_TIME_WINDOW, ICMP_THRESHOLD

class IcmpScanRule:
    def __init__(self):
        self.ip_icmp_times = defaultdict(list)
        self.time_window = ICMP_TIME_WINDOW
        self.icmp_threshold = ICMP_THRESHOLD

    def check(self, pkt):
        if pkt["proto"] != "ICMP":
            return None

        src_ip = pkt["src"]
        now = time.time()
        self.ip_icmp_times[src_ip].append(now)

        self.ip_icmp_times[src_ip] = [t for t in self.ip_icmp_times[src_ip] if now - t <= self.time_window]

        if len(self.ip_icmp_times[src_ip]) >= self.icmp_threshold:
            self.ip_icmp_times[src_ip].clear()
            return f"⚠ Scan ICMP détecté depuis {src_ip}"

        return None