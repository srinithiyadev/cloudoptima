from flask import Flask, jsonify, request
from flask_cors import CORS
from alert import alert_bp
from aws_api import aws_bp
from routes.test_email import test_bp
from simulated_cloud import simulated_bp
import os
import psycopg2
import psycopg2.extras
import sys
import traceback
from datetime import datetime

# Database connection using single URL
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        traceback.print_exc()
        return None

app = Flask(__name__)
CORS(app, origins=['https://cloudoptima.vercel.app', 'http://localhost:5500', 'http://127.0.0.1:5500', 'https://cloudoptima-api-python.onrender.com'])

# Simple test route (no DB)
@app.route('/simple-test')
def simple_test():
    return {"status": "ok", "message": "Simple test working"}

# Health check with DB status
@app.route('/health')
def health_check():
    db_status = "connected"
    db_error = None
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            db_status = "disconnected"
            db_error = "Connection failed"
        else:
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

# ========== AUTH ENDPOINTS ==========
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    try:
        # Check if user exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (data['email'],))
        if cursor.fetchone():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Insert new user
        cursor.execute("""
            INSERT INTO users (name, email, password, created_at) 
            VALUES (%s, %s, %s, NOW())
        """, (data['name'], data['email'], data['password']))
        conn.commit()
        
        return jsonify({
            'success': True,
            'user': {
                'id': cursor.lastrowid,
                'email': data['email'],
                'name': data['name']
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", 
                      (data['email'], data['password']))
        user = cursor.fetchone()
        
        if user:
            return jsonify({
                'success': True,
                'user': {
                    'email': user['email'],
                    'name': user.get('name', user['email'].split('@')[0]),
                    'id': user['id']
                },
                'token': 'dummy-jwt-token'
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/auth/verify', methods=['POST'])
def verify_auth():
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({'valid': False, 'error': 'Database offline'}), 503
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (data['email'],))
        user = cursor.fetchone()
        
        if user:
            return jsonify({'valid': True, 'email': data['email']})
        return jsonify({'valid': False}), 401
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    return jsonify({'success': True})

@app.route('/api/user/delete', methods=['POST'])
def delete_user():
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM alerts WHERE user_id IN (SELECT id FROM users WHERE email = %s)", (data['email'],))
        cursor.execute("DELETE FROM users WHERE email = %s", (data['email'],))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# ========== SETTINGS ENDPOINTS ==========
@app.route('/api/user/settings', methods=['POST'])
def save_user_settings():
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE email = %s", (data['userId'],))
        user = cursor.fetchone()
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        user_id = user['id']
        
        cursor.execute("SELECT * FROM alerts WHERE user_id = %s", (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE alerts 
                SET alert_email = %s, frequency = %s, enabled = %s,
                    alert_sensitivity = %s, weekly_report = %s, anomaly_alerts = %s,
                    idle_threshold = %s, cpu_threshold = %s, ignore_tagged = %s,
                    monthly_budget = %s, budget_alert = %s, auto_stop = %s,
                    show_costs = %s, slack_url = %s, teams_url = %s,
                    full_name = %s, organization = %s
                WHERE user_id = %s
            """, (
                data.get('alertEmail'), data.get('scanFrequency'), data.get('alertOnIdle'),
                data.get('alertSensitivity'), data.get('weeklyReport'), data.get('anomalyAlerts'),
                data.get('idleThreshold'), data.get('cpuThreshold'), data.get('ignoreTagged'),
                data.get('monthlyBudget'), data.get('budgetAlert'), data.get('autoStop'),
                data.get('showCosts'), data.get('slackUrl'), data.get('teamsUrl'),
                data.get('fullName'), data.get('organization'), user_id
            ))
        else:
            cursor.execute("""
                INSERT INTO alerts (
                    user_id, alert_email, frequency, enabled, alert_sensitivity,
                    weekly_report, anomaly_alerts, idle_threshold, cpu_threshold,
                    ignore_tagged, monthly_budget, budget_alert, auto_stop,
                    show_costs, slack_url, teams_url, full_name, organization
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                data.get('alertEmail'), data.get('scanFrequency'), data.get('alertOnIdle'),
                data.get('alertSensitivity'), data.get('weeklyReport'), data.get('anomalyAlerts'),
                data.get('idleThreshold'), data.get('cpuThreshold'), data.get('ignoreTagged'),
                data.get('monthlyBudget'), data.get('budgetAlert'), data.get('autoStop'),
                data.get('showCosts'), data.get('slackUrl'), data.get('teamsUrl'),
                data.get('fullName'), data.get('organization')
            ))
        
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
        cursor.execute("SELECT id FROM users WHERE email = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        cursor.execute("SELECT * FROM alerts WHERE user_id = %s", (user['id'],))
        settings = cursor.fetchone()
        
        if settings:
            return jsonify({
                'alertEmail': settings.get('alert_email'),
                'scanFrequency': settings.get('frequency'),
                'alertOnIdle': settings.get('enabled'),
                'alertSensitivity': settings.get('alert_sensitivity'),
                'weeklyReport': settings.get('weekly_report'),
                'anomalyAlerts': settings.get('anomaly_alerts'),
                'idleThreshold': settings.get('idle_threshold'),
                'cpuThreshold': settings.get('cpu_threshold'),
                'ignoreTagged': settings.get('ignore_tagged'),
                'monthlyBudget': settings.get('monthly_budget'),
                'budgetAlert': settings.get('budget_alert'),
                'autoStop': settings.get('auto_stop'),
                'showCosts': settings.get('show_costs'),
                'slackUrl': settings.get('slack_url'),
                'teamsUrl': settings.get('teams_url'),
                'fullName': settings.get('full_name'),
                'organization': settings.get('organization')
            })
        return jsonify({})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# ========== ADMIN ENDPOINTS ==========
@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                u.id, 
                u.email, 
                u.name, 
                u.created_at,
                COUNT(a.id) as settings_count,
                (
                    SELECT COUNT(*) 
                    FROM alerts 
                    WHERE user_id = u.id AND enabled = true
                ) as active_alerts
            FROM users u
            LEFT JOIN alerts a ON u.id = a.user_id
            GROUP BY u.id
            ORDER BY u.created_at DESC
        """)
        users = cursor.fetchall()
        
        for user in users:
            cursor.execute("""
                SELECT created_at as login_time
                FROM user_activity
                WHERE user_id = %s AND activity_type = 'login'
                ORDER BY created_at DESC
                LIMIT 5
            """, (user['id'],))
            user['recent_logins'] = cursor.fetchall()
        
        return jsonify({
            'users': users,
            'total': len(users),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/admin/user/<int:user_id>', methods=['GET'])
def get_user_details(user_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, email, name, created_at
            FROM users
            WHERE id = %s
        """, (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        cursor.execute("SELECT * FROM alerts WHERE user_id = %s", (user_id,))
        user['settings'] = cursor.fetchone()
        
        cursor.execute("""
            SELECT created_at as login_time
            FROM user_activity
            WHERE user_id = %s AND activity_type = 'login'
            ORDER BY created_at DESC
            LIMIT 20
        """, (user_id,))
        user['login_history'] = cursor.fetchall()
        
        return jsonify(user)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/admin/stats', methods=['GET'])
def get_admin_stats():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) as total FROM users")
        total_users = cursor.fetchone()['total']
        
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM users 
            WHERE DATE(created_at) = CURRENT_DATE
        """)
        new_today = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) as count
            FROM user_activity
            WHERE activity_type = 'login'
            AND created_at >= NOW() - INTERVAL '7 days'
        """)
        active_7d = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) as count
            FROM alerts
            WHERE enabled = true
        """)
        alerts_enabled = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as login_count
            FROM user_activity
            WHERE activity_type = 'login'
            AND created_at >= NOW() - INTERVAL '30 days'
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """)
        login_activity = cursor.fetchall()
        
        return jsonify({
            'total_users': total_users,
            'new_users_today': new_today or 0,
            'active_users_last_7d': active_7d or 0,
            'users_with_alerts': alerts_enabled or 0,
            'login_activity': login_activity,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/track/login', methods=['POST'])
def track_login():
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE email = %s", (data['email'],))
        user = cursor.fetchone()
        
        if user:
            cursor.execute("""
                INSERT INTO user_activity (user_id, activity_type, ip_address, user_agent, created_at)
                VALUES (%s, 'login', %s, %s, NOW())
            """, (user['id'], request.remote_addr, request.headers.get('User-Agent')))
            conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

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
            '/api/auth/signup',
            '/api/auth/login',
            '/api/auth/verify',
            '/api/auth/logout',
            '/api/user/delete',
            '/api/user/settings',
            '/api/admin/users',
            '/api/admin/user/<id>',
            '/api/admin/stats',
            '/api/aws/*',
            '/api/alert/*',
            '/api/simulated/*'
        ]
    })

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