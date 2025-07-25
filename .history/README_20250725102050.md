🔎 Recon Tool

A Python-based recon toolkit for bug bounty hunters and pentesters.✨ Features

1. Passive Recon (test1.py)
- WHOIS lookup
- DNS records
- crt.sh certificate search
- Wayback Machine URL collection
- Google Dork suggestions
- Host reachability
- Port scan (common ports)
- Banner grabbing
- Tech stack from headers
- CORS testing
- Cloud bucket enumeration

2. Active Recon (test2.py)
- Subdomain enumeration using Subfinder
- Automatic filtering of unique subdomains
- HTTPX integration to find live (active) subdomains

3. Parameter Discovery (test3.py)
- Fuzzing for common parameters using a wordlist

📦 Installation

```bash
git clone https://github.com/Aryamevada2853/recon_tool.git
cd recon_tool
pip install -r requirements.txt
