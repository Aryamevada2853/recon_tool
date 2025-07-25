import subprocess
import sys
import os

def separator(title):
    print(f"\n{'='*20} {title} {'='*20}")

def check_tool_installed(tool):
    """Check if a tool like subfinder/httpx is installed."""
    from shutil import which
    return which(tool) is not None


def run_subfinder(domain, outfile="subfinder_subs.txt"):
    print(f"[*] Running subfinder on {domain} ...")
    cmd = ["subfinder", "-d", domain, "-o", outfile, "-silent"]
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print("[!] subfinder not found. Install it from ProjectDiscovery.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"[!] subfinder failed: {e}")
        sys.exit(1)

    if not os.path.exists(outfile):
        print("[!] Subfinder output file not found.")
        sys.exit(1)
    return outfile


def read_subs(filename):
    subs = set()
    with open(filename, "r") as f:
        for line in f:
            sub = line.strip()
            if sub:
                subs.add(sub)
    return sorted(subs)


def verify_with_httpx(subdomains):
    print("[*] Verifying subdomains with httpx ...")
    if not check_tool_installed("httpx"):
        print("[!] httpx not installed. Install it with: go install github.com/projectdiscovery/httpx/cmd/httpx@latest")
        return []

    temp_file = "temp_subs.txt"
    with open(temp_file, "w") as f:
        for sub in subdomains:
            f.write(sub + "\n")

    try:
        cmd = ["httpx", "-silent", "-l", temp_file]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        alive = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)  # cleanup temp file

    return sorted(set(alive))

# Main 
def main(domain):
    # Run subfinder
    output_file = run_subfinder(domain)

    # Read unique subdomains
    subs = read_subs(output_file)
    separator("UNIQUE SUBDOMAINS")
    for s in subs:
        print(s)

    # Verify with httpx
    alive = verify_with_httpx(subs)
    separator("ACTIVE SUBDOMAINS")
    for a in alive:
        print(a)

# entry
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 test2.py <domain>")
        sys.exit(1)

    domain = sys.argv[1].strip()
    main(domain)
