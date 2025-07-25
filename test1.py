import sys
import socket
import requests
import whois
import dns.resolver
import json
import threading
from queue import Queue
from datetime import datetime
from urllib.parse import urlparse

# ====== Colors ======
class color:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def separator(title):
    print(f"\n{color.HEADER}{'='*20} {title} {'='*20}{color.END}")

# ==========================
# PASSIVE RECON MODULES
# ==========================

def get_whois(domain):
    separator("WHOIS INFO")
    try:
        w = whois.whois(domain)
        print(f"{color.BOLD}Domain Name:{color.END} {w.domain_name}")
        print(f"{color.BOLD}Registrar:{color.END} {w.registrar}")
        print(f"{color.BOLD}Name Servers:{color.END} {', '.join(w.name_servers) if w.name_servers else 'N/A'}")
        print(f"{color.BOLD}Creation Date:{color.END} {w.creation_date}")
        print(f"{color.BOLD}Expiration Date:{color.END} {w.expiration_date}")
        if w.emails:
            print(f"{color.BOLD}Emails:{color.END} {w.emails}")
        if w.org:
            print(f"{color.BOLD}Org:{color.END} {w.org}")
    except Exception as e:
        print(f"{color.RED}[!] WHOIS failed:{color.END} {e}")

def get_dns_records(domain):
    separator("DNS RECORDS")
    record_types = ["A", "MX", "NS", "TXT"]
    for rtype in record_types:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            for rdata in answers:
                print(f"{color.GREEN}{rtype}:{color.END} {rdata}")
        except Exception as e:
            # Could be no records or query failed
            print(f"{color.YELLOW}[-] No {rtype} record found or query failed.{color.END}")

def get_crtsh_subdomains(domain):
    separator("CRT.SH SUBDOMAINS")
    try:
        url = f"https://crt.sh/?q=%25.{domain}&output=json"
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            entries = json.loads(r.text)
            subdomains = set()
            for entry in entries:
                name_value = entry.get('name_value', '')
                for sub in name_value.split('\n'):
                    if domain in sub:
                        subdomains.add(sub.strip())
            for s in sorted(subdomains):
                print(f"{color.BLUE}• {s}{color.END}")
        else:
            print(f"{color.RED}[!] crt.sh returned {r.status_code}{color.END}")
    except Exception as e:
        print(f"{color.RED}[!] crt.sh lookup failed:{color.END} {e}")

def get_wayback_urls(domain):
    separator("WAYBACK MACHINE URLS (Top 50)")
    try:
        url = f"http://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&collapse=urlkey"
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            data = r.json()
            urls = [row[2] for row in data[1:]]  # skip header row
            for u in urls[:50]:
                print(f"{color.YELLOW}- {u}{color.END}")
        else:
            print(f"{color.RED}[!] Wayback response {r.status_code}{color.END}")
    except Exception as e:
        print(f"{color.RED}[!] Wayback failed:{color.END} {e}")

def print_google_dorks(domain):
    separator("GOOGLE DORKS")
    dorks = [
        f"site:{domain}",
        f"site:{domain} ext:php | ext:aspx | ext:jsp",
        f"site:{domain} inurl:admin",
        f"site:{domain} intitle:index.of",
        f"site:{domain} \"password\"",
    ]
    for d in dorks:
        print(f"{color.BLUE}→ {d}{color.END}")

# ==========================
# ACTIVE RECON MODULES
# ==========================

