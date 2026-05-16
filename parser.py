from scapy.all import rdpcap
import sqlite3
import os

def create_database():
    conn = sqlite3.connect("network_data.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS packets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time REAL,
            src_ip TEXT,
            dst_ip TEXT,
            protocol TEXT,
            size INTEGER
        )
    ''')
    conn.commit()
    conn.close()
    print("Database created successfully!")

def parse_pcap(file_path):
    print(f"Reading file: {file_path}")
    packets = rdpcap(file_path)
    
    conn = sqlite3.connect("network_data.db")
    cursor = conn.cursor()
    
    count = 0
    for packet in packets:
        try:
            time = float(packet.time)
            size = len(packet)
            src_ip = packet[1].src if packet.haslayer('IP') else "Unknown"
            dst_ip = packet[1].dst if packet.haslayer('IP') else "Unknown"
            
            if packet.haslayer('TCP'):
                protocol = "TCP"
            elif packet.haslayer('UDP'):
                protocol = "UDP"
            elif packet.haslayer('ICMP'):
                protocol = "ICMP"
            else:
                protocol = "Other"
            
            cursor.execute('''
                INSERT INTO packets (time, src_ip, dst_ip, protocol, size)
                VALUES (?, ?, ?, ?, ?)
            ''', (time, src_ip, dst_ip, protocol, size))
            count += 1
        except:
            pass
    
    conn.commit()
    conn.close()
    print(f"Done! {count} packets saved to database.")

if __name__ == "__main__":
    create_database()
    
    # We'll use your call.pcapng file!
    pcap_file = r"C:\Users\A\call.pcapng"
    
    if os.path.exists(pcap_file):
        parse_pcap(pcap_file)
    else:
        print(f"File not found: {pcap_file}")