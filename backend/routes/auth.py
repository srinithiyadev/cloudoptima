from flask import Blueprint, request, jsonify
import jwt
import datetime
import os

auth_bp = Blueprint('auth', __name__)

# Mock users for testing (remove this when you add database)
mock_users = {
    'demo@cloudoptima.com': {
        'password': 'demo123',
        'name': 'Demo User',
        'id': 1
    }
}

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        # Check mock user
        if email in mock_users and mock_users[email]['password'] == password:
            # Generate token
            token = jwt.encode({
                'user_id': mock_users[email]['id'],
                'email': email,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
            }, os.environ.get('SECRET_KEY', 'dev-secret-key'), algorithm='HS256')
            
            return jsonify({
                'token': token,
                'user': {
                    'id': mock_users[email]['id'],
                    'name': mock_users[email]['name'],
                    'email': email
                }
            }), 200
        
        return jsonify({'message': 'Invalid credentials'}), 401
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        # Check if user exists
        if email in mock_users:
            return jsonify({'message': 'Email already registered'}), 400
        
        # Add mock user (replace with database later)
        mock_users[email] = {
            'password': password,
            'name': name,
            'id': len(mock_users) + 1
        }
        
        return jsonify({'message': 'User created successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/test', methods=['GET'])
def test():
    return jsonify({'message': 'Auth routes working!'})