def check_host(target):
    separator("HOST REACHABILITY")
    try:
        ip = socket.gethostbyname(target)
        print(f"{color.BOLD}Resolved IP:{color.END} {ip}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((ip, 80))
        if result == 0:
            print(f"{color.GREEN}[+] Host is reachable on port 80 (HTTP){color.END}")
        else:
            print(f"{color.RED}[-] Host not reachable on port 80{color.END}")
        sock.close()
    except Exception as e:
        print(f"{color.RED}[!] Host check failed:{color.END} {e}")

common_ports = {
    21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS', 80: 'HTTP',
    110: 'POP3', 143: 'IMAP', 443: 'HTTPS', 3306: 'MySQL', 3389: 'RDP'
}

open_ports = []

def port_scan_worker(target, q):
    while not q.empty():
        port = q.get()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex((target, port))
            if result == 0:
                open_ports.append(port)
            s.close()
        except:
            pass
        q.task_done()

def scan_ports(target):
    separator("PORT SCAN (Common Ports)")
    q = Queue()
    for port in common_ports.keys():
        q.put(port)
    for _ in range(50):
        t = threading.Thread(target=port_scan_worker, args=(target, q))
        t.daemon = True
        t.start()
    q.join()
    if open_ports:
        for p in sorted(open_ports):
            service = common_ports.get(p, "Unknown")
            print(f"{color.GREEN}[+] Open Port {p}/{service}{color.END}")
    else:
        print(f"{color.RED}[-] No common ports open{color.END}")

def grab_banners(target):
    separator("BANNER GRABBING")
    for port in open_ports:
        try:
            s = socket.socket()
            s.settimeout(2)
            s.connect((target, port))
            s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
            banner = s.recv(1024).decode(errors='ignore').strip()
            print(f"{color.BLUE}Port {port}:{color.END}\n{banner}\n")
            s.close()
        except:
            pass

def detect_tech(target):
    separator("TECH STACK FROM HEADERS")
    try:
        resp = requests.get(f"http://{target}", timeout=5)
        server = resp.headers.get('Server', 'Unknown')
        powered_by = resp.headers.get('X-Powered-By', 'Unknown')
        print(f"{color.BOLD}Server:{color.END} {server}")
        print(f"{color.BOLD}X-Powered-By:{color.END} {powered_by}")
    except Exception as e:
        print(f"{color.RED}[!] Could not detect tech stack:{color.END} {e}")

# ==========================
# WEB APP TESTS MODULES
# ==========================

def cors_test(base_url):
    separator("CORS TESTING")
    try:
        headers = {"Origin": "https://evil.com"}
        r = requests.get(base_url, headers=headers, timeout=10)
        acao = r.headers.get("Access-Control-Allow-Origin", "")
        if "evil.com" in acao or "*" in acao:
            print(f"{color.YELLOW}[!] Potential CORS misconfig: {acao}{color.END}")
        else:
            print(f"{color.GREEN}[+] No obvious CORS misconfig{color.END}")
    except Exception as e:
        print(f"{color.RED}[!] CORS Test failed:{color.END} {e}")

def bucket_enum(domain):
    separator("CLOUD BUCKET ENUMERATION")
    patterns = [
        f"http://{domain}.s3.amazonaws.com",
        f"http://s3.amazonaws.com/{domain}",
        f"https://storage.googleapis.com/{domain}",
        f"https://{domain}.storage.googleapis.com",
    ]
    for url in patterns:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code in [200, 403]:
                print(f"{color.YELLOW}[!] Potential bucket: {url} ({r.status_code}){color.END}")
        except:
            pass

# ==========================
# MAIN FUNCTION
# ==========================

def main(target):
    # Extract domain from URL or raw input
    parsed = urlparse(target)
    domain = parsed.netloc or parsed.path
    base_url = f"{parsed.scheme}://{domain}" if parsed.scheme else f"http://{domain}"

    print(f"{color.BOLD}{color.HEADER}[*] Running Passive Recon on: {domain}{color.END}")
    get_whois(domain)
    get_dns_records(domain)
    get_crtsh_subdomains(domain)
    get_wayback_urls(domain)
    print_google_dorks(domain)

    print(f"{color.BOLD}{color.HEADER}[*] Running Active Recon on: {domain}{color.END}")
    check_host(domain)
    scan_ports(domain)
    grab_banners(domain)
    detect_tech(domain)

    print(f"{color.BOLD}{color.HEADER}[*] Running Web Tests on: {base_url}{color.END}")
    cors_test(base_url)
    bucket_enum(domain)

    print(f"\n{color.BOLD}{color.GREEN}[✔] Recon Completed Successfully{color.END}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"{color.RED}Usage:{color.END} python3 recon_all.py <target_domain_or_url>")
        sys.exit(1)
    target_input = sys.argv[1]
    main(target_input)
