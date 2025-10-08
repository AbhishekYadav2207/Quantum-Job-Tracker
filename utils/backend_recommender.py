# [file name]: utils/backend_recommender.py
# [file content begin]
import logging


class BackendRecommender:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_recommendations(self, user_id, backend_status_cache):
        """Get backend recommendations for a user"""
        recommendations = []

        for backend_name, backend_info in backend_status_cache.items():
            if not backend_info.get('operational', False):
                continue

            score = self.calculate_backend_score(backend_name, backend_info)

            recommendations.append({
                'name': backend_name,
                'service_type': backend_info.get('service_type', 'unknown'),
                'qubits': backend_info.get('qubits', 'Unknown'),
                'queue_length': backend_info.get('pending_jobs', 0),
                'score': score,
                'recommendation_reason': self.get_recommendation_reason(backend_name, backend_info, score)
            })

        # Sort by score (descending)
        recommendations.sort(key=lambda x: x['score'], reverse=True)

        return recommendations[:3]  # Return top 3 recommendations

    def calculate_backend_score(self, backend_name, backend_info):
        """Calculate a score for backend recommendation"""
        score = 100

        # Penalize based on queue length
        queue_length = backend_info.get('pending_jobs', 0)
        score -= min(queue_length * 2, 50)  # Max penalty of 50 for long queues

        # Prefer simulators for development
        if backend_info.get('simulator', False):
            score += 10

        # Prefer backends with more qubits (more capability)
        qubits = backend_info.get('qubits', 0)
        if isinstance(qubits, int):
            score += min(qubits / 5, 20)  # Max bonus of 20 for large backends

        # Ensure score is within reasonable bounds
        return max(0, min(score, 100))

    def get_recommendation_reason(self, backend_name, backend_info, score):
        """Generate a human-readable reason for the recommendation"""
        reasons = []

        queue_length = backend_info.get('pending_jobs', 0)
        if queue_length == 0:
            reasons.append("No jobs in queue")
        elif queue_length < 5:
            reasons.append("Short queue")
        else:
            reasons.append(f"{queue_length} jobs in queue")

        if backend_info.get('simulator', False):
            reasons.append("Simulator (good for testing)")

        qubits = backend_info.get('qubits', 0)
        if isinstance(qubits, int) and qubits > 10:
            reasons.append("High qubit count")

        return ", ".join(reasons)
# [file content end]