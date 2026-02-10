from flask import Blueprint, request, jsonify
import time
import os

alert_bp = Blueprint('alert', __name__)

@alert_bp.route('/send', methods=['POST'])
def send_alert():
    """Send alert - Demo mode with realistic simulation"""
    try:
        data = request.json
        resource_id = data.get('resource_id', 'Unknown')
        email = data.get('email', 'team@example.com')
        
        # Simulate API call delay
        time.sleep(0.5)
        
        # Check if real credentials available (for production)
        has_sendgrid = os.getenv('SENDGRID_API_KEY')
        has_gmail = os.getenv('GMAIL_USER')
        
        mode = 'DEMO'
        if has_sendgrid or has_gmail:
            mode = 'PRODUCTION_READY'
        
        return jsonify({
            'success': True,
            'message': f'🚨 Alert processed for {resource_id}',
            'alert': {
                'id': f'alert_{int(time.time())}',
                'resource': resource_id,
                'recipient': email,
                'channel': 'email',
                'status': 'sent',
                'mode': mode,
                'note': 'Real email would be sent in production via SendGrid/Gmail API'
            },
            'integration_ready': bool(has_sendgrid or has_gmail)
        })
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e),
            'message': 'Alert system error - falling back to demo'
        }), 500

@alert_bp.route('/channels', methods=['GET'])
def available_channels():
    """List available alert channels"""
    return jsonify({
        'channels': [
            {'id': 'email', 'name': 'Email', 'status': 'demo'},
            {'id': 'slack', 'name': 'Slack', 'status': 'planned'},
            {'id': 'teams', 'name': 'Microsoft Teams', 'status': 'planned'}
        ],
        'setup_guide': 'Add SENDGRID_API_KEY or SLACK_WEBHOOK to enable real alerts'
    })