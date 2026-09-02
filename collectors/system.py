import platform
import os

def collect_system_info():
    return {
        "os": platform.system(),
        "kernel": platform.release(),
        "architecture": platform.machine(),
        "hostname": platform.node(),
        "cpu_count": os.cpu_count(),
    }