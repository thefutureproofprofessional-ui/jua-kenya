"""
Kenya Services Information Platform
Direct Link Architecture: Python <--> Cloudflare
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests  # NEW: Allows Python to download data directly
import json

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
# Replace this with your actual Cloudflare Worker URL
CLOUDFLARE_WORKER_URL = "https://steep-mode-9a93.thefutureproofprofessional.workers.dev/"

# --- DATA STORAGE ---
SERVICES_DATA = []

# Backup Data (Safe Fallback)
INITIAL_DATA = [
    {
        "service_name": "Passport Application (Ordinary)",
        "category": "Government",
        "paybill_number": "222222",
        "account_format": "eCitizen Invoice No",
        "requirements": "ID, Birth Cert, Parents IDs",
        "cost": "Ksh 4,550",
        "source_url": "https://immigration.go.ke"
    },
    {
        "service_name": "Kenya Power (Prepaid)",
        "category": "Utilities",
        "paybill_number": "888880",
        "account_format": "Meter No",
        "requirements": "None",
        "cost": "Bill Amount",
        "source_url": "https://kplc.co.ke"
    }
]
SERVICES_DATA = INITIAL_DATA.copy()

# --- HELPER: CLEANING LOGIC ---
def clean_and_format(item):
    """Filters out garbage data from the scraper"""
    if not isinstance(item, dict): return None
    
    # 1. Get Name
    raw_name = str(item.get('service_name') or item.get('title') or "")
    
    # 2. Block Garbage (HTML code, Z-Index, etc)
    if '&' in raw_name or ';' in raw_name or 'z-index' in raw_name.lower():
        return None
    if len(raw_name) < 4 or raw_name.isdigit():
        return None

    # 3. Format Fields
    return {
        "service_name": raw_name.title(),
        "category": (item.get('category') or "General").title(),
        "paybill_number": str(item.get('paybill_number') or item.get('paybill') or "N/A"),
        "account_format": item.get('account_format') or "Account No",
        "cost": str(item.get('cost') or "Standard Rates"),
        "requirements": item.get('requirements') or "No specific requirements",
        "process_steps": item.get('process_steps') or "Check official website",
        "source_url": item.get('source_url') or "#"
    }

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

# NEW: The "Trigger" Route
# Visiting this URL forces Python to go fetch new data
@app.route('/update-now', methods=['GET'])
def trigger_update():
    global SERVICES_DATA
    try:
        print("Connecting to Cloudflare...")
        response = requests.get(CLOUDFLARE_WORKER_URL, timeout=10)
        
        if response.status_code != 200:
            return jsonify({"error": "Cloudflare refused connection", "code": response.status_code}), 500
            
        data = response.json()
        
        # Cloudflare usually returns { "data": [...] }
        raw_list = data.get('data', []) if isinstance(data, dict) else data
        
        # Clean the data
        clean_list = []
        for item in raw_list:
            clean_item = clean_and_format(item)
            if clean_item:
                clean_list.append(clean_item)
                
        # Update Memory
        if len(clean_list) > 0:
            # We keep the backup data at the top, then add new findings
            SERVICES_DATA = INITIAL_DATA + clean_list
            print(f"SUCCESS: Updated with {len(clean_list)} new services.")
            return jsonify({
                "status": "success", 
                "message": "Database updated successfully", 
                "total_services": len(SERVICES_DATA)
            })
        else:
            return jsonify({"status": "warning", "message": "Cloudflare returned 0 valid items"}), 200

    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/services')
def get_services():
    """Frontend fetches data from here"""
    category = request.args.get('category')
    search = request.args.get('search', '').lower()
    
    filtered = SERVICES_DATA
    
    if category and category != 'all':
        filtered = [s for s in filtered if s['category'].lower() == category.lower()]
    
    if search:
        filtered = [s for s in filtered if search in s['service_name'].lower()]
        
    return jsonify(filtered)

@app.route('/api/categories')
def get_categories():
    if not SERVICES_DATA: return jsonify([])
    cats = list(set(s['category'] for s in SERVICES_DATA))
    return jsonify(sorted(cats))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
