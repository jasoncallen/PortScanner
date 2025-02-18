import socket
import threading
import json
import subprocess
from queue import Queue
import ipaddress
import platform


def is_host_online(host) -> bool:
    """
    Checks if a given host is online by sending a single ping request.

    The function executes a system ping command to determine the reachability of the host.
    It suppresses output and error messages for cleaner execution.
    If the ping command succeeds (return code 0), the host is considered online.
    If the command fails or an exception occurs, the function returns False.

    Args:
        host (str): The IP address or hostname to check.

    Returns:
        bool: True if the host responds to the ping request, False otherwise.
    """
    try:
        if platform.system() == "Windows":
            response = subprocess.run(["ping", "-n", "1", host], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            response = subprocess.run(["ping", "-c", "1", host], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return response.returncode == 0
    except Exception:
        return False

def get_host_info(host) -> tuple[str, list]:
    """
    Retrieves the hostname and alias information for a given IP address or hostname.

    The function attempts to resolve the provided host using a reverse DNS lookup.
    If the lookup is successful, it returns the resolved hostname and alias list.
    If the lookup fails due to an error (e.g., host not found), it returns `"Unknown"`
    as the hostname and an empty list for aliases.

    Args:
        host (str): The IP address or hostname to look up.

    Returns:
        tuple[str, list]: A tuple containing:
            - The resolved hostname (or "Unknown" if resolution fails).
            - A list of alias names associated with the host (empty if none exist).
    """
    try:
        hostname,alias,_ = socket.gethostbyaddr(host)
    except (socket.herror, socket.gaierror):
        hostname, alias = "Unknown", []
    return hostname, alias

def scan_port(host, port, output_queue) -> None:
    """Attempts to connect to a port on the given host."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(.5)
        if sock.connect_ex((host, port)) == 0:
            output_queue.put(port)

def worker(host, queue, output_queue) -> None:
    """Worker function to process ports from the queue."""
    while not queue.empty():
        port = queue.get()
        scan_port(host, port, output_queue)
        queue.task_done()

def port_scanner(host, start_port, end_port, num_threads) -> list[int]:
    """
    Scans a specified range of ports on a given host using multithreading.

    The function creates worker threads to efficiently scan the specified range of ports,
    checking if they are open. It uses a queue system to distribute scanning tasks among 
    multiple threads for faster execution.

    Args:
        host (str): The target IP address or hostname to scan.
        start_port (int): The starting port number for the scan.
        end_port (int): The ending port number for the scan.
        num_threads (int): The number of worker threads to use for scanning. 

    Returns:
        list[int]: A list of open ports discovered on the target host.
    """
    port_queue = Queue()
    output_queue = Queue()
    
    for port in range(start_port, end_port + 1):
        port_queue.put(port)
    
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=worker, args=(host, port_queue, output_queue))
        thread.daemon = True  # Daemon threads will exit when the main program exits
        thread.start()
        threads.append(thread)
    
    port_queue.join()
    
    open_ports = []
    while not output_queue.empty():
        open_ports.append(output_queue.get())
    
    return open_ports

def scan_from_file(host_list, start_port, end_port, num_threads, output_filename) -> None:
    """
    Reads a file containing a list of IP addresses, scans each for open ports, and saves the results.

    The function performs the following steps:
    - Reads the IP addresses from the specified host list.
    - Checks if each host is online.
    - Retrieves hostname and alias information for each host.
    - If the host is online, scans for open ports within the given range using multithreading.
    - Stores the scan results, including host state, hostname, alias, and open ports.
    - Saves the results as a JSON file.

    Args:
        host_list (list): list containing IP addresses to scan.
        start_port (int): The starting port number for scanning.
        end_port (int): The ending port number for scanning.
        num_threads (int): The number of threads to use for scanning.
        output_filename (str): Path to the output JSON file where results will be saved.

    Returns:
        None: The results are written to the specified output file.
    """
        
    results = {}
    for host in host_list:

        print(f"Scanning {host}...")
        state = "Online" if is_host_online(host) else "Offline"
        hostname, alias = get_host_info(host)
        open_ports = []
        
        if state == "Online":
            open_ports = port_scanner(host, start_port, end_port, num_threads)
        
        results[host] = {
            "State": state,
            "Hostname": hostname,
            "Alias": alias,
            "Open Ports": open_ports
        }
    
    try:
        with open(output_filename, 'w') as outfile:
            json.dump(results, outfile, indent=4)
            print(f"Scan results saved to {output_filename}")
    except IOError as e:
        print(f"Error writing output file: {e}")

def check_file() -> list:
    """
    Prompts the user to enter the path to a file containing IP addresses and validates its existence.

    The function performs the following operations:
    - Ensures the specified file exists before proceeding.
    - Reads and processes the file line by line.
    - Validates each line to check if it is a valid IP address.
    - Removes duplicate and invalid IP addresses from the final list.

    Returns:
        list[str]: A list of unique, valid IP addresses extracted from the file.
    """
    return_list = []
    while True:
        input_file = input("Enter the path to the file containing IP addresses: ")
        try:
            
            try_file = open(input_file)
            try_file.close()
            break
        except FileNotFoundError:
            print(f"File {input_file} was not found! Please try again.")
        except Exception as e:
            # Handle the exception
            print("An error occurred:", e)

    with open(input_file) as working_file:
        for line in working_file:
            line =line.strip()
            # print(line)
            try:
                ip = ipaddress.ip_address(line)
                if line not in return_list:
                    return_list.append(line)
            except ValueError:
                pass

    return return_list
            
def TCP_port_check() -> tuple[int,int]:
    """
    Prompts the user to input a valid start and end TCP port range.

    The function ensures that:
    - The start port is between 1 and 65000 (inclusive).
    - The end port is between the specified start port and 65000 (inclusive).
    - Invalid inputs trigger appropriate error messages, prompting the user to re-enter values.

    Returns:
        tuple[int, int]: A tuple containing the validated start and end TCP ports.
    """
    while True:
        try:
            start_port = int(input("Enter the start TCP port: "))
            if start_port >= 1 and start_port <= 65000:
                break
            raise ValueError
        except ValueError:
            print(f"Entry is invalid! Please enter a number from 1 to 65000.")
        except Exception as e:
            print(e)

    while True:
        try:
            end_port = int(input("Enter the end TCP port: "))
            if end_port >= start_port and end_port <= 65000:
                break
            raise ValueError
        except ValueError:
            print(f"Entry is invalid! Please enter a number from {start_port} to 65000.")
        except Exception as e:
            print(e)
    
    return start_port,end_port

def get_threads_count() -> int:
    """
    Prompts the user to input the number of threads to use.
    
    - If the user presses Enter without entering a value, a default of 100 is returned.
    - Ensures that the user provides a valid integer input.
    - If an invalid entry is detected, an error message is displayed,
      and the user is prompted to enter the value again.

    Returns:
        int: The validated number of threads specified by the user, or the default value of 100.
    """
    default_threads = 100
    while True:
        try:
            threads = input(f"Enter the number of threads to use (default {default_threads}): ").strip()
            if threads == "":
                return default_threads
            threads = int(threads)
            return threads
        except ValueError:
            print("Invalid entry! Please enter a valid number or press Enter to use the default.")
        except Exception as e:
            print(e)

if __name__ == "__main__":
    host_list = check_file()
    start_port,end_port = TCP_port_check()
    threads = get_threads_count()
    output_file = input("Enter the output filename (JSON format): ")
    
    scan_from_file(host_list, start_port, end_port, threads, output_file)
