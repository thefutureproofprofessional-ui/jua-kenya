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

# Sample initial data
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

SERVICES_DATA = INITIAL_DATA.copy()

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/api/services', methods=['GET', 'POST'])
def services():
    """API endpoint for services"""
    if request.method == 'POST':
        # Update services from N8N
        data = request.get_json()
        
        # Handle both formats: {"services": [...]} or direct array [...]
        if 'services' in data:
            new_services = data['services']
        else:
            new_services = data
        
        # Ensure it's a list
        if not isinstance(new_services, list):
            new_services = [new_services]
        
        global SERVICES_DATA
        SERVICES_DATA = new_services
        
        print(f"[N8N UPDATE] Updated {len(SERVICES_DATA)} services")
        return jsonify({"status": "success", "message": "Services updated"}), 200
    
    # GET request - return services
    category = request.args.get('category')
    search = request.args.get('search', '').lower()
    
    filtered = SERVICES_DATA
    
    if category:
        filtered = [s for s in filtered if s['category'] == category]
    
    if search:
        filtered = [s for s in filtered if 
                   search in s['service_name'].lower() or 
                   search in s.get('requirements', '').lower()]
    
    return jsonify(filtered)

@app.route('/api/categories')
def categories():
    """Get all unique categories"""
    cats = list(set(s['category'] for s in SERVICES_DATA))
    return jsonify(sorted(cats))

@app.route('/service/<service_name>')
def service_detail(service_name):
    """Service detail page"""
    service = next((s for s in SERVICES_DATA if s['service_name'] == service_name), None)
    if service:
        return render_template('service_detail.html', service=service)
    return "Service not found", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
