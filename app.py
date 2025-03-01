from flask import Flask, request, render_template
import requests
import os

app = Flask(__name__)

PIHOLE_API_URL = os.environ.get("PIHOLE_API_URL")
PIHOLE_PASSWORD = os.environ.get("PIHOLE_PASSWORD") # Using password now, not API token

def get_pihole_session_id():
    """Authenticates with Pi-hole API and returns a session ID (SID)."""
    if not PIHOLE_API_URL or not PIHOLE_PASSWORD:
        return None, "Pi-hole API URL or Password not configured."

    auth_endpoint = f"{PIHOLE_API_URL}/api/auth"
    auth_payload = {"password": PIHOLE_PASSWORD}

    try:
        response = requests.post(auth_endpoint, json=auth_payload, timeout=5, verify=False) # verify=False as before if needed
        response.raise_for_status()
        auth_data = response.json()
        sid = auth_data.get("sid")
        if sid:
            return sid, None # Return SID and no error
        else:
            return None, "Pi-hole API authentication failed: SID not found in response."
    except requests.exceptions.RequestException as e:
        return None, f"Error authenticating with Pi-hole API: {e}"
    except ValueError:
        return None, "Error decoding Pi-hole API auth response (invalid JSON)."

def get_pihole_block_reason(domain):
    """Queries Pi-hole API for blocking reason using session ID."""
    sid, auth_error = get_pihole_session_id()
    if auth_error:
        return auth_error

    if not PIHOLE_API_URL or not sid: # Check for SID now
        return "Pi-hole API credentials or session ID missing."

    api_endpoint = f"{PIHOLE_API_URL}/api/domain/info/{domain}" # New endpoint for domain info
    params = {
        "sid": sid # Pass SID as query parameter
    }

    try:
        response = requests.get(api_endpoint, params=params, timeout=10, verify=False) # verify=False as before if needed
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "blocked":
            blocking_reasons = data.get("reasons", []) # Reasons are now in a list called "reasons" in v6
            if blocking_reasons:
                return "Domain is blocked. Reasons: " + "; ".join(blocking_reasons)
            else:
                return "Domain is blocked, but specific reason from Pi-hole not available."
        elif data.get("status") == "OK":
            return "Domain is not blocked by Pi-hole."
        else:
            return "Pi-hole API returned an unexpected response."

    except requests.exceptions.RequestException as e:
        return f"Error querying Pi-hole API: {e}"
    except ValueError:
        return "Error decoding Pi-hole API response (invalid JSON)."


@app.route('/')
def blocked_page():
    domain = request.host
    pihole_reason = get_pihole_block_reason(domain)
    return render_template('index.html', domain=domain, pihole_reason=pihole_reason)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)