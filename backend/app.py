from flask import Flask, jsonify
from flask_cors import CORS
from alert import alert_bp
from aws_api import aws_bp
from routes.test_email import test_bp  # ← ADD THIS IMPORT
import os


# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'CloudOptima2026!',  # Use your password
    'database': 'cloudoptima'
}

def get_db_connection():
    try:
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

app = Flask(__name__)
CORS(app, origins=['https://cloudoptima.vercel.app', 'http://localhost:5500'])


# Register blueprints
app.register_blueprint(aws_bp, url_prefix='/api/aws')
app.register_blueprint(alert_bp, url_prefix='/api/alert')
app.register_blueprint(test_bp)  # ← ADD THIS REGISTRATION

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'CloudOptima API'})
@app.route('/api/user/settings', methods=['POST'])
def save_user_settings():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
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
    conn.close()
    return jsonify({'success': True})

@app.route('/api/user/settings', methods=['GET'])
def get_user_settings():
    user_id = request.args.get('userId')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alerts WHERE user_id = %s", (user_id,))
    settings = cursor.fetchone()
    conn.close()
    return jsonify(settings or {})

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
