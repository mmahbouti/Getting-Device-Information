import ipaddress
import ping3
import socket
from concurrent.futures import ThreadPoolExecutor
import csv

def ping_ip(ip):
    response = ping3.ping(ip, timeout=2)
    if response is not None and response is not False:
        return f"reachable"

    else:
        return f"unreachable"


def scan_port(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        sock.close()
        if result == 0:
            return "open"
        else:
            return "closed"
    except:
        return "error"

def main():
    input_ip_ranges = input("Please Enter your IP Ranges(Hint: You can Enter Multiple IP Ranges with Format 10.0.0.0/24,10.1.2.0/24):")
    input_ranges = input_ip_ranges.split(",")

    output_csv_file = input("Please Enter output csv file name:")
    if not output_csv_file.endswith(".csv"):
        output_csv_file += ".csv"

    input_port_ranges = input("Please Enter your Port Ranges(Hint: You can Enter Multiple Port Ranges with Format 22,23,80):")
    ports = [int(x) for x in input_port_ranges.split(",")]
    with ThreadPoolExecutor(max_workers=10) as executor, open(output_csv_file, "w", newline="") as csv_file:


        csv_writer = csv.writer(csv_file)
        header = ["ip", "ping_result"]
        for port in ports:
            header.append(f"port {port} scan")
        csv_writer.writerow(header)

        for ip_range in input_ranges:
            network = ipaddress.ip_network(ip_range, strict=False)
            for ip in network:
                ping_result = executor.submit(ping_ip, str(ip)).result()

                if "unreachable" not in ping_result:
                    port_scan_results = [executor.submit(scan_port, str(ip), port).result() for port in ports]
                else:
                    port_scan_results = ["N/A"] * len(ports)

                csv_row = [ip]
                csv_row.extend([ping_result])
                csv_row.extend(port_scan_results)
                csv_writer.writerow(csv_row)

if __name__ == "__main__":
    main()
