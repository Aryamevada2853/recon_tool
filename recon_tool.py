import subprocess
import sys
import os

# ===== Colors =====
class color:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def banner():
    print(f"{color.BOLD}{color.HEADER}")
    print("=======================================")
    print('''         
██████╗░███████╗░█████╗░░█████╗░███╗░░██╗██╗███╗░░██╗░█████╗░████████╗░█████╗░██████╗░
██╔══██╗██╔════╝██╔══██╗██╔══██╗████╗░██║██║████╗░██║██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗
██████╔╝█████╗░░██║░░╚═╝██║░░██║██╔██╗██║██║██╔██╗██║███████║░░░██║░░░██║░░██║██████╔╝
██╔══██╗██╔══╝░░██║░░██╗██║░░██║██║╚████║██║██║╚████║██╔══██║░░░██║░░░██║░░██║██╔══██╗
██║░░██║███████╗╚█████╔╝╚█████╔╝██║░╚███║██║██║░╚███║██║░░██║░░░██║░░░╚█████╔╝██║░░██║
╚═╝░░╚═╝╚══════╝░╚════╝░░╚════╝░╚═╝░░╚══╝╚═╝╚═╝░░╚══╝╚═╝░░╚═╝░░░╚═╝░░░░╚════╝░╚═╝░░╚═╝       
''')
    print("=======================================")
    print(f"{color.END}")

def menu():
    print(f"{color.GREEN}[1]{color.END} Run Passive Recon (test1.py)")
    print(f"{color.GREEN}[2]{color.END} Run Subdomain Enum (test2.py)")
    print(f"{color.GREEN}[3]{color.END} Run Parameter Discovery (test3.py)")
    print(f"{color.GREEN}[4]{color.END} Run Subdomain Takeover checker (test4.py)")
    print(f"{color.GREEN}[0]{color.END} Exit")

def main():
    banner()
    while True:
        menu()
        choice = input(f"\n{color.YELLOW}Enter your choice: {color.END}").strip()

        if choice == "1":
            target = input(f"{color.BLUE}Enter target domain (e.g., example.com): {color.END}").strip()
            subprocess.run([sys.executable, "test1.py", target])

        elif choice == "2":
            target = input(f"{color.BLUE}Enter target domain (e.g., example.com): {color.END}").strip()
            subprocess.run([sys.executable, "test2.py", target])

        elif choice == "3":
            target = input(f"{color.BLUE}Enter target URL (e.g., https://example.com): {color.END}").strip()
            subprocess.run([sys.executable, "test3.py", target])

        elif choice == "4":
            target = input(f"{color.BLUE}Enter target for module 4(subfinder_subs.txt, add this): {color.END}").strip()
            subprocess.run([sys.executable, "test4.py", target])

        elif choice == "0":
            print(f"{color.BOLD}{color.GREEN}[✔] Exiting Recon Tool. Goodbye!{color.END}")
            break

        else:
            print(f"{color.RED}[!] Invalid choice, please try again.{color.END}")

if __name__ == "__main__":
    main()
