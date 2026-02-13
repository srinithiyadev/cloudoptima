from flask import Flask, jsonify
from flask_cors import CORS
from alert import alert_bp
from aws_api import aws_bp
import os
from routes.test_email import test_bp    # ← IMPORT THE BLUEPRINT
app.register_blueprint(test_bp)          # ← REGISTER THE BLUEPRINT

app = Flask(__name__)
CORS(app)


@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'CloudOptima API'})

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
