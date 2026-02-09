import boto3
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
import os

aws_bp = Blueprint('aws', __name__)

# AWS Cost Data
@aws_bp.route('/cost', methods=['POST'])
def get_cost():
    try:
        data = request.json
        access_key = data.get('accessKeyId') or os.getenv('AWS_ACCESS_KEY_ID')
        secret_key = data.get('secretAccessKey') or os.getenv('AWS_SECRET_ACCESS_KEY')
        
        client = boto3.client('ce',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='us-east-1'
        )
        
        # Last 30 days for better data
        end = datetime.now()
        start = end - timedelta(days=30)
        
        response = client.get_cost_and_usage(
            TimePeriod={
                'Start': start.strftime('%Y-%m-%d'),
                'End': end.strftime('%Y-%m-%d')
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'SERVICE'}
            ]
        )
        
        # Format response for frontend
        formatted = {
            'total_cost': '0',
            'services': [],
            'daily_costs': [],
            'by_service': {}
        }
        
        # Process daily costs
        for day in response.get('ResultsByTime', []):
            date = day['TimePeriod']['Start']
            total = day.get('Total', {}).get('UnblendedCost', {}).get('Amount', '0')
            
            formatted['daily_costs'].append({
                'date': date,
                'cost': total
            })
            
            # Track services
            for group in day.get('Groups', []):
                service = group['Keys'][0]
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                
                if service not in formatted['by_service']:
                    formatted['by_service'][service] = 0
                formatted['by_service'][service] += cost
        
        # Convert service costs to list
        formatted['services'] = [
            {'service': service, 'cost': str(round(cost, 2))}
            for service, cost in formatted['by_service'].items() if cost > 0
        ]
        
        # Calculate total
        total = sum(float(day['cost']) for day in formatted['daily_costs'])
        formatted['total_cost'] = str(round(total, 2))
        
        return jsonify(formatted)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Idle EC2 Detection
@aws_bp.route('/instances', methods=['POST'])
def get_instances():
    try:
        data = request.json
        access_key = data.get('accessKeyId')
        secret_key = data.get('secretAccessKey')
        
        ec2 = boto3.client('ec2',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='us-east-1'
        )
        
        # Get all running instances
        instances = ec2.describe_instances(Filters=[
            {'Name': 'instance-state-name', 'Values': ['running']}
        ])
        
        idle_instances = []
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                # Simple idle detection: running >7 days
                launch_time = instance['LaunchTime']
                days_running = (datetime.now(launch_time.tzinfo) - launch_time).days
                
                if days_running > 7:
                    idle_instances.append({
                        'id': instance['InstanceId'],
                        'type': instance['InstanceType'],
                        'launched': launch_time.strftime('%Y-%m-%d'),
                        'days_running': days_running,
                        'name': next((tag['Value'] for tag in instance.get('Tags', []) 
                                    if tag['Key'] == 'Name'), 'No Name'),
                        'state': 'idle'
                    })
        
        return jsonify({
            'idle_instances': idle_instances,
            'total_instances': len(idle_instances),
            'estimated_savings': len(idle_instances) * 50  # $50/month per instance
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500