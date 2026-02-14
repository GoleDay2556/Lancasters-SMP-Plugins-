import requests
import socket
import time
import json
import os
from datetime import datetime

VERSION = "V1.6MC"
CONFIG_FILE = "config.json"

# ---- COLORS ----
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RESET  = "\033[0m"
# ----------------

config = None

def now_time():
    """Return current time as [HH:MM:SS]"""
    return f"[{datetime.now().strftime('%H:%M:%S')}]"

# ---------------- Config Loader ----------------
def load_config():
    global config

    if not os.path.exists(CONFIG_FILE):
        print(RED + "❌ Error1: .json File/Config Missing" + RESET)
        return False

    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        return True
    except Exception:
        print(RED + "❌ Error2: Wrong Config" + RESET)
        return False

if not load_config():
    while True:
        time.sleep(60)

# Validate required keys
required_keys = [
    "statuspage_api_key",
    "page_id",
    "component_id",
    "mc_host",
    "mc_port",
    "status_profile"
]

for key in required_keys:
    if key not in config:
        print(RED + f"❌ Error2: Missing required key '{key}'" + RESET)
        while True:
            time.sleep(60)

STATUSPAGE_API_KEY = config["statuspage_api_key"]
PAGE_ID = config["page_id"]
COMPONENT_ID = config["component_id"]

MC_HOST = config["mc_host"]
MC_PORT = config.get("mc_port", 25565)
CHECK_INTERVAL = config.get("check_interval", 60)
STATUS_PROFILE = config["status_profile"]  # starting severity

# ---------------- Status order ----------------
STATUS_ORDER = [
    "operational",
    "degraded_performance",
    "partial_outage",
    "major_outage",
    "maintenance"
]

# ---------------- Auth Test ----------------
def test_auth():
    url = f"https://api.statuspage.io/v1/pages/{PAGE_ID}"
    headers = {
        "Authorization": f"Bearer {STATUSPAGE_API_KEY}"
    }
    try:
        r = requests.get(url, headers=headers)
    except Exception as e:
        print(RED + f"❌ Error0: HTTP request failed ({e})" + RESET)
        return False

    print(now_time() + f"CONNECTION → Auth test HTTP {r.status_code}")

    if r.status_code in (200, 304):
        print(GREEN + "✅ Connection success" + RESET)
        return True
    elif r.status_code == 401:
        print(RED + "❌ Error3: Invalid API Key" + RESET)
    elif r.status_code == 404:
        print(RED + "❌ Error4: Wrong Page ID" + RESET)
    else:
        print(RED + f"❌ Error0: HTTP {r.status_code}" + RESET)

    return False

if not test_auth():
    while True:
        time.sleep(60)

# ---------------- Server Check ----------------
def is_server_online():
    try:
        sock = socket.create_connection((MC_HOST, MC_PORT), timeout=5)
        sock.close()
        return True
    except:
        return False

# ---------------- Status Update ----------------
def update_status(status):
    url = f"https://api.statuspage.io/v1/pages/{PAGE_ID}/components/{COMPONENT_ID}"
    headers = {
        "Authorization": f"Bearer {STATUSPAGE_API_KEY}"
    }
    data = {
        "component[status]": status
    }
    try:
        r = requests.patch(url, headers=headers, data=data)
        print("========== Status ==========")
        print(now_time() + YELLOW + f"Status → {status} ({r.status_code})" + RESET)
    except Exception as e:
        print(now_time() + RED + f"❌ Failed to update status ({e})" + RESET)

# ---------------- Offline Escalation ----------------
offline_since = None
last_status = None

def get_escalated_status(offline_seconds, start_level):
    """Return Statuspage status based on offline duration and starting severity."""
    try:
        start_index = STATUS_ORDER.index(start_level)
    except ValueError:
        start_index = 1  # default to degraded_performance if invalid

    # Each hour offline escalates one level
    step = int(offline_seconds // 3600)
    new_index = min(start_index + step, len(STATUS_ORDER) - 1)
    return STATUS_ORDER[new_index]

# ---------------- Main Loop ----------------
print(GREEN + f"✅ MC Status Loaded! {VERSION}" + RESET)

while True:
    online = is_server_online()
    now = time.time()

    if online:
        offline_since = None
        new_status = "operational"
    else:
        if offline_since is None:
            offline_since = now

        offline_duration = now - offline_since
        new_status = get_escalated_status(offline_duration, STATUS_PROFILE)

    # Update Statuspage only if status changed
    if new_status != last_status:
        update_status(new_status)
        last_status = new_status

    # Console log
    if online:
        print(now_time() + GREEN + f"Server online → operational" + RESET)
    else:
        print(now_time() + RED + f"Server offline for {int(offline_duration//60)} min → {new_status}" + RESET)

    time.sleep(CHECK_INTERVAL)
