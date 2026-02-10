from flask import Blueprint, request, jsonify
import os

alert_bp = Blueprint('alert', __name__)

@alert_bp.route('/send', methods=['POST'])
def send_alert():
    try:
        data = request.json
        resource_id = data.get('resource_id', 'Unknown')
        email = data.get('email', 'user@example.com')
        
        # In production, use real email/Slack
        # For demo, simulate alert
        print(f"📧 [ALERT] Idle resource detected: {resource_id}")
        print(f"   Would notify: {email}")
        
        return jsonify({
            'success': True,
            'message': f'Alert queued for resource {resource_id}. Email would be sent to {email}',
            'demo': True
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500# Alert endpoint added
