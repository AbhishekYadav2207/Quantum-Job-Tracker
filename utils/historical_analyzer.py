# [file name]: utils/historical_analyzer.py
# [file content begin]
import json
import os
import logging
from datetime import datetime, timedelta


class HistoricalAnalyzer:
    def __init__(self):
        self.history_file = "job_history.json"
        self.history = self.load_history()
        self.logger = logging.getLogger(__name__)

    def load_history(self):
        """Load historical job data"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_history(self):
        """Save historical job data"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f)
        except Exception as e:
            self.logger.error(f"Error saving job history: {e}")

    def record_job_event(self, job_id, event_type, timestamp=None, data=None):
        """Record a job event in history"""
        if job_id not in self.history:
            self.history[job_id] = []

        event = {
            'type': event_type,
            'timestamp': timestamp or datetime.now().isoformat(),
            'data': data or {}
        }

        self.history[job_id].append(event)
        self.save_history()

    def get_job_timeline(self, job_id):
        """Get timeline of events for a job"""
        return self.history.get(job_id, [])

    def get_analytics(self, user_id=None):
        """Get analytics data"""
        analytics = {
            'total_jobs': len(self.history),
            'jobs_by_status': {},
            'jobs_by_backend': {},
            'average_queue_time': 0,
            'success_rate': 0,
            'recent_activity': []
        }

        # Count jobs by status and backend
        completed_jobs = 0
        total_queue_time = 0

        for job_id, events in self.history.items():
            # Filter by user if specified
            if user_id:
                user_events = [e for e in events if e.get('data', {}).get('user_id') == user_id]
                if not user_events:
                    continue

            # Get latest status
            status_events = [e for e in events if e['type'] == 'status_change']
            if status_events:
                latest_status = status_events[-1]['data'].get('status', 'unknown')
                analytics['jobs_by_status'][latest_status] = analytics['jobs_by_status'].get(latest_status, 0) + 1

                if latest_status == 'COMPLETED':
                    completed_jobs += 1

            # Get backend
            backend_events = [e for e in events if e['type'] == 'backend_assigned']
            if backend_events:
                backend = backend_events[0]['data'].get('backend', 'unknown')
                analytics['jobs_by_backend'][backend] = analytics['jobs_by_backend'].get(backend, 0) + 1

            # Calculate queue time
            queue_events = [e for e in events if e['type'] == 'queued']
            start_events = [e for e in events if e['type'] == 'running']

            if queue_events and start_events:
                queue_time = datetime.fromisoformat(start_events[0]['timestamp']) - datetime.fromisoformat(
                    queue_events[0]['timestamp'])
                total_queue_time += queue_time.total_seconds()

            # Add to recent activity
            if events:
                analytics['recent_activity'].append({
                    'job_id': job_id,
                    'last_event': events[-1]['type'],
                    'timestamp': events[-1]['timestamp']
                })

        # Calculate averages
        if completed_jobs > 0:
            analytics['success_rate'] = (completed_jobs / len(self.history)) * 100
            analytics['average_queue_time'] = total_queue_time / completed_jobs if completed_jops > 0 else 0

        # Sort recent activity
        analytics['recent_activity'].sort(key=lambda x: x['timestamp'], reverse=True)
        analytics['recent_activity'] = analytics['recent_activity'][:10]  # Top 10 most recent

        return analytics
# [file content end]