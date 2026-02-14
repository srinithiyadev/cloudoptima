from flask import Blueprint, request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from brevo_email import send_test_alert

test_bp = Blueprint('test', __name__)

@test_bp.route('/api/email/test-alert', methods=['POST'])
def send_test_alert_endpoint():
    try:
        data = request.json
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email required'}), 400
        
        # Call the test function - it doesn't need parameters
        result = send_test_alert()
        
        if result:
            return jsonify({
                'success': True, 
                'message': f'Test alert sent! Check {email} (email sent to srinithiyadevops@gmail.com)'
            })
        else:
            return jsonify({'error': 'Failed to send email'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
