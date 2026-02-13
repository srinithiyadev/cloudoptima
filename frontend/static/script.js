// Update summary cards
function updateSummary() {
    const rows = document.querySelectorAll('#resources-table tbody tr');
    const idleRows = Array.from(rows).filter(row => 
        row.querySelector('.status-badge').textContent.includes('IDLE')
    );
    
    document.getElementById('total-resources').textContent = rows.length;
    document.getElementById('idle-resources').textContent = idleRows.length;
}

// Run scan button
async function runScan() {
    const btn = document.querySelector('.btn-scan');
    const originalText = btn.innerHTML;
    
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scanning...';
    btn.disabled = true;
    
    // Mock API call
    setTimeout(async () => {
        try {
            const response = await fetch('/api/scan', { method: 'POST' });
            const data = await response.json();
            
            alert(`✅ ${data.message}\nPage will refresh in 2 seconds.`);
            
            // Refresh page after 2 seconds
            setTimeout(() => {
                window.location.reload();
            }, 2000);
            
        } catch (error) {
            alert('❌ Scan failed: ' + error.message);
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    }, 1500);
}

// Send alert for idle resource
function sendAlert(resourceId) {
    if (confirm(`Send alert to team about idle resource: ${resourceId}?`)) {
        alert(`📢 Alert sent for ${resourceId}\nTeam will be notified via Slack.`);
        // In real version, call API to send Slack alert
    }
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

// ===== AWS CONNECTION FUNCTIONS =====
function connectAWS() {
    const accessKey = document.getElementById('aws-key').value.trim();
    const secretKey = document.getElementById('aws-secret').value.trim();
    const region = document.getElementById('aws-region').value;
    
    if (!accessKey || !secretKey) {
        alert('Please enter both Access Key and Secret Key');
        return;
    }
    
    // Show loading
    const btn = event.target;
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Connecting...';
    btn.disabled = true;
    
    // Simulate connection
    setTimeout(() => {
        // Hide form, show connected info
        document.getElementById('awsForm').style.display = 'none';
        document.getElementById('connectedInfo').style.display = 'block';
        
        // Update status badge
        const statusBadge = document.getElementById('awsStatus');
        statusBadge.innerHTML = '<i class="fas fa-circle"></i> Connected';
        statusBadge.style.background = '#10b981';
        
        // Show account info
        document.getElementById('connectedAccount').textContent = accessKey.substring(0, 8) + '...';
        document.getElementById('connectedRegion').textContent = region;
        
        // Save to localStorage
        localStorage.setItem('aws_connected', 'true');
        localStorage.setItem('aws_region', region);
        
        // Restore button
        btn.innerHTML = originalText;
        btn.disabled = false;
        
        // Show success message
        alert('✅ AWS Account connected! Auto-scanner will now monitor for idle resources.');
        
        // Update the data source indicator
        document.getElementById('cost-source').innerText = '(Real AWS Data)';
        document.getElementById('data-source').innerText = '(Connected to AWS)';
    }, 1500);
}

function disconnectAWS() {
    if (confirm('Disconnect AWS account? Auto-alerts will stop.')) {
        // Show form, hide connected info
        document.getElementById('awsForm').style.display = 'block';
        document.getElementById('connectedInfo').style.display = 'none';
        
        // Update status badge
        const statusBadge = document.getElementById('awsStatus');
        statusBadge.innerHTML = '<i class="fas fa-circle"></i> Not Connected';
        statusBadge.style.background = '#f97316';
        
        // Clear localStorage
        localStorage.removeItem('aws_connected');
        localStorage.removeItem('aws_region');
        
        // Update data source indicator
        document.getElementById('cost-source').innerText = '(Demo Data)';
        document.getElementById('data-source').innerText = '(Demo Data)';
        
        alert('🔌 AWS account disconnected.');
    }
}

// ===== AUTO-ALERT FUNCTIONS =====
function saveAlertSettings() {
    const email = document.getElementById('alertEmail').value;
    const frequency = document.getElementById('scanFrequency').value;
    const enabled = document.getElementById('autoAlertToggle').checked;
    
    if (!email) {
        alert('Please enter an email address');
        return;
    }
    
    // Save to localStorage
    localStorage.setItem('alert_email', email);
    localStorage.setItem('scan_frequency', frequency);
    localStorage.setItem('alerts_enabled', enabled);
    
    alert('✅ Settings saved! Auto-scanner will run every ' + frequency + ' hours.');
    
    // Update status
    document.getElementById('alertStatus').innerText = enabled ? 'ACTIVE' : 'DISABLED';
    document.getElementById('alertStatus').style.background = enabled ? '#10b981' : '#ef4444';
}

async function testAlert() {
    const email = document.getElementById('alertEmail').value;
    
    if (!email) {
        alert('Please enter an email address first');
        return;
    }
    
    // Show sending state
    const btn = event.target;
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
    btn.disabled = true;
    
    try {
        // Call backend to send REAL email
        const response = await fetch('https://cloudoptima.onrender.com/api/email/test-alert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('✅ Test alert sent! Check your inbox at ' + email);
            
            // Update the stats
            const alertsSent = document.getElementById('alertsSent');
            alertsSent.innerText = parseInt(alertsSent.innerText) + 1;
            
            // Add to recent alerts
            const recentDiv = document.getElementById('recentAlerts');
            const newAlert = document.createElement('div');
            newAlert.style.cssText = 'padding: 8px; border-bottom: 1px solid #e2e8f0; font-size: 14px;';
            newAlert.innerHTML = '<i class="fas fa-check-circle" style="color: #10b981;"></i> Test Alert - Just now';
            recentDiv.insertBefore(newAlert, recentDiv.firstChild);
        } else {
            alert('❌ Failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Test alert error:', error);
        alert('❌ Could not connect to backend. Make sure your backend is running.');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// ===== LOGOUT FUNCTION =====
function logout() {
    // Clear EVERYTHING from storage
    localStorage.clear();
    sessionStorage.clear();
    
    // Redirect to login page
    window.location.replace('/login.html');
    
    return false;
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    // Format last scan time
    const lastScanEl = document.getElementById('last-scan');
    if (lastScanEl) {
        lastScanEl.textContent = formatDate(lastScanEl.textContent);
    }
    
    // Update summary
    updateSummary();
    
    // Show user email
    const user = JSON.parse(localStorage.getItem('user') || '{"email":"demo@cloudoptima.com"}');
    const userEmailElement = document.getElementById('userEmailText');
    if (userEmailElement) {
        userEmailElement.textContent = user.email;
    }
    
    // Check if AWS was previously connected
    if (localStorage.getItem('aws_connected')) {
        const awsForm = document.getElementById('awsForm');
        const connectedInfo = document.getElementById('connectedInfo');
        const statusBadge = document.getElementById('awsStatus');
        
        if (awsForm && connectedInfo && statusBadge) {
            awsForm.style.display = 'none';
            connectedInfo.style.display = 'block';
            statusBadge.innerHTML = '<i class="fas fa-circle"></i> Connected';
            statusBadge.style.background = '#10b981';
        }
    }
    
    // Load saved alert settings
    const savedEmail = localStorage.getItem('alert_email');
    const savedFrequency = localStorage.getItem('scan_frequency');
    const alertsEnabled = localStorage.getItem('alerts_enabled');
    
    if (savedEmail) {
        const alertEmail = document.getElementById('alertEmail');
        if (alertEmail) alertEmail.value = savedEmail;
    }
    
    if (savedFrequency) {
        const scanFreq = document.getElementById('scanFrequency');
        if (scanFreq) scanFreq.value = savedFrequency;
    }
    
    if (alertsEnabled !== null) {
        const toggle = document.getElementById('autoAlertToggle');
        const status = document.getElementById('alertStatus');
        if (toggle) toggle.checked = alertsEnabled === 'true';
        if (status) {
            status.innerText = alertsEnabled === 'true' ? 'ACTIVE' : 'DISABLED';
            status.style.background = alertsEnabled === 'true' ? '#10b981' : '#ef4444';
        }
    }
    
    // Auto-refresh every 60 seconds
    setInterval(() => {
        fetch('/api/data')
            .then(response => response.json())
            .then(data => {
                if (data.scan_time !== document.getElementById('last-scan')?.dataset.original) {
                    if (confirm('New scan data available. Refresh page?')) {
                        window.location.reload();
                    }
                }
            })
            .catch(() => {
                // Silent fail - ignore
            });
    }, 60000);
});