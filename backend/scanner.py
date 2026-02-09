# scanner.py
import json
import random
from datetime import datetime

def mock_scan():
    """Simulate cloud scanning"""
    resources = []
    
    for i in range(5):
        is_idle = random.choice([True, False])
        resources.append({
            "id": f"i-{random.randint(10000, 99999)}",
            "name": f"{random.choice(['Web', 'API', 'DB', 'Cache', 'App'])}-Server",
            "cloud": random.choice(["aws", "azure", "gcp"]),
            "status": "idle" if is_idle else "active",
            "cpu": f"{random.randint(1, 5) if is_idle else random.randint(60, 95)}%",
            "cost": f"${random.randint(15, 150)}/month",
            "region": random.choice(["us-east-1", "us-west-2", "eastus", "westeurope"])
        })
    
    idle_count = len([r for r in resources if r["status"] == "idle"])
    total_savings = sum(int(r["cost"][1:].split("/")[0]) for r in resources if r["status"] == "idle")
    
    data = {
        "scan_time": datetime.now().isoformat(),
        "resources": resources,
        "total_savings": f"${total_savings}/month",
        "idle_count": idle_count,
        "total_count": len(resources)
    }
    
    with open("data/scan_results.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Scan saved: {idle_count}/{len(resources)} idle")
    return data

if __name__ == "__main__":
    mock_scan()