from flask import Flask, request, render_template
import requests
import os

app = Flask(__name__)

PIHOLE_API_URL = os.environ.get("PIHOLE_API_URL")
PIHOLE_API_TOKEN = os.environ.get("PIHOLE_API_TOKEN")

def get_pihole_block_reason(domain):
    if not PIHOLE_API_URL or not PIHOLE_API_TOKEN:
        return "Pi-hole API credentials not configured."

    api_endpoint = f"{PIHOLE_API_URL}/api.php"
    params = {
        "domaininfo": domain,
        "auth": PIHOLE_API_TOKEN
    }

    try:
        response = requests.get(api_endpoint, params=params, timeout=5) # Added timeout
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if data.get("status") == "blocked":
            blocking_lists = data.get(" GranadaDBGroupLists", []) # Check for lists
            blocking_gravity = data.get("gravity", "Unknown Gravity Reason") # Gravity reason
            blocking_regex = data.get("regex_list", []) # Check for regex rules
            blocking_exact = data.get("exact_list", []) # Check for exact rules

            reasons = []
            if blocking_lists:
                reasons.append(f"Blocked by lists: {', '.join(blocking_lists)}")
            if blocking_gravity != "Unknown Gravity Reason": # Check if Gravity provided a reason
                reasons.append(f"Blocked by Gravity: {blocking_gravity}")
            if blocking_regex:
                reasons.append(f"Blocked by Regex Rules: {', '.join(blocking_regex)}")
            if blocking_exact:
                reasons.append(f"Blocked by Exact Rules: {', '.join(blocking_exact)}")


            if reasons:
                return "Domain is blocked. Reasons: " + "; ".join(reasons)
            else:
                return "Domain is blocked, but specific reason from Pi-hole not available."
        elif data.get("status") == "OK":
            return "Domain is not blocked by Pi-hole."
        else:
            return "Pi-hole API returned an unexpected response."

    except requests.exceptions.RequestException as e:
        return f"Error querying Pi-hole API: {e}"
    except ValueError: # JSONDecodeError
        return "Error decoding Pi-hole API response (invalid JSON)."


@app.route('/')
def blocked_page():
    domain = request.host
    pihole_reason = get_pihole_block_reason(domain)
    return render_template('index.html', domain=domain, pihole_reason=pihole_reason)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)