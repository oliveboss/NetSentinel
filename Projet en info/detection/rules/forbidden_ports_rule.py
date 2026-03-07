from ..rules_config import FORBIDDEN_PORTS

class ForbiddenPortsRule:
    def __init__(self):
        self.forbidden_ports = set(FORBIDDEN_PORTS)

    def check(self, pkt):
        dst_port = pkt.get("dport")
        if dst_port in self.forbidden_ports:
            src_ip = pkt["src"]
            return f"⚠ Tentative de connexion sur port interdit {dst_port} depuis {src_ip}"
        return None