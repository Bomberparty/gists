import socket
import ipaddress
from multiprocessing import Pool

def check_ssh(ip):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((ip, 22))
            if result == 0:
                return ip
    except:
        pass
    return None

if __name__ == '__main__':
    network = ipaddress.IPv4Network('192.168.137.1/24', strict=False)
    ips = [str(host) for host in network.hosts()]
    
    with Pool(processes=10) as pool:
        results = pool.map(check_ssh, ips)
    
    successful_ips = [ip for ip in results if ip is not None]
    print("IP addresses with SSH port open:")
    for ip in successful_ips:
        print(ip)