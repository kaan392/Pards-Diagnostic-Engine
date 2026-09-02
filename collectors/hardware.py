import psutil


def collect_hardware_info():
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "cpu_usage_percent": psutil.cpu_percent(interval=1),
        "ram_total_gb": round(memory.total / (1024 ** 3), 2),
        "ram_used_percent": memory.percent,
        "disk_total_gb": round(disk.total / (1024 ** 3), 2),
        "disk_used_percent": disk.percent,
    }