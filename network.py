import socket
import subprocess
import platform
import dns.resolver


def ping_host(host):
    """
    Ping a host and return result.
    Works on both Windows and Linux/Mac.
    """
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "4", host]
    try:
        output = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10
        )
        if output.returncode == 0:
            return True, output.stdout
        else:
            return False, output.stdout or output.stderr
    except subprocess.TimeoutExpired:
        return False, "Ping timed out after 10 seconds."
    except Exception as e:
        return False, str(e)


def scan_ports(host, ports):
    """
    Scan a list of ports on a given host.
    Returns dict of port -> 'Open' or 'Closed'
    """
    results = {}
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            if result == 0:
                results[port] = "Open"
            else:
                results[port] = "Closed"
            sock.close()
        except socket.gaierror:
            results[port] = "Host unreachable"
        except Exception as e:
            results[port] = f"Error: {str(e)}"
    return results


def dns_lookup(domain):
    """
    Perform DNS lookup for a domain.
    Returns IP address and DNS records.
    """
    results = {}
    try:
        # Basic IP resolution
        ip = socket.gethostbyname(domain)
        results["IP Address"] = ip

        # A records
        try:
            a_records = dns.resolver.resolve(domain, "A")
            results["A Records"] = [str(r) for r in a_records]
        except Exception:
            results["A Records"] = ["Not found"]

        # MX records
        try:
            mx_records = dns.resolver.resolve(domain, "MX")
            results["MX Records"] = [str(r.exchange) for r in mx_records]
        except Exception:
            results["MX Records"] = ["Not found"]

        # TXT records
        try:
            txt_records = dns.resolver.resolve(domain, "TXT")
            results["TXT Records"] = [str(r) for r in txt_records]
        except Exception:
            results["TXT Records"] = ["Not found"]

    except socket.gaierror as e:
        results["Error"] = f"Could not resolve domain: {str(e)}"
    except Exception as e:
        results["Error"] = str(e)

    return results


# Common ports reference
COMMON_PORTS = {
    21:   "FTP",
    22:   "SSH",
    23:   "Telnet",
    25:   "SMTP",
    53:   "DNS",
    80:   "HTTP",
    110:  "POP3",
    143:  "IMAP",
    443:  "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    8080: "HTTP Alt",
    8443: "HTTPS Alt",
}

# IT Support Toolkit - 2nd Line Network Diagnostic Tool
# Author: Anudeep Burra | Built with Python socket and dnspython