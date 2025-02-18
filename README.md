# Port Scanner

## Overview
This Python-based port scanner allows users to check the availability of hosts, retrieve host information, and scan ports in a multithreaded fashion for efficiency. The tool reads from a file containing a list of IP addresses, checks their status, and identifies open ports in a given range. The results are saved in JSON format for easy reference.

## Features
- Check if a host is online via ICMP ping.
- Retrieve hostname and alias information using reverse DNS lookup.
- Scan a range of ports efficiently using multithreading.
- Read a list of hosts from a file and scan them automatically.
- Save results in a JSON file.

## Prerequisites
Ensure you have the following installed on your system:
- Python 3.6+

## Installation
Clone this repository:
```sh
 git clone https://github.com/jasoncallen/PortScanner.git
 cd PortScanner
```

## Usage
1. Prepare a file containing a list of IP addresses, one per line.
2. Run the script:
```sh
 python PortScanner.py
```
3. Follow the prompts to provide:
   - The file containing IP addresses.
   - The start and end ports for scanning.
   - The number of threads for scanning (default: 100).
   - The output filename (in JSON format).

## Example Output
A sample JSON output file may look like:
```json
{
    "192.168.1.1": {
        "State": "Online",
        "Hostname": "router.local",
        "Alias": [],
        "Open Ports": [22, 80, 443]
    },
    "192.168.1.2": {
        "State": "Offline",
        "Hostname": "Unknown",
        "Alias": [],
        "Open Ports": []
    }
}
```

## Functions Explained
- `is_host_online(host)`: Checks if a host is reachable via ICMP ping.
- `get_host_info(host)`: Retrieves the hostname and alias information of a given IP.
- `port_scanner(host, start_port, end_port, num_threads)`: Scans a range of ports using multiple threads.
- `scan_from_file(host_list, start_port, end_port, num_threads, output_filename)`: Reads hosts from a file and scans each one.
- `check_file()`: Ensures the input file exists and extracts valid IP addresses.
- `TCP_port_check()`: Prompts user for start and end ports, validating inputs.
- `get_threads_count()`: Allows users to specify the number of scanning threads.

## Notes
- Requires administrator/root privileges to run on some systems due to ICMP ping restrictions.
- The script suppresses ping output for cleaner execution.
- Designed for efficiency but may require adjustments based on network conditions.

## License
This project is licensed under the GNU V2.0 License.
