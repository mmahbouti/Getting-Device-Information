import csv
import concurrent.futures
from netmiko import ConnectHandler
import re
from getpass import getpass

def connect_and_get_info(ip,ping_result, port_22_scan, port_23_scan,port_80_scan,port_443_scan,error_connection_file,username,password):
    # Define device_type based on open port
    if port_22_scan == "open":
        device_type = "terminal_server"
    elif port_23_scan == "open":
        device_type = "cisco_ios_telnet"
        #print(ip,device_type)
    else:
        device_type = None  # Not supported
    
    if device_type:
        
        try:
            # Establish SSH or Telnet connection
            connection = ConnectHandler(
                device_type=device_type,
                ip=ip,
                username=username,
                password=password
            )
            #if device_type == 'cisco_ios_telnet':
                #print(ip,connection.send_command_timing("show version"))
            # Determine device brand based on 'show version' output
            #connection.enable()
            show_version_output = connection.send_command_timing("show version")
            #print(ip,show_version_output)
            if 'Command fail. Return code' in show_version_output:
                device_brand = "fortigate"
                #print(show_version_output)
            elif "ios-xe" in show_version_output.lower():
                device_brand = "ios-xe"
            elif "nx-os" in show_version_output.lower():
                device_brand = "nx-os"
            elif "asa" in show_version_output.lower():
                device_brand = "asa"
            elif "ios" in show_version_output.lower():
                device_brand = "ios"
            else:
                device_brand = "unknown"
            #print(device_type)
            # Get the hostname
            if device_brand == "fortigate":
                hostname_output = connection.send_command("get system status | grep -fi hostname")
                hostname = hostname_output
                hostname = hostname.split(" ")[1]

                version_output = connection.send_command("get system status | grep -fi version")
                version_output = version_output.split("\n")[0]
                model = version_output.split(" ")[1]
                
                serial_output = connection.send_command("get system status | grep -fi serial")
                serial = serial_output.split(" ")[1]
                
                version = version_output.split(" ")[2]

            elif device_brand == "nx-os":
                connection = ConnectHandler(device_type="cisco_nxos",ip=ip,username=username,password=password)
                #connection.enable()
                show_version_dict = connection.send_command_timing("show version", use_textfsm=True)
                if show_version_dict and isinstance(show_version_dict, list) and len(show_version_dict) > 0:
                    hostname = show_version_dict[0].get("hostname", "N/A")
                    model = show_version_dict[0].get("platform", "N/A")
                    serial = show_version_dict[0].get("serial", "N/A")
                    version = show_version_dict[0].get("boot_image", "N/A")
                    
            elif device_brand == "asa":
                connection = ConnectHandler(device_type="cisco_asa",ip=ip,username=username,password=password)
                #connection.enable()
                show_version_dict = connection.send_command_timing("show version", use_textfsm=True)
                if show_version_dict and isinstance(show_version_dict, list) and len(show_version_dict) > 0:
                    hostname = show_version_dict[0].get("hostname", "N/A")
                    model = "N/A"
                    serial = "N/A"
                    version = "N/A"

            elif device_brand == "ios" or device_brand =="ios-xe":
                if device_type =="cisco_ios_telnet":
                    connection = ConnectHandler(device_type="cisco_ios_telnet",ip=ip,username=username,password=password)
                else:
                    connection = ConnectHandler(device_type="cisco_ios",ip=ip,username=username,password=password)
                
                show_version_dict = connection.send_command_timing("show version", use_textfsm=True)
                if show_version_dict and isinstance(show_version_dict, list) and len(show_version_dict) > 0:
                    hostname = show_version_dict[0].get("hostname", "N/A")
                    model = str(show_version_dict[0].get("hardware", "N/A"))
                    serial = str(show_version_dict[0].get("serial", "N/A"))

                    version = show_version_dict[0].get("version", "N/A")
                    software_image = show_version_dict[0].get("software_image", "N/A")
                    version = version + "-" + software_image
            else:
                hostname = "N/A"
                model = "N/A"
                serial = "N/A"
                version = "N/A"
            # Close the connection
            connection.disconnect()
            print (ip,ping_result, port_22_scan, port_23_scan,port_80_scan,port_443_scan,hostname,model,serial,version)
            return {
                "ip": ip,
                "port 22 scan": port_22_scan,
                "ping_result" : ping_result,
                "port 23 scan": port_23_scan,
                "port 80 scan": port_80_scan,
                "port 443 scan": port_443_scan,
                "device_brand": device_brand,
                "hostname": hostname,
                "model": model,
                "serial": serial,
                "version": version
            }
        except Exception as e:
            # Handle connection errors or authentication failures
            with open(error_connection_file, "a") as error_file:
                error_file.write(f"Error connecting to {ip}: {str(e)}\n")

    return None

def main():
    #input_file = "port_scan_results_TDC_OOB.csv"
    input_file = input("Please Enter input csv file name:")
    if not input_file.endswith(".csv"):
        input_file += ".csv"
	
    output_file = input("Please Enter output csv file name:")
    if not output_file.endswith(".csv"):
        output_file += ".csv"
	
    error_connection_file = input("Please Enter error connection text file name:")
    if not error_connection_file.endswith(".txt"):
        error_connection_file += ".txt"
	
    #output_file = "device_info_results_TDC_OOB.csv"
    username = input("Please Enter Your Username:")
    password = getpass("Please Enter Your Password:")
	
    with open(input_file, "r") as input_csv, open(output_file, "w", newline="") as output_csv:
        input_reader = csv.DictReader(input_csv)
        headers = input_reader.fieldnames
        headers.extend(["device_brand", "hostname","model","serial","version"])
        
        output_writer = csv.DictWriter(output_csv, fieldnames=headers)
        output_writer.writeheader()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for row in input_reader:
                ip = row["ip"]
                ping_result = row["ping_result"]
                port_22_scan = row["port 22 scan"]
                port_23_scan = row["port 23 scan"]
                port_80_scan = row["port 80 scan"]
                port_443_scan = row["port 443 scan"]
                
                future = executor.submit(connect_and_get_info, ip, ping_result, port_22_scan, port_23_scan,port_80_scan,port_443_scan,error_connection_file,username,password)
                futures.append(future)
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    output_writer.writerow(result)

if __name__ == "__main__":
    main()
