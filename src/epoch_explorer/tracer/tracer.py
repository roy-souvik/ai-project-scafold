import json
from datetime import datetime
import threading
from collections import defaultdict

def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)

        return instances[cls]

    return get_instance

# # Usage
# singleton1 = Singleton()
# singleton2 = Singleton()
# print(singleton1 is singleton2) # Output: True

@singleton
class InMemoryTracer:
    """Simple in-memory tracer for observability without external dependencies"""

    def __init__(self, max_traces: int = 10000):
        self.traces = []
        self.max_traces = max_traces
        self.lock = threading.Lock()

    def add_trace(self, operation: str, input_data: dict, output_data: dict,
                  duration_ms: float, status: str = "success", error: str = None):
        """Add a trace to memory"""
        print("tracer id in post :", id(self))
        with self.lock:
            trace = {
                "timestamp": datetime.utcnow().isoformat(),
                "operation": operation,
                "input": input_data,
                "output": output_data,
                "duration_ms": duration_ms,
                "status": status,
                "error": error
            }
            print(trace,"trace details")
            self.traces.append(trace)

            # Keep memory bounded
            if len(self.traces) > self.max_traces:
                self.traces = self.traces[-self.max_traces:]
            print(len(self.traces),"length")

    def get_traces(self, operation: str = None, limit: int = 100):
        """Retrieve traces"""
        with self.lock:
            result = self.traces
            if operation:
                result = [t for t in result if t["operation"] == operation]
            return result[-limit:]

    def get_stats(self):
        """Get statistics about traces including token usage"""
        print("tracer id in get:", id(self))
        with self.lock:
            print(self.traces,"traces within get traces")
            if not self.traces:
                print("no trace")
                return {}

            stats = defaultdict(lambda: {
                "count": 0,
                "total_duration": 0,
                "errors": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0
            })

            print(stats,"stats at top")

            for trace in self.traces:
                op = trace["operation"]
                stats[op]["count"] += 1
                stats[op]["total_duration"] += trace["duration_ms"]

                if trace["status"] == "error":
                    stats[op]["errors"] += 1

                # Aggregate token usage
                if "input_tokens" in trace["output"]:
                    stats[op]["input_tokens"] += trace["input"].get("input_tokens", 0)
                if "output_tokens" in trace["output"]:
                    stats[op]["output_tokens"] += trace["output"].get("output_tokens", 0)
                if "total_tokens" in trace["output"]:
                    stats[op]["total_tokens"] += trace["output"].get("total_tokens", 0)

            # Calculate averages
            for op in stats:
                if stats[op]["count"] > 0:
                    stats[op]["avg_duration"] = stats[op]["total_duration"] / stats[op]["count"]

            print(stats,"stats")
            return dict(stats)

    def export_json(self, filepath: str):
        """Export traces to JSON file"""
        with self.lock:
            with open(filepath, 'w') as f:
                json.dump(self.traces, f, indent=2)

    def clear(self):
        """Clear all traces"""
        with self.lock:
            self.traces = []
