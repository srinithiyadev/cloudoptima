from flask import Flask, render_template, jsonify, request
import json
import scanner  # Your scanner module
from datetime import datetime
import os

app = Flask(__name__)

def load_scan_data():
    """Load scan results from file"""
    data_file = 'data/scan_results.json'
    
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            return json.load(f)
    
    # If no scan yet, run mock scan
    return scanner.mock_scan()

@app.route('/')
def dashboard():
    data = load_scan_data()
    return render_template('index.html', 
                         instances=data['resources'],
                         last_scan=data['scan_time'],
                         savings=data['total_savings'])

@app.route('/api/data')
def api_data():
    """JSON API endpoint"""
    return jsonify(load_scan_data())

@app.route('/api/scan', methods=['POST'])
def run_scan():
    """Run a new scan"""
    try:
        scan_data = scanner.mock_scan()
        return jsonify({
            "success": True,
            "message": f"Found {scan_data['idle_count']} idle resources",
            "savings": scan_data["total_savings"],
            "scan_time": scan_data["scan_time"]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    # Create data directory if not exists
    os.makedirs('data', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)