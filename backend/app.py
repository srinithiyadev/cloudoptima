from flask import Flask, jsonify
from alert import alert_bp
from aws_api import aws_bp
import os

app = Flask(__name__)

# Register API routes
app.register_blueprint(aws_bp, url_prefix='/api/aws')
app.register_blueprint(alert_bp, url_prefix='/api/alert')

@app.route('/health')
def health_check():
    """Health check endpoint for Render monitoring"""
    return jsonify({'status': 'healthy', 'service': 'CloudOptima API'})

if __name__ == '__main__':
    # Create data directory if not exists
    os.makedirs('data', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)

