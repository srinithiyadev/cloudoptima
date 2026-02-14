from flask import Flask, jsonify
from flask_cors import CORS
from alert import alert_bp
from aws_api import aws_bp
from routes.test_email import test_bp
import os

# ✅ FIRST - Create the app
app = Flask(__name__)
CORS(app)

# ✅ THEN - Register blueprints (AFTER app exists)
app.register_blueprint(aws_bp, url_prefix='/api/aws')
app.register_blueprint(alert_bp, url_prefix='/api/alert')
app.register_blueprint(test_bp)          # ← NOW THIS WORKS!

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'CloudOptima API'})

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
