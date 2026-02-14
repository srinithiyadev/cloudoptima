from flask import Blueprint, request, jsonify
from models import db, User, UserSettings
import jwt
import datetime
import os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already registered'}), 400
        
        # Create user
        user = User(name=name, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.flush()  # Get user.id
        
        # Create default settings
        settings = UserSettings(
            user_id=user.id,
            alert_email=email,
            scan_frequency=6,
            auto_scan_enabled=True
        )
        db.session.add(settings)
        db.session.commit()
        
        return jsonify({'message': 'User created successfully'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user.id,
            'email': user.email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }, os.environ.get('SECRET_KEY', 'dev-secret-key'), algorithm='HS256')
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
