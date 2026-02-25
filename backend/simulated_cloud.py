from flask import Blueprint, jsonify
import random
from datetime import datetime, timedelta

simulated_bp = Blueprint('simulated', __name__)

@simulated_bp.route('/api/azure/resources')
def get_azure_resources():
    # Simulated Azure VM data
    vms = []
    for i in range(1, 6):
        vms.append({
            'id': f'azure-vm-{i}',
            'name': f'azure-vm-{i}',
            'status': random.choice(['running', 'stopped', 'idle']),
            'size': random.choice(['Standard_B1s', 'Standard_D2s_v3', 'Standard_F4s']),
            'location': random.choice(['eastus', 'westus', 'europe', 'asia']),
            'cost_per_hour': round(random.uniform(0.02, 0.50), 3),
            'idle_hours': random.randint(0, 720) if random.random() > 0.5 else 0
        })
    return jsonify(vms)

@simulated_bp.route('/api/gcp/resources')
def get_gcp_resources():
    # Simulated GCP VM data
    vms = []
    for i in range(1, 5):
        vms.append({
            'id': f'gcp-vm-{i}',
            'name': f'gcp-instance-{i}',
            'status': random.choice(['RUNNING', 'STOPPED', 'TERMINATED']),
            'machine_type': random.choice(['n1-standard-1', 'e2-medium', 'f1-micro']),
            'zone': random.choice(['us-central1', 'europe-west1', 'asia-east1']),
            'cost_per_hour': round(random.uniform(0.01, 0.40), 3),
            'idle_hours': random.randint(0, 500) if random.random() > 0.4 else 0
        })
    return jsonify(vms)

@simulated_bp.route('/api/cloud/all')
def get_all_cloud_resources():
    # Combine AWS (real) + Azure (simulated) + GCP (simulated)
    from aws_api import get_aws_resources  # Import your real AWS function
    
    aws_data = get_aws_resources()  # Your real AWS function
    azure_data = get_azure_resources().__dict__  # Simulated
    gcp_data = get_gcp_resources().__dict__  # Simulated
    
    return jsonify({
        'aws': aws_data,
        'azure': azure_data,
        'gcp': gcp_data,
        'total_estimated_savings': random.randint(500, 5000)
    })

@simulated_bp.route('/api/cloud/add', methods=['POST'])
def add_cloud_provider():
    # For user to add their own cloud credentials
    data = request.json
    # Store in database
    return jsonify({'success': True, 'message': f"{data['provider']} added successfully"})