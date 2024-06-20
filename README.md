# 01.Port-Scan.py
This code executes ping and port scans on individual or multiple IP ranges and port numbers.
You must enter the IP address with a prefix and you can use (",") for multiple IP ranges for example 10.20.0.0/25,46.224.0.0/17
Also, you can use multiple ports for scanning and you have to use (",") for various ports for example 22,23,80,53
Finally, you must enter the CSV output file name and this file shows scanning output.

Input:

![port-scan-input](https://github.com/mmahbouti/Getting-Device-Information/assets/96656121/3855a374-e48b-4c87-8649-018eacda4fc6)


Output:

![port-scan-output](https://github.com/mmahbouti/Getting-Device-Information/assets/96656121/2dfb0e59-4af5-444c-81b3-7000273dd483)

# 02.getting_device_info.py
This code executes the output of 01.port_scan.py and gets information(such as device brand, hostname, model, serial number, and version)about the IPs on this file. If you have another input file, you can use your input.
This code can execute on the IOS, IOS-XE, NX-OS, ASA, and FortiGate devices.
If you use ports 22, 23, 80, and 443 on 01.port_scan.py, you don't need to modify this code and you can use this code easily.


Input:

![device-info-input](https://github.com/mmahbouti/Getting-Device-Information/assets/96656121/fdbe9045-7f04-427b-832a-683fd983fa29)


Output:

![device-info-output](https://github.com/mmahbouti/Getting-Device-Information/assets/96656121/817c11a3-dd8c-40d1-a835-953e672278a3)

