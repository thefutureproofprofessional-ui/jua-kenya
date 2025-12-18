"""
Kenya Services Information Platform
A modern, responsive web application for accessing Kenyan service information
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)

# In-memory storage (replace with database in production)
SERVICES_DATA = []

# Sample initial data - ensures your site works even before N8N runs
INITIAL_DATA = [
    {
        "service_name": "Passport Application (Ordinary)",
        "category": "Government",
        "paybill_number": "222222",
        "account_format": "eCitizen Invoice No",
        "requirements": "ID, Birth Cert, Parents IDs, Recommender ID",
        "cost": "34 Pages: Ksh 7,550 | 50 Pages: Ksh 9,550 | 66 Pages: Ksh 12,050",
        "process_steps": "Apply via eCitizen -> Immigration. Booking required.",
        "source_url": "https://immigration.go.ke"
    },
    {
        "service_name": "National ID (First Time)",
        "category": "Government",
        "paybill_number": "222222",
        "account_format": "eCitizen Invoice No",
        "requirements": "Birth Cert, Parents IDs, Proof of Residence",
        "cost": "Ksh 300",
        "process_steps": "Must be done in person at Huduma Center/Registrar",
        "source_url": "https://identity.go.ke"
    },
    {
        "service_name": "Equity Bank (Mobile)",
        "category": "Banking",
        "paybill_number": "247247",
        "account_format": "Bank Account Number",
        "requirements": None,
        "cost": "Transaction Fee",
        "process_steps": "Dial USSD *247# for menu",
        "source_url": "https://equitygroupholdings.com"
    },
    {
        "service_name": "KCB Bank (Mobile)",
        "category": "Banking",
        "paybill_number": "522522",
        "account_format": "Bank Account Number",
        "requirements": None,
        "cost": "Transaction Fee",
        "process_steps": "Dial USSD *522# for menu",
        "source_url": "https://kcbgroup.com"
    },
    {
        "service_name": "DSTV Kenya",
        "category": "Entertainment",
        "paybill_number": "444900",
        "account_format": "Smart Card Number",
        "requirements": None,
        "cost": "Subscription Plan",
        "process_steps": "Ensure decoder is on when paying",
        "source_url": "https://dstv.com"
    }
]

# Initialize with sample data
SERVICES_DATA = INITIAL_DATA.copy()

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/api/services', methods=['GET', 'POST'])
def services():
    """API endpoint for services with Smart Cleaning Logic"""
    global SERVICES_DATA
    
    if request.method == 'POST':
        try:
            # 1. Get the data safely
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # 2. Extract the list (handle {"services": [...]} or direct [...])
            raw_items = data.get('services', []) if isinstance(data, dict) else data
            
            # Ensure it is a list
            if not isinstance(raw_items, list):
                raw_items = [raw_items]

            # 3. CLEAN & NORMALIZE DATA (The Safety Net)
            cleaned_services = []
            
            for item in raw_items:
                # Skip garbage items (like empty strings or raw HTML blocks)
                if not isinstance(item, dict) or 'html' in str(item).lower():
                    continue
                    
                # Force the keys to match your website template exactly
                normalized_item = {
                    "service_name": item.get('service_name') or item.get('title') or "Unknown Service",
                    "category": item.get('category') or "General",
                    
                    # CRITICAL FIX: Look for 'paybill', 'paybill_number', or 'Paybill'
                    # and save it strictly as 'paybill_number' for your frontend
                    "paybill_number": str(item.get('paybill_number') or item.get('paybill') or item.get('Paybill') or "N/A"),
                    
                    "account_format": item.get('account_format') or "Account No",
                    "cost": str(item.get('cost') or "Standard Rates"),
                    "process_steps": item.get('process_steps') or "Check provider details",
                    "source_url": item.get('source_url') or "#",
                    "requirements": item.get('requirements') or None
                }
                cleaned_services.append(normalized_item)

            # 4. Update the database ONLY if we have valid data
            if len(cleaned_services) > 0:
                SERVICES_DATA = cleaned_services
                print(f"[SUCCESS] Website updated with {len(SERVICES_DATA)} clean services")
                return jsonify({"status": "success", "count": len(SERVICES_DATA)}), 200
            else:
                print("[WARNING] Received empty or garbage data. Keeping old data.")
                return jsonify({"status": "ignored", "message": "No valid data found in request"}), 400

        except Exception as e:
            print(f"[ERROR] Update failed: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    
    # GET request - return services to the frontend
    category = request.args.get('category')
    search = request.args.get('search', '').lower()
    
    filtered = SERVICES_DATA
    
    if category:
        filtered = [s for s in filtered if s.get('category') == category]
    
    if search:
        filtered = [s for s in filtered if 
                   search in s.get('service_name', '').lower() or 
                   search in s.get('requirements', '').lower()]
    
    return jsonify(filtered)

@app.route('/api/categories')
def categories():
    """Get all unique categories"""
    try:
        # Ensure SERVICES_DATA is a list
        if not isinstance(SERVICES_DATA, list):
            return jsonify([])
        
        cats = list(set(s.get('category', 'Unknown') for s in SERVICES_DATA if isinstance(s, dict)))
        return jsonify(sorted(cats))
    except Exception as e:
        print(f"[ERROR] Categories endpoint failed: {e}")
        return jsonify([]), 500

@app.route('/service/<service_name>')
def service_detail(service_name):
    """Service detail page"""
    service = next((s for s in SERVICES_DATA if s['service_name'] == service_name), None)
    if service:
        return render_template('service_detail.html', service=service)
    return "Service not found", 404

if __name__ == '__main__':
    # In production, use gunicorn or similar
    app.run(debug=True, host='0.0.0.0', port=5000)
