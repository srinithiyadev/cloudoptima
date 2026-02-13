from flask import Blueprint, request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from brevo_email import send_idle_alert

# THIS IS YOUR BLUEPRINT
test_bp = Blueprint('test', __name__)

@test_bp.route('/api/email/test-alert', methods=['POST'])
def send_test_alert():
    try:
        data = request.json
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email required'}), 400
        
        test_resource = {
            'id': 'i-test-123456',
            'name': 'test-server',
            'type': 'EC2',
            'region': 'us-east-1',
            'idle_days': 7,
            'monthly_cost': 45.50
        }
        
        result = send_idle_alert(email, test_resource)
        
        if result:
            return jsonify({'success': True, 'message': 'Test alert sent!'})
        else:
            return jsonify({'error': 'Failed to send email'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500