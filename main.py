import socket
import os
import struct
import time

ICMP_ECHO_REQUEST = 8  

def checksum(source_string):
    countTo = (len(source_string) // 2) * 2
    sum = 0
    for i in range(0, countTo, 2):
        sum += source_string[i] + (source_string[i + 1] << 8)
    if countTo < len(source_string):
        sum += source_string[-1]
    sum = (sum >> 16) + (sum & 0xffff)
    sum += (sum >> 16)
    return ~sum & 0xffff

def create_packet(id):
    """Create an ICMP echo request packet."""
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, 0, id, 1)
    checksum_value = checksum(header)
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, socket.htons(checksum_value), id, 1)
    return header

def traceroute(target, max_hops=30, packets_per_hop=3):
    print(f"Трассировка до {target}:")
    target_ip = socket.gethostbyname(target)

    for ttl in range(1, max_hops + 1):
        for seq in range(packets_per_hop):
            with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as sock:
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
                packet_id = os.getpid() & 0xFFFF
                packet = create_packet(packet_id)
                sock.sendto(packet, (target_ip, 1))
                start_time = time.time()

                try:
                    reply, addr = sock.recvfrom(1024)
                    round_trip_time = (time.time() - start_time) * 1000  
                    print(f"{ttl}\t{round_trip_time:.2f}ms\t{addr[0]}")
                except socket.timeout:
                    print(f"{ttl}\t*\t*")

                if reply[20] == 3:  
                    print("Достигнут конечный узел.")
                    return

        time.sleep(1)

if __name__ == "__main__":
    target = input("Введите IP-адрес или доменное имя: ")
    traceroute(target)