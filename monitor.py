import psutil
import platform
from datetime import datetime


def get_cpu_info():
    """Get CPU usage and core information."""
    return {
        "usage_percent": psutil.cpu_percent(interval=1),
        "core_count": psutil.cpu_count(logical=False),
        "thread_count": psutil.cpu_count(logical=True),
        "per_core": psutil.cpu_percent(interval=1, percpu=True),
        "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else "N/A"
    }


def get_memory_info():
    """Get RAM usage information."""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "total_gb": round(mem.total / (1024**3), 2),
        "used_gb": round(mem.used / (1024**3), 2),
        "available_gb": round(mem.available / (1024**3), 2),
        "percent": mem.percent,
        "swap_total_gb": round(swap.total / (1024**3), 2),
        "swap_used_gb": round(swap.used / (1024**3), 2),
        "swap_percent": swap.percent
    }


def get_disk_info():
    """Get disk usage for all partitions."""
    disks = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "filesystem": partition.fstype,
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "percent": usage.percent,
                "alert": usage.percent >= 80  # alert if over 80%
            })
        except PermissionError:
            continue
    return disks


def get_top_processes(limit=10):
    """Get top processes by CPU usage."""
    processes = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
        try:
            info = proc.info
            processes.append({
                "pid": info["pid"],
                "name": info["name"],
                "cpu_percent": round(info["cpu_percent"] or 0, 2),
                "memory_percent": round(info["memory_percent"] or 0, 2),
                "status": info["status"]
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Sort by CPU usage
    processes.sort(key=lambda x: x["cpu_percent"], reverse=True)
    return processes[:limit]


def get_network_stats():
    """Get network interface statistics."""
    stats = psutil.net_io_counters()
    return {
        "bytes_sent_mb": round(stats.bytes_sent / (1024**2), 2),
        "bytes_recv_mb": round(stats.bytes_recv / (1024**2), 2),
        "packets_sent": stats.packets_sent,
        "packets_recv": stats.packets_recv,
    }


def get_system_info():
    """Get general system information."""
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes = remainder // 60
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "hostname": platform.node(),
        "architecture": platform.machine(),
        "uptime": f"{hours}h {minutes}m",
        "boot_time": boot_time.strftime("%Y-%m-%d %H:%M:%S")
    }