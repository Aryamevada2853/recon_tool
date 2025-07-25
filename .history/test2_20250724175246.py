import subprocess
import sys
import os

def run_subfinder(domain, outfile="subfinder_subs.txt"):
    print(f"[*] Running subfinder on {domain} ...")
    # Run subfinder
    cmd = ["subfinder", "-d", domain, "-o", outfile, "-silent"]
    subprocess.run(cmd)
    # Check if file created
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
    temp_file = "temp_subs.txt"
    with open(temp_file, "w") as f:
        for sub in subdomains:
            f.write(sub + "\n")
    cmd = ["httpx", "-silent", "-l", temp_file]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    alive = result.stdout.decode().splitlines()
    return sorted(set(alive))

def main(domain):
    # Step 1: Run subfinder
    output_file = run_subfinder(domain)

    # Step 2: Read unique subdomains
    subs = read_subs(output_file)
    print("\n==================== UNIQUE SUBDOMAINS ====================")
    for s in subs:
        print(s)

    # Step 3: Verify with httpx
    alive = verify_with_httpx(subs)
    print("\n==================== ACTIVE SUBDOMAINS ====================")
    for a in alive:
        print(a)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 subenum.py <domain>")
        sys.exit(1)

    domain = sys.argv[1].strip()
    main(domain)
