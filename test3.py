import sys
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===== Colors =====
class color:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    HEADER = '\033[95m'
    BOLD = '\033[1m'

def separator(title):
    print(f"\n{color.HEADER}{'='*20} {title} {'='*20}{color.END}")

def load_wordlist(path):
    if path.startswith("~/"):
        path = os.path.expanduser(path)
    if not os.path.isfile(path):
        print(f"{color.RED}[!] Wordlist file not found: {path}{color.END}")
        sys.exit(1)
    with open(path, "r") as f:
        words = [line.strip() for line in f if line.strip()]
    return words

def check_param(base_url, param):
    try:
        url = f"{base_url}?{param}=test"
        r = requests.get(url, timeout=3, allow_redirects=False)
        # treat 200, 301, 302 as valid
        if r.status_code in [200, 301, 302]:
            return param
    except:
        return None
    return None

def main():
    if len(sys.argv) != 2:
        print(f"{color.RED}Usage:{color.END} python3 test3.py <target_url>")
        sys.exit(1)

    base_url = sys.argv[1]
    if not base_url.startswith("http://") and not base_url.startswith("https://"):
        base_url = "https://" + base_url

    wordlist_path = input("Enter path to parameter wordlist [~/SecLists/Discovery/Web-Content/common.txt]: ").strip()
    if wordlist_path == "":
        wordlist_path = "~/SecLists/Discovery/Web-Content/common.txt"

    print(f"\n[*] Loading wordlist from: {wordlist_path}")
    words = load_wordlist(wordlist_path)
    print(f"[*] Loaded {len(words)} words")

    separator("PARAMETER DISCOVERY")

    found = []
    # 🏎️ Use ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=30) as executor:  # tweak max_workers for speed
        futures = {executor.submit(check_param, base_url, w): w for w in words}
        for future in as_completed(futures):
            result = future.result()
            if result:
                found.append(result)
                print(f"{color.GREEN}[+] Possible param: {result}{color.END}")

    if not found:
        print(f"{color.YELLOW}[-] No possible parameters found.{color.END}")
    else:
        print(f"\n{color.BOLD}{color.GREEN}[✔] Found {len(found)} possible parameters!{color.END}")

if __name__ == "__main__":
    main()
