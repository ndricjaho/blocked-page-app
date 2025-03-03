__version__ = "1.0.0"  # Start with version 1.0.0

import logging
from flask import Flask, request, render_template
import requests
import os
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# Disable Werkzeug access logging completely
werkzeug_log = logging.getLogger('werkzeug')
werkzeug_log.disabled = True  # Disable the Werkzeug logger


# Get logger for custom blocked domain logs (keep this as before)
blocked_domain_logger = logging.getLogger('blocked_domain_log')
blocked_domain_logger.setLevel(logging.INFO)
blocked_domain_formatter = logging.Formatter('%(message)s')
blocked_domain_handler = logging.StreamHandler(sys.stdout)
blocked_domain_handler.setFormatter(blocked_domain_formatter)
blocked_domain_logger.addHandler(blocked_domain_handler)


PIHOLE_API_URL = os.environ.get("PIHOLE_API_URL")
PIHOLE_PASSWORD = os.environ.get("PIHOLE_PASSWORD")

SESSION_ID = None
SESSION_TIMEOUT = 1800
SESSION_EXPIRY_TIME = 0

def is_session_valid(sid):
    """Checks if the session ID is valid."""
    if not PIHOLE_API_URL or not sid:
        return False

    auth_check_endpoint = f"{PIHOLE_API_URL}/api/auth"
    headers = {'sid': sid}

    try:
        response = requests.get(auth_check_endpoint, headers=headers, timeout=5, verify=False)
        response.raise_for_status()
        auth_check_data = response.json()
        return auth_check_data.get("session", {}).get("valid", False)

    except requests.exceptions.RequestException:
        return False
    except ValueError:
        return False


def get_pihole_session_id():
    """Retrieves or renews session ID."""
    global SESSION_ID, SESSION_EXPIRY_TIME, SESSION_TIMEOUT

    if SESSION_ID and is_session_valid(SESSION_ID):
        return SESSION_ID, None

    if not PIHOLE_API_URL or not PIHOLE_PASSWORD:
        return None, "Pi-hole API URL or Password not configured."

    auth_endpoint = f"{PIHOLE_API_URL}/api/auth"
    auth_payload = {"password": PIHOLE_PASSWORD}

    try:
        response = requests.post(auth_endpoint, json=auth_payload, timeout=5, verify=False)
        response.raise_for_status()
        auth_data = response.json()
        session_data = auth_data.get("session", {})
        sid = session_data.get("sid")
        validity = session_data.get("validity", SESSION_TIMEOUT)

        if sid:
            SESSION_ID = sid
            SESSION_TIMEOUT = validity
            SESSION_EXPIRY_TIME = time.time() + validity
            return SESSION_ID, None
        else:
            return None, "Pi-hole API authentication failed: SID not found."
    except requests.exceptions.RequestException as e:
        return None, f"Authentication error: {e}"
    except ValueError:
        return None, "Invalid JSON response from API auth."



def get_pihole_block_reason(domain):
    """Fetches block reasons from Pi-hole API using /api/search/{domain}."""
    sid, auth_error = get_pihole_session_id()
    if auth_error:
        return auth_error

    if not PIHOLE_API_URL or not sid:
        return "API URL or session ID missing."

    search_endpoint = f"{PIHOLE_API_URL}/api/search/{domain}" # Search endpoint
    headers = {'sid': sid}

    try:
        response = requests.get(search_endpoint, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        search_data = response.json()

        reasons = []

        # Extract domain-level block reasons (exact/regex rules)
        if "domains" in search_data.get("search", {}):
            for domain_entry in search_data["search"]["domains"]:
                comment = domain_entry.get("comment")
                if comment:
                    reasons.append(f"Custom Rule: {comment}")

        # Extract gravity block reasons (blocklists)
        if "gravity" in search_data.get("search", {}):
            for gravity_entry in search_data["search"]["gravity"]:
                list_comment = gravity_entry.get("comment")
                if list_comment:
                    reasons.append(f"{list_comment}")


        if reasons:
            return "Domain is blocked. Reasons: " + "; ".join(reasons)
        else:
            return "Domain is blocked, but specific reason from Pi-hole not available via API search."


    except requests.exceptions.RequestException as e:
        return f"Error querying Pi-hole API: {e}"
    except ValueError:
        return "Error decoding Pi-hole API response (search endpoint)."



@app.route('/')
def blocked_page():
    domain = request.host
    source_ip = request.remote_addr
    blocked_domain_logger.info(f"{domain} from {source_ip}") # Keep custom logging
    pihole_reason = get_pihole_block_reason(domain)
    return render_template('index.html', domain=domain, pihole_reason=pihole_reason)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)