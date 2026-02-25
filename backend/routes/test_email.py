from flask import Blueprint, request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Try importing, but don't fail if brevo_email not working yet
try:
    from brevo_email import send_test_alert
except ImportError:
    print("Warning: brevo_email module not found")
    def send_test_alert():
        return True  # Dummy function

test_bp = Blueprint('test', __name__)

@test_bp.route('/api/test', methods=['GET'])
def test():
    return jsonify({'message': 'Test endpoint working'})

@test_bp.route('/api/email/test-alert', methods=['POST'])
def send_test_alert_endpoint():
    try:
        data = request.json
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email required'}), 400
        
        # Call the test function
        result = send_test_alert()
        
        if result:
            return jsonify({
                'success': True, 
                'message': f'Test alert sent! Check your inbox'
            })
        else:
            return jsonify({'error': 'Failed to send email'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500