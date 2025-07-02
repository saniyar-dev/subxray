#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import base64
import requests
import argparse

# --- ANSI Color Codes for Visualization ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Import the parsing and saving functions from our other script.
# This requires 'xray_parser.py' to be in the same directory.
try:
    from xray_parser import (
        parse_vmess,
        parse_vless,
        parse_trojan,
        parse_ss,
        save_config_to_file
    )
except ImportError:
    print(f"{Colors.FAIL}Error: 'xray_parser.py' not found.{Colors.ENDC}", file=sys.stderr)
    print(f"{Colors.WARNING}Please make sure 'xray_parser.py' is in the same directory as this script.{Colors.ENDC}", file=sys.stderr)
    sys.exit(1)

def print_banner():
    """Prints a cool, colorful banner to the console."""
    banner = f"""
{Colors.HEADER}{Colors.BOLD}
███████╗██╗   ██╗██████╗ ██╗  ██╗██████╗  █████╗ ██╗   ██╗
██╔════╝██║   ██║██╔══██╗╚██╗██╔╝██╔══██╗██╔══██╗╚██╗ ██╔╝
███████╗██║   ██║██████╔╝ ╚███╔╝ ██████╔╝███████║ ╚████╔╝ 
╚════██║██║   ██║██╔══██╗ ██╔██╗ ██╔══██╗██╔══██║  ╚██╔╝  
███████║╚██████╔╝██████╔╝██╔╝ ██╗██║  ██║██║  ██║   ██║   
╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   
{Colors.ENDC}
{Colors.CYAN}              Xray Config Generator Tool
{Colors.BLUE}======================================================{Colors.ENDC}
    """
    print(banner)


def fetch_links_from_subscription(url: str) -> list:
    """
    Fetches content from a subscription URL, decodes it from Base64,
    and returns a list of individual share links.
    """
    print(f"{Colors.CYAN}Fetching subscription from: {Colors.UNDERLINE}{url}{Colors.ENDC}")
    try:
        # Use a timeout and a common user-agent header
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"{Colors.FAIL}Error fetching URL: {e}{Colors.ENDC}", file=sys.stderr)
        return []

    # Subscription content is typically Base64 encoded.
    try:
        decoded_content = base64.b64decode(response.content).decode('utf-8')
        # Split into a list of links, stripping any whitespace from each line
        links = [line.strip() for line in decoded_content.splitlines() if line.strip()]
        print(f"{Colors.GREEN}Successfully fetched and decoded {len(links)} links.{Colors.ENDC}")
        return links
    except (base64.binascii.Error, UnicodeDecodeError) as e:
        print(f"{Colors.FAIL}Error decoding subscription content: {e}{Colors.ENDC}", file=sys.stderr)
        print(f"{Colors.WARNING}The content might not be Base64 encoded or is corrupted.{Colors.ENDC}", file=sys.stderr)
        return []

def main():
    """
    Main function to fetch links from a URL and parse them into config files.
    """
    print_banner()

    parser = argparse.ArgumentParser(
        description="Fetch and parse Xray subscription links into individual config files.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("url", help="The subscription URL to fetch links from.")
    parser.add_argument(
        "--omit-first",
        action="store_true",
        help="Omit the first link from the subscription list (often a stats link)."
    )
    args = parser.parse_args()

    links = fetch_links_from_subscription(args.url)

    if not links:
        print(f"{Colors.WARNING}No links to process. Exiting.{Colors.ENDC}")
        sys.exit(1)

    # If the omit-first flag is set, remove the first link from the list
    if args.omit_first:
        if len(links) > 0:
            omitted_link = links.pop(0)
            print(f"{Colors.CYAN}Omitting first link as requested: {Colors.ENDC}{omitted_link[:50]}...")
        else:
            print(f"{Colors.WARNING}--omit-first flag was used, but there are no links to omit.{Colors.ENDC}")


    successful_configs = 0
    failed_configs = 0

    for link in links:
        print(f"\n{Colors.BLUE}Processing link: {Colors.ENDC}{link[:50]}...")
        config = None
        # Determine the protocol and call the appropriate parser function
        if link.startswith("vmess://"):
            config = parse_vmess(link)
        elif link.startswith("vless://"):
            config = parse_vless(link)
        elif link.startswith("trojan://"):
            config = parse_trojan(link)
        elif link.startswith("ss://"):
            config = parse_ss(link)
        else:
            print(f"{Colors.WARNING}Skipping unsupported link protocol: {link}{Colors.ENDC}", file=sys.stderr)
            failed_configs += 1
            continue
        
        if config:
            save_config_to_file(config)
            successful_configs += 1
        else:
            print(f"{Colors.FAIL}Failed to parse link: {link}{Colors.ENDC}", file=sys.stderr)
            failed_configs += 1
    
    summary = f"""
{Colors.BLUE}======================================================{Colors.ENDC}
{Colors.BOLD}                      SUMMARY                       {Colors.ENDC}
{Colors.BLUE}======================================================{Colors.ENDC}
{Colors.GREEN}Successfully generated configs: {successful_configs}{Colors.ENDC}
{Colors.FAIL}Failed or skipped links:      {failed_configs}{Colors.ENDC}
{Colors.BLUE}======================================================{Colors.ENDC}
    """
    print(summary)


if __name__ == "__main__":
    main()

