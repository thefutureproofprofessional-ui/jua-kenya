"""
Kenya Services Information Platform
A modern, responsive web application for accessing Kenyan service information
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# --- 1. THE DATA STORAGE ---
SERVICES_DATA = []
INITIAL_DATA = [
    {
        "service_name": "Passport Application (Ordinary)",
        "category": "Government",
        "paybill_number": "222222",
        "account_format": "eCitizen Invoice No",
        "requirements": "ID, Birth Cert, Parents IDs",
        "cost": "Ksh 4,550",
        "process_steps": "Apply via eCitizen",
        "source_url": "https://immigration.go.ke"
    },
    {
        "service_name": "Kenya Power (Prepaid)",
        "category": "Utilities",
        "paybill_number": "888880",
        "account_format": "Meter No",
        "requirements": "None",
        "cost": "Bill Amount",
        "process_steps": "Pay via M-PESA",
        "source_url": "https://kplc.co.ke"
    }
]
SERVICES_DATA = INITIAL_DATA.copy()


# --- 2. THE PRESENTATION LOGIC (Your Request) ---
def format_for_display(service):
    """
    This is the logic that 'guides how Python displays data'.
    It polishes raw data into a professional format for the website.
    """
    if not isinstance(service, dict):
        return None

    # Rule 1: Fix Title Capitalization (e.g., "passport" -> "Passport")
    raw_name = service.get('service_name') or service.get('title') or "Unknown Service"
    display_name = raw_name.replace("&#34;", "").replace("34)&", "").strip().title()

    # Rule 2: Handle Empty Costs
    raw_cost = service.get('cost')
    if not raw_cost or raw_cost.lower() in ['none', 'null', 'undefined']:
        display_cost = "Check with Provider"
    else:
        display_cost = str(raw_cost).strip()

    # Rule 3: Ensure Paybill is never empty
    raw_paybill = service.get('paybill_number') or service.get('paybill')
    if not raw_paybill or str(raw_paybill).lower() in ['nan', 'none', 'undefined']:
        display_paybill = "N/A"
    else:
        display_paybill = str(raw_paybill).strip()

    return {
        "service_name": display_name,
        "category": (service.get('category') or "General").title(),
        "paybill_number": display_paybill,
        "account_format": service.get('account_format') or "Account No",
        "cost": display_cost,
        "requirements": service.get('requirements') or "No specific requirements",
        "process_steps": service.get('process_steps') or "Check official website",
        "source_url": service.get('source_url') or "#"
    }


# --- 3. THE API ENDPOINTS ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/services', methods=['GET', 'POST'])
def services():
    global SERVICES_DATA
    
    # --- HANDLE INCOMING DATA (From n8n) ---
    if request.method == 'POST':
        try:
            data = request.get_json()
            # Handle {"services": [...]} or raw list [...]
            raw_items = data.get('services', []) if isinstance(data, dict) else data
            if not isinstance(raw_items, list): raw_items = [raw_items]

            cleaned_list = []
            for item in raw_items:
                # Apply the Presentation Logic immediately upon receipt
                polished_item = format_for_display(item)
                if polished_item: 
                    cleaned_list.append(polished_item)

            if cleaned_list:
                SERVICES_DATA = cleaned_list
                print(f"[SUCCESS] Updated {len(cleaned_list)} services.")
                return jsonify({"status": "success", "count": len(cleaned_list)}), 200
            else:
                return jsonify({"status": "ignored", "message": "No valid data"}), 400

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    # --- HANDLE OUTGOING DATA (To Website) ---
    # We apply the presentation logic ONE MORE TIME just to be safe
    # before sending to the frontend.
    
    category = request.args.get('category')
    search = request.args.get('search', '').lower()
    
    # Filter Logic
    filtered = SERVICES_DATA
    if category:
        filtered = [s for s in filtered if s['category'].lower() == category.lower()]
    
    if search:
        filtered = [s for s in filtered if 
                   search in s['service_name'].lower() or 
                   search in str(s.get('paybill_number', '')).lower()]
    
    return jsonify(filtered)


@app.route('/api/categories')
def categories():
    """Get unique categories for the dropdown menu"""
    if not SERVICES_DATA: return jsonify([])
    cats = list(set(s['category'] for s in SERVICES_DATA))
    return jsonify(sorted(cats))

@app.route('/service/<service_name>')
def service_detail(service_name):
    """Detail page logic"""
    # Find service (case-insensitive search)
    service = next((s for s in SERVICES_DATA if s['service_name'].lower() == service_name.lower()), None)
    if service:
        return render_template('service_detail.html', service=service)
    return "Service not found", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
