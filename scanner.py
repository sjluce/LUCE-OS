import platform
import psutil
import os
import subprocess
import json

try:
    import wmi  # Windows only: pip install wmi
except ImportError:
    wmi = None

def get_system_info():
    info = {}
    
    # OS Details
    info['OS'] = platform.uname()._asdict()
    
    # CPU
    info['CPU'] = {
        'Physical Cores': psutil.cpu_count(logical=False),
        'Logical Cores': psutil.cpu_count(logical=True),
        'Usage %': psutil.cpu_percent(interval=1),
        'Frequency MHz': psutil.cpu_freq().current if psutil.cpu_freq() else 'N/A'
    }
    
    # Memory
    mem = psutil.virtual_memory()
    info['Memory'] = {
        'Total GB': round(mem.total / (1024**3), 2),
        'Available GB': round(mem.available / (1024**3), 2),
        'Used %': mem.percent
    }
    
    # Disks
    info['Disks'] = []
    for part in psutil.disk_partitions(all=False):
        usage = psutil.disk_usage(part.mountpoint)
        info['Disks'].append({
            'Device': part.device,
            'Mount': part.mountpoint,
            'Type': part.fstype,
            'Total GB': round(usage.total / (1024**3), 2),
            'Used %': usage.percent
        })
    
    # Basic Hardware/Drivers
    if platform.system() == 'Windows' and wmi:
        c = wmi.WMI()
        info['GPU'] = [gpu.Name for gpu in c.Win32_VideoController()]
        info['Drivers Sample'] = [dev.Name for dev in c.Win32_PnPEntity()[:10]]  # Sample to avoid overload
    elif platform.system() == 'Linux':
        try:
            info['GPU'] = subprocess.check_output(['lspci', '|', 'grep', '-i', 'vga'], shell=True).decode().strip()
        except:
            info['GPU'] = 'Run lspci for details'
    
    return info

# Run and print pretty JSON
if __name__ == "__main__":
    data = get_system_info()
    print(json.dumps(data, indent=4))
