import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from app import app
    print("✅ App imported successfully")
except Exception as e:
    print(f"❌ Import error: {e}")
    # Create a simple Flask app for error handling
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    @app.route('/health')
    @app.route('/api/health')
    def error_handler():
        return jsonify({
            'error': 'Import failed',
            'details': str(e),
            'cwd': os.getcwd(),
            'files': os.listdir(os.path.dirname(__file__))
        })

# Vercel needs this
handler = app