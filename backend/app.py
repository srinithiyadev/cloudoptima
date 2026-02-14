from flask import Flask, jsonify
from flask_cors import CORS
from routes.auth import auth_bp
import os

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(auth_bp)

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'CloudOptima API'})

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    print("🚀 Starting Flask server without database...")
    app.run(debug=True, host='0.0.0.0', port=5000)