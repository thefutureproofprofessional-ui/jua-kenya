"""
Kenya Services Information Platform
Fixed: Includes 'Garbage Filter' to block Z-Index and CSS errors.
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# In-memory storage
SERVICES_DATA = []

# Sample initial data
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

# --- THE FIREWALL: CLEANING LOGIC ---
def is_garbage(item):
    """Returns True if the item looks like a bug (CSS, Z-Index, etc)"""
    if not isinstance(item, dict): return True
    
    # 1. Get the name
    raw_name = str(item.get('service_name') or item.get('title') or "").lower()
    
    # 2. Block CSS/Code keywords (The "Z-Index" Fix)
    bad_words = ['z-index', 'width', 'height', 'padding', 'margin', 'charset', 'viewport', 'var(', 'function']
    if any(word in raw_name for word in bad_words):
        return True
        
    # 3. Block HTML artifacts
    if '&' in raw_name or ';' in raw_name or '{' in raw_name:
        return True
        
    # 4. Block nonsense names
    if len(raw_name) < 3 or raw_name.isdigit():
        return True
        
    return False

def clean_item(item):
    """Polishes a valid item for display"""
    return {
        "service_name": (item.get('service_name') or item.get('title') or "Unknown").title(),
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

@app.route('/api/services', methods=['GET', 'POST'])
def services():
    global SERVICES_DATA
    
    # POST: Update Data (from N8N or Scraper)
    if request.method == 'POST':
        try:
            data = request.get_json()
            raw_items = data.get('services', []) if isinstance(data, dict) else data
            if not isinstance(raw_items, list): raw_items = [raw_items]

            cleaned_list = []
            
            for item in raw_items:
                # 1. Run the Firewall
                if is_garbage(item):
                    continue 
                
                # 2. Clean valid items
                cleaned_list.append(clean_item(item))

            if len(cleaned_list) > 0:
                # Keep backup data at the start, append new data
                SERVICES_DATA = INITIAL_DATA + cleaned_list
                print(f"[SUCCESS] Website updated with {len(cleaned_list)} clean services.")
                return jsonify({"status": "success", "count": len(cleaned_list)}), 200
            else:
                return jsonify({"status": "ignored", "message": "All data was garbage/z-index"}), 400

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    # GET: Fetch Data
    category = request.args.get('category')
    search = request.args.get('search', '').lower()
    
    filtered = SERVICES_DATA
    
    if category and category != 'all':
        filtered = [s for s in filtered if s['category'].lower() == category.lower()]
    
    if search:
        filtered = [s for s in filtered if 
                   search in s['service_name'].lower() or 
                   search in str(s.get('paybill_number', '')).lower()]
    
    return jsonify(filtered)

@app.route('/api/categories')
def categories():
    if not SERVICES_DATA: return jsonify([])
    cats = list(set(s['category'] for s in SERVICES_DATA))
    return jsonify(sorted(cats))

@app.route('/service/<service_name>')
def service_detail(service_name):
    service = next((s for s in SERVICES_DATA if s['service_name'].lower() == service_name.lower()), None)
    if service:
        return render_template('service_detail.html', service=service)
    return "Service not found", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
