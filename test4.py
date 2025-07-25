import sys
import dns.resolver
import requests

# Colors for pretty output 
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

#  Common fingerprints for takeover 
FINGERPRINTS = {
    "github.io": "There isn't a GitHub Pages site here.",
    "herokuapp.com": "No such app",
    "amazonaws.com": "NoSuchBucket",
    "netlify.app": "Not Found",
    "readthedocs.io": "Unknown Domain",
    "pantheonsite.io": "The gods are wise",
    "azurewebsites.net": "404 Web Site not found",
}

def load_subdomains(filename):
    subs = []
    try:
        with open(filename, "r") as f:
            for line in f:
                s = line.strip()
                if s:
                    subs.append(s)
    except FileNotFoundError:
        print(f"{color.RED}[!] File not found: {filename}{color.END}")
        sys.exit(1)
    return subs

def check_takeover(subdomain):
    try:
        answers = dns.resolver.resolve(subdomain, "CNAME", lifetime=5)
        cname = str(answers[0].target).strip(".")
        # Only now test fingerprints for known services
        for key, sig in FINGERPRINTS.items():
            if key in cname:
                try:
                    r = requests.get(f"http://{subdomain}", timeout=8)
                    if sig.lower() in r.text.lower():
                        return f"[CNAME to {cname}] Possible takeover! Fingerprint: {key}"
                except requests.RequestException:
                    pass
        # If a CNAME exists but no known fingerprint is matched:
        return None
    except dns.resolver.NoAnswer:
        # No CNAME; not necessarily a takeover, skip
        return None
    except dns.resolver.NXDOMAIN:
        # NXDOMAIN might indicate dangling DNS
        return "[NXDOMAIN] No DNS record; investigate manually"
    except Exception:
        return None

def main():
    if len(sys.argv) != 2:
        print(f"{color.RED}Usage:{color.END} python3 test4.py <subdomain_file>")
        sys.exit(1)

    filename = sys.argv[1]
    subdomains = load_subdomains(filename)

    separator("SUBDOMAIN TAKEOVER CHECK")
    vulnerable = []

    for sub in subdomains:
        result = check_takeover(sub)
        if result:
            print(f"{color.YELLOW}[!] {sub}: {result}{color.END}")
            vulnerable.append((sub, result))

    if not vulnerable:
        print(f"{color.GREEN}[✔] No obvious takeover candidates found.{color.END}")
    else:
        print(f"\n{color.RED}[!] {len(vulnerable)} Potential takeover(s) detected!{color.END}")
        for sub, reason in vulnerable:
            print(f" - {sub}: {reason}")

if __name__ == "__main__":
    main()
