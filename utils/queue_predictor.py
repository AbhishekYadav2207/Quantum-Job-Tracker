# [file name]: utils/queue_predictor.py
# [file content begin]
import time
import json
import os
from datetime import datetime, timedelta
import logging


class QueuePredictor:
    def __init__(self):
        self.history_file = "queue_history.json"
        self.history = self.load_history()
        self.logger = logging.getLogger(__name__)

    def load_history(self):
        """Load historical queue data"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_history(self):
        """Save historical queue data"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f)
        except Exception as e:
            self.logger.error(f"Error saving queue history: {e}")

    def record_job_completion(self, job_id, backend_name, queue_time, run_time):
        """Record job completion for historical analysis"""
        if backend_name not in self.history:
            self.history[backend_name] = []

        self.history[backend_name].append({
            'timestamp': datetime.now().isoformat(),
            'job_id': job_id,
            'queue_time': queue_time,
            'run_time': run_time
        })

        # Keep only last 1000 entries per backend
        if len(self.history[backend_name]) > 1000:
            self.history[backend_name] = self.history[backend_name][-1000:]

        self.save_history()

    def estimate_start_time(self, job_id, backend_name, current_queue_length):
        """Estimate when a job will start running"""
        if backend_name not in self.history or not self.history[backend_name]:
            return None

        # Calculate average job runtime from history
        run_times = [entry['run_time'] for entry in self.history[backend_name] if entry['run_time'] > 0]
        if not run_times:
            return None

        avg_run_time = sum(run_times) / len(run_times)

        # Estimate start time based on queue position and average runtime
        estimated_wait = current_queue_length * avg_run_time

        if estimated_wait > 0:
            return (datetime.now() + timedelta(seconds=estimated_wait)).strftime("%Y-%m-%d %H:%M:%S")

        return None

    def estimate_average_wait(self, backend_name):
        """Estimate average wait time for a backend"""
        if backend_name not in self.history or not self.history[backend_name]:
            return "Unknown"

        # Calculate average queue time from history
        queue_times = [entry['queue_time'] for entry in self.history[backend_name] if entry['queue_time'] > 0]
        if not queue_times:
            return "Unknown"

        avg_queue_time = sum(queue_times) / len(queue_times)

        if avg_queue_time < 60:
            return f"{int(avg_queue_time)} seconds"
        elif avg_queue_time < 3600:
            return f"{int(avg_queue_time / 60)} minutes"
        else:
            return f"{int(avg_queue_time / 3600)} hours"
# [file content end]