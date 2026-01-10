import boto3
import json

print("🚀 CloudOptima Initialized")

# ADD REGION HERE
ec2 = boto3.client('ec2', region_name='us-east-1')  # ← Add this

response = ec2.describe_instances()

print(f"📦 Found {len(response['Reservations'])} EC2 reservations")
for res in response['Reservations']:
    for inst in res['Instations']:
        print(f"   Instance: {inst['InstanceId']} - {inst['State']['Name']}")

with open('data.json', 'w') as f:
    json.dump(response['Reservations'], f, default=str)
print("✅ Data saved to data.json")