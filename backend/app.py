from flask import Flask, jsonify
from flask_cors import CORS
from models import db, bcrypt
from routes.auth import auth_bp
from routes.test_email import test_bp
import os

app = Flask(__name__)
CORS(app)

# Database configuration
database_url = os.environ.get('DATABASE_URL', 'postgresql://localhost/cloudoptima')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(test_bp)

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'CloudOptima API'})

# Create tables
with app.app_context():
    db.create_all()
    print("✅ Database tables created!")

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
