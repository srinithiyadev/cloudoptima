from flask import Blueprint, jsonify
import random
from datetime import datetime, timedelta
import time

simulated_bp = Blueprint('simulated', __name__)

# ========== AZURE SIMULATED DATA ==========
@simulated_bp.route('/api/simulated/azure/resources')
def get_azure_resources():
    """Simulated Azure VM data matching real API format"""
    
    azure_regions = ['eastus', 'westus', 'northeurope', 'southeastasia', 'japaneast']
    vm_sizes = [
        'Standard_D2s_v3', 'Standard_B2s', 'Standard_F4s', 
        'Standard_E2s_v3', 'Standard_D4s_v4', 'Standard_B1s'
    ]
    statuses = ['running', 'stopped', 'deallocated', 'running', 'running']  # Weighted to running
    
    resources = []
    for i in range(1, 9):  # 8 simulated Azure VMs
        status = random.choice(statuses)
        running_hours = random.randint(0, 720) if status == 'running' else 0
        idle_hours = random.randint(0, 300) if status == 'running' and random.random() > 0.6 else 0
        
        vm = {
            'id': f'/subscriptions/1234-5678-9012-3456/resourceGroups/rg-{random.choice(["prod","dev","test"])}/providers/Microsoft.Compute/virtualMachines/azure-vm-{i}',
            'name': f'vm-{random.choice(["web","api","db","cache"])}-{random.randint(1,999)}',
            'location': random.choice(azure_regions),
            'resourceGroup': f'rg-{random.choice(["production","development","testing"])}',
            'properties': {
                'hardwareProfile': {'vmSize': random.choice(vm_sizes)},
                'storageProfile': {
                    'osDisk': {'name': f'disk-{i}', 'diskSizeGB': random.choice([30, 64, 128])}
                },
                'osProfile': {'computerName': f'vm{i}', 'adminUsername': 'azureuser'},
                'statuses': [{'code': f'PowerState/{status}', 'level': 'Info'}]
            },
            'tags': {
                'environment': random.choice(['prod', 'dev', 'test']),
                'cost-center': f'cc-{random.randint(100,999)}',
                'owner': random.choice(['team-alpha', 'team-beta', 'team-gamma'])
            },
            'cost': {
                'perHour': round(random.uniform(0.08, 0.65), 3),
                'monthly': round(random.uniform(50, 450), 2),
                'currency': 'USD'
            },
            'metrics': {
                'cpu_utilization': random.randint(0, 95),
                'memory_utilization': random.randint(0, 90),
                'disk_read_bytes': random.randint(1000000, 1000000000),
                'network_in_bytes': random.randint(1000000, 5000000000)
            },
            'idle_detected': idle_hours > 100,
            'idle_hours': idle_hours,
            'potential_savings': round(idle_hours * random.uniform(0.08, 0.20), 2) if idle_hours > 0 else 0
        }
        resources.append(vm)
    
    return jsonify({
        'value': resources,
        'count': len(resources),
        'nextLink': None,
        'simulated': True,
        'timestamp': datetime.now().isoformat()
    })

@simulated_bp.route('/api/simulated/azure/usage')
def get_azure_usage():
    """Simulated Azure billing data"""
    return jsonify({
        'usage': [
            {'meter': 'Virtual Machines', 'quantity': random.randint(100, 500), 'cost': round(random.uniform(50, 300), 2)},
            {'meter': 'Storage', 'quantity': random.randint(500, 2000), 'cost': round(random.uniform(20, 150), 2)},
            {'meter': 'Bandwidth', 'quantity': random.randint(10, 200), 'cost': round(random.uniform(5, 80), 2)}
        ],
        'total': round(random.uniform(100, 600), 2),
        'currency': 'USD',
        'period': 'Monthly'
    })

# ========== GCP SIMULATED DATA ==========
@simulated_bp.route('/api/simulated/gcp/resources')
def get_gcp_resources():
    """Simulated GCP Compute Engine instances"""
    
    gcp_zones = ['us-central1-a', 'us-central1-b', 'europe-west1-b', 'asia-east1-a', 'asia-southeast1-b']
    machine_types = ['n1-standard-1', 'n1-standard-2', 'e2-medium', 'f1-micro', 'c2-standard-4', 'n2-standard-4']
    statuses = ['RUNNING', 'STOPPED', 'TERMINATED', 'RUNNING', 'RUNNING']
    
    resources = []
    for i in range(1, 7):  # 6 simulated GCP instances
        status = random.choice(statuses)
        running_hours = random.randint(0, 720) if status == 'RUNNING' else 0
        idle_hours = random.randint(0, 250) if status == 'RUNNING' and random.random() > 0.55 else 0
        
        instance = {
            'id': f'{random.randint(1000000000, 9999999999)}',
            'name': f'instance-{random.choice(["web","app","db","worker"])}-{random.randint(1,999)}',
            'zone': f'projects/cloudoptima/zones/{random.choice(gcp_zones)}',
            'machineType': f'zones/{random.choice(gcp_zones)}/machineTypes/{random.choice(machine_types)}',
            'status': status,
            'creationTimestamp': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
            'labels': {
                'environment': random.choice(['prod', 'dev', 'test']),
                'team': random.choice(['backend', 'frontend', 'data', 'ml']),
                'managed-by': 'terraform'
            },
            'tags': {
                'items': [random.choice(['http-server', 'https-server', 'ssh'])]
            },
            'networkInterfaces': [{
                'network': 'global/networks/default',
                'networkIP': f'10.128.0.{random.randint(2, 255)}',
                'accessConfigs': [{'name': 'external-nat', 'natIP': f'{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}'}]
            }],
            'disks': [{
                'type': 'PERSISTENT',
                'boot': True,
                'diskSizeGb': random.choice([20, 50, 100, 200])
            }],
            'cpuPlatform': random.choice(['Intel Broadwell', 'Intel Skylake', 'AMD Rome', 'Intel Cascade Lake']),
            'cost': {
                'perHour': round(random.uniform(0.05, 0.55), 3),
                'monthly': round(random.uniform(35, 380), 2),
                'currency': 'USD'
            },
            'metrics': {
                'cpu_usage_percent': random.randint(0, 98),
                'memory_usage_percent': random.randint(0, 92),
                'disk_usage_bytes': random.randint(1000000000, 50000000000)
            },
            'idle_detected': idle_hours > 80,
            'idle_hours': idle_hours,
            'recommended_action': random.choice(['none', 'resize', 'stop', 'delete']) if idle_hours > 80 else 'none',
            'potential_savings': round(idle_hours * random.uniform(0.05, 0.15), 2) if idle_hours > 0 else 0
        }
        resources.append(instance)
    
    return jsonify({
        'items': resources,
        'total_items': len(resources),
        'kind': 'compute#instanceList',
        'simulated': True,
        'timestamp': datetime.now().isoformat()
    })

