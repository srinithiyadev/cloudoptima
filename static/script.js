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

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Format last scan time
    const lastScanEl = document.getElementById('last-scan');
    if (lastScanEl) {
        lastScanEl.textContent = formatDate(lastScanEl.textContent);
    }
    
    // Update summary
    updateSummary();
    
    // Auto-refresh every 60 seconds
    setInterval(() => {
        fetch('/api/data')
            .then(response => response.json())
            .then(data => {
                if (data.scan_time !== document.getElementById('last-scan').dataset.original) {
                    if (confirm('New scan data available. Refresh page?')) {
                        window.location.reload();
                    }
                }
            });
    }, 60000);
});