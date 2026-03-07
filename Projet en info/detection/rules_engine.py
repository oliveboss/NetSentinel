from .rules.portscan_rule import PortScanRule
from .rules.syn_flood_rule import SynFloodRule
from .rules.icmp_scan_rule import IcmpScanRule
from .rules.forbidden_ports_rule import ForbiddenPortsRule

class RulesEngine:
    def __init__(self):
        self.rules = [
            PortScanRule(),
            SynFloodRule(),
            IcmpScanRule(),
            ForbiddenPortsRule()      # Ports interdits
        ]

    def process_packet(self, pkt):
        alerts = []
        for rule in self.rules:
            result = rule.check(pkt)
            if result:
                alerts.append(result)
        return alerts