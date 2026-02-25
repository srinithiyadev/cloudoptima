from flask import Flask, jsonify, request
from flask_cors import CORS
from alert import alert_bp
from aws_api import aws_bp
from routes.test_email import test_bp
from simulated_cloud import simulated_bp
import os
import pymysql
import pymysql.cursors
import sys
import traceback

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'CloudOptima2026!'),
    'database': os.getenv('DB_NAME', 'cloudoptima'),
    'port': int(os.getenv('DB_PORT', 3306))
}

def get_db_connection():
    try:
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port'],
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=5
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        traceback.print_exc()
        return None

app = Flask(__name__)
CORS(app, origins=['https://cloudoptima.vercel.app', 'http://localhost:5500', '*'])

# Simple test route (no DB)
@app.route('/simple-test')
def simple_test():
    return {"status": "ok", "message": "Simple test working"}

# Health check with DB status
@app.route('/health')
def health_check():
    # Test database connection
    db_status = "connected"
    db_error = None
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            db_status = "disconnected"
            db_error = "Connection failed"
        else:
            # Test query
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
    except Exception as e:
        db_status = "error"
        db_error = str(e)
    finally:
        if conn:
            conn.close()
    
    return jsonify({
        'status': 'healthy', 
        'service': 'CloudOptima API',
        'database': {
            'status': db_status,
            'error': db_error
        },
        'environment': os.getenv('FLASK_ENV', 'production')
    })

# Register blueprints
app.register_blueprint(aws_bp, url_prefix='/api/aws')
app.register_blueprint(alert_bp, url_prefix='/api/alert')
app.register_blueprint(test_bp)
app.register_blueprint(simulated_bp, url_prefix='/api/simulated')

@app.route('/')
def home():
    return jsonify({
        'status': 'CloudOptima API Running',
        'endpoints': [
            '/simple-test',
            '/health',
            '/api/aws/*',
            '/api/alert/*',
            '/api/simulated/*',
            '/api/user/settings'
        ]
    })

@app.route('/api/user/settings', methods=['POST'])
def save_user_settings():
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    
    try:
        # Check if settings exist
        cursor.execute("SELECT * FROM alerts WHERE user_id = %s", (data['userId'],))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE alerts 
                SET alert_email = %s, frequency = %s, enabled = %s 
                WHERE user_id = %s
            """, (data['alertEmail'], data['scanFrequency'], data['alertOnIdle'], data['userId']))
        else:
            cursor.execute("""
                INSERT INTO alerts (user_id, alert_email, frequency, enabled)
                VALUES (%s, %s, %s, %s)
            """, (data['userId'], data['alertEmail'], data['scanFrequency'], data['alertOnIdle']))
        
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/user/settings', methods=['GET'])
def get_user_settings():
    user_id = request.args.get('userId')
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM alerts WHERE user_id = %s", (user_id,))
        settings = cursor.fetchone()
        return jsonify(settings or {})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# Error handler
@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'details': str(error)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    port = int(os.getenv('PORT', 5000))
    print(f"Starting CloudOptima API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)