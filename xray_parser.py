#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import json
import sys
import re
from urllib.parse import urlparse, parse_qs, unquote

def sanitize_filename(name):
    """
    Sanitizes a string to be used as a valid filename.
    Replaces spaces with underscores and removes characters that are not
    alphanumeric, underscores, or hyphens.
    """
    if not name:
        return "unnamed_config"
    name = re.sub(r'[\s/\\|:<>*?"\']+', '_', name)
    name = re.sub(r'[^\w\-_.]', '', name)
    return name if name else "unnamed_config"

def get_param(params, key, default=None):
    """Helper to get a single value from parsed query string."""
    val = params.get(key)
    if val is None:
        return default
    return val[0] if isinstance(val, list) else val

def build_stream_settings(params: dict, default_host: str) -> dict:
    """
    Constructs the streamSettings object based on parsed link parameters.
    This is a comprehensive implementation based on Xray documentation.
    """
    network = get_param(params, "net") or get_param(params, "type", "tcp")
    security = get_param(params, "tls") or get_param(params, "security", "none")
    
    stream_settings = {"network": network, "security": security}

    # --- Socket Options (sockopt) ---
    sockopt = {}
    if get_param(params, "mark"): sockopt["mark"] = int(get_param(params, "mark"))
    if get_param(params, "tcpFastOpen"): sockopt["tcpFastOpen"] = get_param(params, "tcpFastOpen") in [True, 'true']
    if get_param(params, "tproxy"): sockopt["tproxy"] = get_param(params, "tproxy")
    if sockopt:
        stream_settings["sockopt"] = sockopt

    # --- Transport Protocol Settings ---
    if network == "tcp":
        header_type = get_param(params, "headerType", "none")
        if header_type == "http":
            host = get_param(params, "host", default_host)
            path = get_param(params, "path", "/")
            stream_settings["tcpSettings"] = {
                "header": {
                    "type": "http",
                    "request": {"path": path.split(','), "headers": {"Host": [host]}}
                }
            }
    elif network == "kcp":
        stream_settings["kcpSettings"] = {
            "mtu": int(get_param(params, "mtu", 1350)), "tti": int(get_param(params, "tti", 50)),
            "uplinkCapacity": int(get_param(params, "uplinkCapacity", 5)),
            "downlinkCapacity": int(get_param(params, "downlinkCapacity", 20)),
            "congestion": get_param(params, "congestion", False) in [True, 'true'],
            "readBufferSize": int(get_param(params, "readBufferSize", 2)),
            "writeBufferSize": int(get_param(params, "writeBufferSize", 2)),
            "header": {"type": get_param(params, "headerType", "none")},
            "seed": get_param(params, "path") # mKCP uses 'path' as 'seed'
        }
    elif network == "ws":
        stream_settings["wsSettings"] = {
            "path": get_param(params, "path", "/"),
            "Host": get_param(params, "host", default_host)
        }
    elif network == "h2":
        stream_settings["httpSettings"] = {
            "host": [get_param(params, "host", default_host)],
            "path": get_param(params, "path", "/")
        }
    elif network == "httpupgrade":
        stream_settings["httpUpgradeSettings"] = {
            "path": get_param(params, "path", "/"),
            "host": get_param(params, "host", default_host)
        }
    elif network == "quic":
        stream_settings["quicSettings"] = {
            "security": get_param(params, "quicSecurity", "none"),
            "key": get_param(params, "key", ""),
            "header": {"type": get_param(params, "headerType", "none")}
        }
    elif network == "grpc":
        stream_settings["grpcSettings"] = {
            "serviceName": get_param(params, "serviceName", ""),
            "multiMode": get_param(params, "mode") == "multi"
        }

    # --- Security Settings (TLS / XTLS / REALITY) ---
    if security in ["tls", "xtls"]:
        sni = get_param(params, "sni", get_param(params, "peer", default_host))
        alpn = get_param(params, "alpn", "")
        fingerprint = get_param(params, "fp", "")
        
        security_settings = {"serverName": sni, "allowInsecure": get_param(params, "allowInsecure", False) in [True, 'true']}
        if alpn: security_settings["alpn"] = alpn.split(',')
        if fingerprint: security_settings["fingerprint"] = fingerprint
        if security == "xtls" and get_param(params, "flow"):
            security_settings["flow"] = get_param(params, "flow")
            
        stream_settings[f"{security}Settings"] = security_settings
        
    elif security == "reality":
        sni = get_param(params, "sni", get_param(params, "peer", default_host))
        stream_settings["realitySettings"] = {
            "serverName": sni,
            "fingerprint": get_param(params, "fp", "chrome"),
            "publicKey": get_param(params, "pbk", ""),
            "shortId": get_param(params, "sid", ""),
            "spiderX": get_param(params, "spx", "/")
        }

    return stream_settings

