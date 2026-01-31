import requests
import socket
import time
import json
import sys
import os

CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print("❌ config.json not found")
        sys.exit(2)

    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

config = load_config()

STATUSPAGE_API_KEY = config["statuspage_api_key"]
PAGE_ID = config["page_id"]
COMPONENT_ID = config["component_id"]

MC_HOST = config["mc_host"]
MC_PORT = config.get("mc_port", 25565)
CHECK_INTERVAL = config.get("check_interval", 60)

def is_server_online():
    try:
        sock = socket.create_connection((MC_HOST, MC_PORT), timeout=5)
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

print("✅ Minecraft Server Status Checker started")

while True:
    update_status("operational" if is_server_online() else "major_outage")
    print(f"Found Minecraft Server Instance on {MC_PORT}")
    time.sleep(CHECK_INTERVAL)
