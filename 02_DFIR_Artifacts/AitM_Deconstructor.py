```python
#!/usr/bin/env python3
"""
AitM_Deconstructor.py
Forensic extraction and typosquatting analysis script for Tycoon 2FA .eml artifacts.
Author: GHOST BREACH Threat Labs | Aegis Logistics DFIR Simulation
Requires: pip install requests
"""

import email
from email import policy
from email.message import Message
import re
import os
import argparse
import logging
from urllib.parse import urlparse
import requests
from typing import List, Optional, Tuple

# Configure strict logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def calculate_levenshtein(s1: str, s2: str) -> int:
    """
    Calculates the Levenshtein distance between two strings using dynamic programming.
    This mathematical proof of typosquatting is preferred over basic difflib comparisons.
    """
    if len(s1) < len(s2):
        return calculate_levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def parse_eml(file_path: str) -> Optional[Message]:
    """Safely parses the raw .eml file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return email.message_from_file(f, policy=policy.default)
    except FileNotFoundError:
        logger.error(f"Artifact not found: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error parsing .eml: {e}")
        return None

def extract_urls(msg: Message) -> List[str]:
    """Extracts defanged and live URLs from the email body."""
    urls = set()
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type in ["text/plain", "text/html"]:
                try:
                    body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                except Exception as e:
                    logger.warning(f"Failed to decode part: {e}")
    else:
        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

    # Regex to catch both normal and defanged (hxxp/hxxps) URLs
    url_pattern = re.compile(r'(?:http|https|hxxp|hxxps)://[^\s<>"]+|www\.[^\s<>"]+')
    found_urls = url_pattern.findall(body)
    
    # Re-fang for analysis (internally only)
    for u in found_urls:
        clean_url = u.replace('hxxp', 'http').replace('[.]', '.')
        urls.add(clean_url)
        
    return list(urls)

def query_urlscan(url: str, api_key: str) -> None:
    """Queries URLScan.io for the extracted domain."""
    logger.info(f"Querying URLScan.io for: {url}")
    headers = {
        'API-Key': api_key,
        'Content-Type': 'application/json'
    }
    data = {"url": url, "visibility": "unlisted"}
    
    try:
        response = requests.post('https://urlscan.io/api/v1/scan/', headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            logger.info(f"[!] URLScan Submission Successful. Report UUID: {result.get('uuid')}")
            logger.info(f"[!] View result at: {result.get('result')}")
        else:
            logger.error(f"URLScan API Error: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        logger.error(f"Network error communicating with URLScan: {e}")

def main() -> None:
    parser = argparse.ArgumentParser(description="AitM .eml Deconstructor and Typosquatting Analyzer")
    parser.add_argument('-f', '--file', required=True, help="Path to the .eml forensic artifact")
    parser.add_argument('-d', '--domain', required=True, help="Legitimate corporate domain to check against")
    parser.add_argument('-s', '--scan', action='store_true', help="Execute URLScan.io API submission")
    args = parser.parse_args()

    logger.info(f"Initiating forensic parse of {args.file}...")
    msg = parse_eml(args.file)
    
    if not msg:
        return

    # 1. Header Analysis
    sender = msg.get('From', 'UNKNOWN')
    auth_results = msg.get('Authentication-Results', 'NONE')
    logger.info(f"Sender: {sender}")
    if "dkim=fail" in auth_results or "spf=softfail" in auth_results:
         logger.warning("Authentication Headers indicate SPF/DKIM failure. High likelihood of spoofing.")

    # 2. Payload Extraction
    extracted_urls = extract_urls(msg)
    if not extracted_urls:
        logger.warning("No URLs detected in payload.")
        return

    logger.info(f"Extracted {len(extracted_urls)} unique URLs.")
    
    # 3. Typosquatting Detection
    legit_domain = args.domain.lower()
    for url in extracted_urls:
        parsed_url = urlparse(url)
        # Strip subdomains for core domain comparison
        netloc_parts = parsed_url.netloc.split('.')
        core_domain = ".".join(netloc_parts[-2:]) if len(netloc_parts) > 1 else parsed_url.netloc
        
        distance = calculate_levenshtein(legit_domain, core_domain)
        
        logger.info(f"Analyzing Domain: {core_domain}")
        logger.info(f"Levenshtein Distance to {legit_domain}: {distance}")
        
        if 1 <= distance <= 3:
            logger.critical(f"TYPOSQUATTING DETECTED! '{core_domain}' is dangerously close to '{legit_domain}'.")

        # 4. API Integration
        if args.scan:
            api_key = os.getenv("URLSCAN_API_KEY")
            if not api_key:
                logger.error("URLSCAN_API_KEY environment variable not set. Aborting API call.")
            else:
                query_urlscan(url, api_key)

if __name__ == "__main__":
    main()