def parse_vmess(link: str) -> dict:
    """Parses a VMess share link."""
    try:
        vmess_data = json.loads(base64.b64decode(link[8:]).decode('utf-8'))
        address = vmess_data.get("add", "")
        tag = vmess_data.get("ps", address)
        return {
            "outbounds": [
                {
                "protocol": "vmess",
                "settings": {"vnext": [{"address": address, "port": int(vmess_data.get("port", 0)),
                    "users": [{"id": vmess_data.get("id", ""), "alterId": int(vmess_data.get("aid", 0)),
                            "security": vmess_data.get("scy", "auto"), "level": 0}]}]},
                "streamSettings": build_stream_settings(vmess_data, address),
                "tag": "outbound_" + tag
                }
            ],
            "remarks": tag

        }
    except Exception as e:
        print(f"Error parsing VMess link: {e}", file=sys.stderr)
        return None

def parse_vless(link: str) -> dict:
    """Parses a VLESS share link."""
    try:
        parsed_url = urlparse(link)
        params = parse_qs(parsed_url.query)
        address = parsed_url.hostname or ""
        tag = unquote(parsed_url.fragment) if parsed_url.fragment else address
        return {
            "outbounds": [
                {
                "protocol": "vless",
                "settings": {"vnext": [{"address": address, "port": int(parsed_url.port or 0),
                    "users": [{"id": parsed_url.username or "", "encryption": get_param(params, "encryption", "none"),
                            "flow": get_param(params, "flow", "")}]}]},
                "streamSettings": build_stream_settings(params, address),
                "tag": "outbound_" + tag
                }
            ],
            "remarks": tag
        }
    except Exception as e:
        print(f"Error parsing VLESS link: {e}", file=sys.stderr)
        return None

def parse_trojan(link: str) -> dict:
    """Parses a Trojan share link."""
    try:
        parsed_url = urlparse(link)
        params = parse_qs(parsed_url.query)
        address = parsed_url.hostname or ""
        tag = unquote(parsed_url.fragment) if parsed_url.fragment else address

        return {
            "outbounds": [
                {
                "protocol": "trojan",
                "settings": {"servers": [{"address": address, "port": int(parsed_url.port or 0),
                                        "password": parsed_url.username or ""}]},
                "streamSettings": build_stream_settings(params, address),
                "tag": "outbound_" + tag
                }
            ],
            "remarks": tag
        }
    except Exception as e:
        print(f"Error parsing Trojan link: {e}", file=sys.stderr)
        return None

def parse_ss(link: str) -> dict:
    """Parses a Shadowsocks (SS) share link."""
    try:
        if link.startswith("ss://"):
            parsed_url = urlparse(link)
            decoded_part = base64.urlsafe_b64decode(parsed_url.netloc + "==").decode('utf-8')
            method, password = decoded_part.split(':', 1)
            address = parsed_url.hostname
            port = parsed_url.port
            tag = unquote(parsed_url.fragment) if parsed_url.fragment else address
        else: # SIP002 format ss://BASE64#TAG
            full_b64 = link[5:].split('#')
            decoded_part = base64.urlsafe_b64decode(full_b64[0] + "==").decode('utf-8')
            method, rest = decoded_part.split(':', 1)
            password, server_part = rest.rsplit('@', 1)
            address, port_str = server_part.split(':', 1)
            port = int(port_str)
            tag = unquote(full_b64[1]) if len(full_b64) > 1 else address

        return {
            "outbounds": [
                {
                "protocol": "shadowsocks",
                "settings": {"servers": [{"method": method, "password": password,
                                        "address": address, "port": port}]},
                "tag": "outbound_" + tag
                }
            ],
            "remarks": tag
        }
    except Exception as e:
        print(f"Error parsing Shadowsocks link: {e}", file=sys.stderr)
        return None

def save_config_to_file(config: dict):
    if not config or "remarks" not in config:
        print("Cannot save file: configuration is invalid or missing a tag.", file=sys.stderr)
        return
    filename = f"{sanitize_filename(config['remarks'])}.json"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print(f"✅ Successfully created configuration file: {filename}")
    except IOError as e:
        print(f"Error writing to file {filename}: {e}", file=sys.stderr)

def main():
    if len(sys.argv) < 2:
        print("Usage: python xray_parser.py <share_link_1> [share_link_2] ...")
        print("Example: python xray_parser.py \"vless://...\"")
        sys.exit(1)

    for link in sys.argv[1:]:
        print(f"\nProcessing link: {link[:50]}...")
        config = None
        if link.startswith("vmess://"):
            config = parse_vmess(link)
        elif link.startswith("vless://"):
            config = parse_vless(link)
        elif link.startswith("trojan://"):
            config = parse_trojan(link)
        elif link.startswith("ss://"):
            config = parse_ss(link)
        else:
            print(f"Unsupported link protocol: {link}", file=sys.stderr)
            continue
        if config:
            save_config_to_file(config)

if __name__ == "__main__":
    main()

