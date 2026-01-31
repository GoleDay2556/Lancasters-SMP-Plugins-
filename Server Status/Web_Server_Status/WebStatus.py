import requests
import socket
import time
import json
import sys
import os

VERSION = "V1.0Web" #Version (DO NOT CHANGE)
CONFIG_FILE = "config.json" #Configuration File (DO NOT CHANGE)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print("❌ config.json not found")
        sys.exit(1)

    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

config = load_config()

STATUSPAGE_API_KEY = config["statuspage_api_key"]
PAGE_ID = config["page_id"]
COMPONENT_ID = config["component_id"]

WEB_HOST = config["panel_host"]
WEB_PORT = config.get("panel_port", 25565)
CHECK_INTERVAL = config.get("check_interval", 60)

def is_server_online():
    try:
        sock = socket.create_connection((WEB_HOST, WEB_PORT), timeout=5)
        sock.close()
        return True
    except:
        return False
def update_status(status):
    url = f"https://api.statuspage.io/v1/pages/{PAGE_ID}/components/{COMPONENT_ID}"
    headers = {
        "Authorization": f"OAuth {STATUSPAGE_API_KEY}"
    }
    data = {
        "component[status]": status
    }
    r = requests.patch(url, headers=headers, data=data)
    print(f"Status → {status} ({r.status_code})")

print("✅ Web Status Checker started" + VERSION)

while True:
    update_status("operational" if is_server_online() else "partial_outage")
    time.sleep(CHECK_INTERVAL)