@simulated_bp.route('/api/simulated/gcp/billing')
def get_gcp_billing():
    """Simulated GCP billing data"""
    return jsonify({
        'billing_account': 'cloudoptima-billing',
        'costs': [
            {'service': 'Compute Engine', 'cost': round(random.uniform(100, 400), 2)},
            {'service': 'Cloud Storage', 'cost': round(random.uniform(20, 150), 2)},
            {'service': 'Cloud SQL', 'cost': round(random.uniform(30, 200), 2)},
            {'service': 'Networking', 'cost': round(random.uniform(10, 80), 2)}
        ],
        'total': round(random.uniform(200, 700), 2),
        'currency': 'USD',
        'forecast': round(random.uniform(250, 750), 2)
    })

# ========== MULTI-CLOUD AGGREGATION ==========
@simulated_bp.route('/api/simulated/cloud/all')
def get_all_cloud_resources():
    """Combined view of all cloud providers"""
    
    # Fetch simulated data
    azure_data = get_azure_resources().json
    gcp_data = get_gcp_resources().json
    
    # Calculate totals
    total_vms = len(azure_data.get('value', [])) + len(gcp_data.get('items', []))
    total_cost = sum(vm.get('cost', {}).get('monthly', 0) for vm in azure_data.get('value', [])) + \
                 sum(instance.get('cost', {}).get('monthly', 0) for instance in gcp_data.get('items', []))
    
    idle_resources = []
    for vm in azure_data.get('value', []):
        if vm.get('idle_detected'):
            idle_resources.append({
                'cloud': 'Azure',
                'name': vm['name'],
                'idle_hours': vm['idle_hours'],
                'savings': vm['potential_savings']
            })
    
    for instance in gcp_data.get('items', []):
        if instance.get('idle_detected'):
            idle_resources.append({
                'cloud': 'GCP',
                'name': instance['name'],
                'idle_hours': instance['idle_hours'],
                'savings': instance['potential_savings']
            })
    
    return jsonify({
        'providers': {
            'azure': {
                'resources': azure_data.get('value', []),
                'count': len(azure_data.get('value', [])),
                'total_cost': sum(vm.get('cost', {}).get('monthly', 0) for vm in azure_data.get('value', []))
            },
            'gcp': {
                'resources': gcp_data.get('items', []),
                'count': len(gcp_data.get('items', [])),
                'total_cost': sum(instance.get('cost', {}).get('monthly', 0) for instance in gcp_data.get('items', []))
            }
        },
        'summary': {
            'total_vms': total_vms,
            'total_monthly_cost': round(total_cost, 2),
            'idle_resources': len(idle_resources),
            'potential_savings': sum(r['savings'] for r in idle_resources),
            'idle_breakdown': idle_resources[:5]  # Top 5 idle resources
        },
        'timestamp': datetime.now().isoformat(),
        'simulated': True
    })

# ========== COST OPTIMIZATION RECOMMENDATIONS ==========
@simulated_bp.route('/api/simulated/recommendations')
def get_optimization_recommendations():
    """AI-powered cost optimization suggestions"""
    
    recommendations = [
        {
            'cloud': 'Azure',
            'resource': 'vm-web-prod-234',
            'type': 'Right-sizing',
            'current': 'Standard_D4s_v4',
            'recommended': 'Standard_D2s_v4',
            'savings': 45.20,
            'confidence': 'high',
            'reason': 'CPU utilization below 15% for 30 days'
        },
        {
            'cloud': 'GCP',
            'resource': 'instance-app-567',
            'type': 'Idle instance',
            'action': 'Stop',
            'savings': 78.50,
            'confidence': 'high',
            'reason': 'No network activity for 14 days'
        },
        {
            'cloud': 'Azure',
            'resource': 'rg-production',
            'type': 'Reserved Instance',
            'recommended': '3-year savings plan',
            'savings': 320.00,
            'confidence': 'medium',
            'reason': 'Consistent usage pattern detected'
        },
        {
            'cloud': 'GCP',
            'resource': 'cloud-sql-instance',
            'type': 'Committed use discount',
            'recommended': '1-year commitment',
            'savings': 156.30,
            'confidence': 'high',
            'reason': 'Database running 24/7 for 6 months'
        }
    ]
    
    return jsonify({
        'recommendations': recommendations,
        'total_potential_savings': sum(r['savings'] for r in recommendations),
        'currency': 'USD',
        'generated': datetime.now().isoformat()
    })