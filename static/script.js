// [file name]: static/script.js
// [file content begin]
// Real-time job status updates
function updateJobStatuses() {
    fetch('/api/jobs/status')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                data.jobs.forEach(job => {
                    updateJobElement(job.job_id, job.status, job.status_class, job.estimated_start);
                });

                // Update last update time
                const lastUpdateElement = document.getElementById('last-update-time');
                if (lastUpdateElement && data.last_update) {
                    const updateTime = new Date(data.last_update);
                    lastUpdateElement.textContent = 'Last updated: ' + updateTime.toLocaleString();
                }
            }
        })
        .catch(error => console.error('Error updating job statuses:', error));
}

function updateJobElement(jobId, status, statusClass, estimatedStart) {
    const statusElement = document.querySelector(`tr[data-job-id="${jobId}"] .job-status`);
    if (statusElement) {
        statusElement.className = `badge bg-${statusClass} job-status`;
        statusElement.textContent = status;
    }

    const etaElement = document.querySelector(`tr[data-job-id="${jobId}"] .job-eta`);
    if (etaElement && estimatedStart) {
        etaElement.textContent = estimatedStart;
    }
}

// Backend status updates
function updateBackendStatuses() {
    fetch('/api/backends/status')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update backend status elements
                Object.entries(data.backends).forEach(([backendName, backendInfo]) => {
                    updateBackendElement(backendName, backendInfo);
                });

                // Update last update time
                const lastUpdateElement = document.getElementById('last-update-time');
                if (lastUpdateElement && data.last_update) {
                    const updateTime = new Date(data.last_update);
                    lastUpdateElement.textContent = 'Last updated: ' + updateTime.toLocaleString();
                }
            }
        })
        .catch(error => console.error('Error updating backend statuses:', error));
}

function updateBackendElement(backendName, backendInfo) {
    // Update backend status elements on various pages
    const elements = document.querySelectorAll(`[data-backend="${backendName}"]`);
    elements.forEach(element => {
        // Update status badge
        const statusBadge = element.querySelector('.backend-status');
        if (statusBadge) {
            const isOperational = backendInfo.operational;
            statusBadge.className = `badge bg-${isOperational ? 'success' : 'danger'} backend-status`;
            statusBadge.textContent = isOperational ? 'Operational' : 'Down';
        }

        // Update queue length
        const queueElement = element.querySelector('.backend-queue');
        if (queueElement) {
            queueElement.textContent = backendInfo.pending_jobs + ' jobs';
        }

        // Update progress bar
        const progressBar = element.querySelector('.progress-bar');
        if (progressBar) {
            const queueLength = backendInfo.pending_jobs;
            const width = Math.min(queueLength * 5, 100);
            progressBar.style.width = width + '%';
            progressBar.className = `progress-bar ${
                queueLength === 0 ? 'bg-success' :
                queueLength < 5 ? 'bg-info' :
                queueLength < 10 ? 'bg-warning' : 'bg-danger'
            }`;
        }
    });
}

// Job timeline viewer
function loadJobTimeline(jobId) {
    fetch(`/api/jobs/${jobId}/timeline`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderTimeline(data.timeline);
            }
        })
        .catch(error => console.error('Error loading job timeline:', error));
}

function renderTimeline(timeline) {
    const timelineContainer = document.getElementById('job-timeline');
    if (!timelineContainer) return;

    timelineContainer.innerHTML = timeline.map(event => `
        <div class="timeline-event">
            <div class="timeline-badge bg-${getEventBadgeClass(event.type)}">
                <i class="bi bi-${getEventIcon(event.type)}"></i>
            </div>
            <div class="timeline-content">
                <h6>${formatEventType(event.type)}</h6>
                <p>${new Date(event.timestamp).toLocaleString()}</p>
                ${event.data ? `<pre class="small">${JSON.stringify(event.data, null, 2)}</pre>` : ''}
            </div>
        </div>
    `).join('');
}

function getEventBadgeClass(eventType) {
    const mapping = {
        'status_change': 'info',
        'queued': 'warning',
        'running': 'primary',
        'completed': 'success',
        'failed': 'danger',
        'cancelled': 'secondary'
    };
    return mapping[eventType] || 'secondary';
}

function getEventIcon(eventType) {
    const mapping = {
        'status_change': 'arrow-repeat',
        'queued': 'clock',
        'running': 'play-circle',
        'completed': 'check-circle',
        'failed': 'exclamation-circle',
        'cancelled': 'x-circle'
    };
    return mapping[eventType] || 'circle';
}

function formatEventType(eventType) {
    return eventType.split('_').map(word =>
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

// Initialize real-time updates based on current page
document.addEventListener('DOMContentLoaded', function() {
    // Set up periodic updates based on current page
    const currentPath = window.location.pathname;

    if (currentPath === '/jobs' || currentPath === '/dashboard') {
        // Update every 30 seconds
        setInterval(updateJobStatuses, 30000);
        // Initial update
        setTimeout(updateJobStatuses, 1000);
    }

    if (currentPath === '/backends') {
        // Update every 30 seconds
        setInterval(updateBackendStatuses, 30000);
        // Initial update
        setTimeout(updateBackendStatuses, 1000);
    }

    // Load timeline if on job details page
    if (currentPath.startsWith('/jobs/') && currentPath.split('/').length === 3) {
        const jobId = currentPath.split('/')[2];
        loadJobTimeline(jobId);
    }
});

// Notification system
function checkNewNotifications() {
    // This would typically connect to a WebSocket or use Server-Sent Events
    // For now, we'll use periodic polling
    console.log('Checking for new notifications...');
    // Implement actual notification check based on your backend
}

// Initialize notification system
if (Notification.permission === 'default') {
    Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
            console.log('Notification permission granted');
        }
    });
}
// [file content end] ```