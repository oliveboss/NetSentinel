# Fichier de configuration pour les règles de NetSentinel

# --- PortScan ---
PORTSCAN_TIME_WINDOW = 10      # secondes
PORTSCAN_PORT_THRESHOLD = 10   # nombre de ports avant alerte

# --- SYN Flood ---
SYNFLOOD_TIME_WINDOW = 5       # secondes
SYNFLOOD_SYN_THRESHOLD = 20    # nombre de SYN avant alerte

# --- ICMP Scan ---
ICMP_TIME_WINDOW = 10          # secondes
ICMP_THRESHOLD = 5             # nombre de paquets ICMP avant alerte

# --- Ports interdits ---
FORBIDDEN_PORTS = [22, 23, 3389]  # SSH, Telnet, RDP par exemple