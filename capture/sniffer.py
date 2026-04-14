# capture/sniffer.py

from scapy.all import sniff, IP, TCP, UDP, ICMP
import state.runtime_state as state

def process_packet(packet):
    if not state.packet_callback:
        return

    # Extraction des flags TCP
    flags = ""
    if TCP in packet:
        tcp_flags = packet[TCP].flags
        if tcp_flags & 0x02: flags += "S"  # SYN
        if tcp_flags & 0x10: flags += "A"  # ACK
        if tcp_flags & 0x01: flags += "F"  # FIN
        if tcp_flags & 0x04: flags += "R"  # RST
        if tcp_flags & 0x08: flags += "P"  # PSH
        if tcp_flags & 0x20: flags += "U"  # URG

    pkt = {
        "src": packet[IP].src if IP in packet else "-",
        "dst": packet[IP].dst if IP in packet else "-",
        "proto": "TCP" if TCP in packet else "UDP" if UDP in packet else "ICMP" if ICMP in packet else "OTHER",
        "sport": packet[TCP].sport if TCP in packet else packet[UDP].sport if UDP in packet else 0,
        "dport": packet[TCP].dport if TCP in packet else packet[UDP].dport if UDP in packet else 0,
        "size": len(packet),
        "flags": flags if TCP in packet else ""
    }

    # DEBUG: Afficher les paquets TCP avec flags
    if TCP in packet and flags:
        print(f"DEBUG SNIFFER: TCP {pkt['src']}:{pkt['sport']} -> {pkt['dst']}:{pkt['dport']} flags='{flags}'")

    state.packet_callback(pkt)

def start_sniffing(iface=None):
    state.capturing = True
    sniff(
        iface=iface,
        prn=process_packet,
        store=False,
        stop_filter=lambda p: not state.capturing
    )

def stop_sniffing():
    state.capturing = False
