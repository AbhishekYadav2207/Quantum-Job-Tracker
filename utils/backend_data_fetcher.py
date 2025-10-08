# [file name]: utils/backend_data_fetcher.py
import logging
from datetime import datetime, timedelta
from qiskit_ibm_runtime import QiskitRuntimeService

class BackendDataFetcher:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes

    def _get_service(self, token=None, channel="ibm_quantum_platform", instance=None):
        """Helper to get QiskitRuntimeService"""
        try:
            if instance:
                return QiskitRuntimeService(channel="ibm_cloud", instance=instance, token=token)
            return QiskitRuntimeService(channel=channel, token=token)
        except Exception as e:
            self.logger.error(f"Failed to create QiskitRuntimeService: {e}")
            return None

    def get_backend_details(self, backend_name, token=None, instance=None):
        """Get detailed information about a specific backend"""
        cache_key = f"backend_{backend_name}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_timeout):
                return cached_data

        try:
            service = self._get_service(token, instance=instance)
            if not service:
                return self._create_fallback_backend_data(backend_name)

            backend = service.backend(backend_name)
            config = backend.configuration()
            status = backend.status()

            formatted_data = {
                "name": backend.name,
                "n_qubits": getattr(config, "n_qubits", "Unknown"),
                "backend_version": getattr(config, "backend_version", "Unknown"),
                "simulator": getattr(config, "simulator", False),
                "description": getattr(config, "description", ""),
                "status": {
                    "operational": getattr(status, "operational", False),
                    "pending_jobs": getattr(status, "pending_jobs", "N/A"),
                    "queue_position": getattr(status, "queue_position", "N/A"),
                    "status_msg": getattr(status, "status_msg", "")
                },
                "configuration": {
                    "max_shots": getattr(config, "max_shots", "N/A"),
                    "max_experiments": getattr(config, "max_experiments", "N/A"),
                    "memory": getattr(config, "memory", False),
                    "basis_gates": getattr(config, "basis_gates", []),
                    "rep_times": getattr(config, "rep_times", []),
                    "default_rep_time": getattr(config, "default_rep_time", "N/A"),
                    "min_rep_time": getattr(config, "min_rep_time", "N/A"),
                    "max_rep_time": getattr(config, "max_rep_time", "N/A"),
                }
            }

            self.cache[cache_key] = (formatted_data, datetime.now())
            return formatted_data
        except Exception as e:
            self.logger.error(f"Error fetching backend details: {e}")
            return self._create_fallback_backend_data(backend_name)

    def _create_fallback_backend_data(self, backend_name):
        """Create fallback backend data structure"""
        return {
            "name": backend_name,
            "n_qubits": "Unknown",
            "backend_version": "Unknown",
            "simulator": False,
            "description": "Could not fetch backend details",
            "status": {
                "operational": False,
                "pending_jobs": "N/A",
                "queue_position": "N/A",
                "status_msg": "Unavailable"
            },
            "configuration": {
                "max_shots": "N/A",
                "max_experiments": "N/A",
                "memory": False,
                "basis_gates": [],
                "rep_times": [],
                "default_rep_time": "N/A",
                "min_rep_time": "N/A",
                "max_rep_time": "N/A"
            }
        }

    def get_backend_calibration(self, backend_name, token=None, instance=None):
        """Return full calibration data from backend.properties()"""
        cache_key = f"calibration_{backend_name}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_timeout):
                return cached_data

        try:
            service = self._get_service(token, instance=instance)
            backend = service.backend(backend_name)
            props = backend.properties()

            if not props:
                return {}

            calibration_data = {
                "last_update": props.last_update_date.isoformat() if hasattr(props, "last_update_date") else None,
                "general": {},
                "qubits": {},
                "gates": {}
            }

            # General backend-level properties
            if hasattr(props, "general") and props.general:
                calibration_data["general"] = {
                    g.name: {
                        "value": getattr(g, "value", None),
                        "unit": getattr(g, "unit", None),
                        "date": getattr(g, "date", None).isoformat() if getattr(g, "date", None) else None
                    }
                    for g in props.general
                }

            # Qubit-specific properties (T1, T2, frequency, readout error, etc.)
            for idx, qubit_params in enumerate(props.qubits):
                qubit_data = {}
                for param in qubit_params:
                    qubit_data[param.name] = {
                        "value": getattr(param, "value", None),
                        "unit": getattr(param, "unit", None),
                        "date": getattr(param, "date", None).isoformat() if getattr(param, "date", None) else None
                    }
                calibration_data["qubits"][f"q{idx}"] = qubit_data

            # Gate-specific properties (gate error, gate length, etc.)
            for gate in props.gates:
                gate_name = f"{gate.gate}-{','.join(map(str, gate.qubits))}"
                gate_data = {}
                for param in gate.parameters:
                    gate_data[param.name] = {
                        "value": getattr(param, "value", None),
                        "unit": getattr(param, "unit", None),
                        "date": getattr(param, "date", None).isoformat() if getattr(param, "date", None) else None
                    }
                calibration_data["gates"][gate_name] = gate_data

            self.cache[cache_key] = (calibration_data, datetime.now())
            return calibration_data

        except Exception as e:
            self.logger.error(f"Error fetching calibration data: {e}")
            return {}

    def get_backend_parameters(self, backend_name, token=None, instance=None):
        """Return backend parameters (just reuse configuration for now)"""
        cache_key = f"parameters_{backend_name}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_timeout):
                return cached_data

        try:
            service = self._get_service(token, instance=instance)
            backend = service.backend(backend_name)
            config = backend.configuration()

            parameters_data = {}
            for field in ["max_shots", "max_experiments", "basis_gates"]:
                parameters_data[field] = {"value": getattr(config, field, "N/A"),
                                          "description": f"{field} from configuration"}

            self.cache[cache_key] = (parameters_data, datetime.now())
            return parameters_data
        except Exception as e:
            self.logger.error(f"Error fetching parameters: {e}")
            return {}

    def get_all_backends(self, token=None, instance=None):
        """List all available backends"""
        cache_key = "all_backends"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_timeout):
                return cached_data

        try:
            service = self._get_service(token, instance=instance)
            backends = service.backends()
            data = [{"name": b.name, "simulator": b.configuration().simulator} for b in backends]

            self.cache[cache_key] = (data, datetime.now())
            return data
        except Exception as e:
            self.logger.error(f"Error fetching all backends: {e}")
            return []
