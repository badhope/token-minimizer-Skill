import socket
from typing import Tuple

def find_available_port(start_port: int = 8000, max_attempts: int = 100) -> int:
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port):
            return port
    raise RuntimeError(f"No available port found in range {start_port}-{start_port + max_attempts}")

def is_port_available(port: int) -> bool:
    """Check if a port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            return True
    except OSError:
        return False

def get_port_with_retry(port: int, max_attempts: int = 10) -> int:
    """Try to use the specified port, fall back to finding an available one."""
    if is_port_available(port):
        return port

    for attempt in range(max_attempts):
        new_port = port + attempt + 1
        if is_port_available(new_port):
            return new_port

    raise RuntimeError(f"Could not find available port near {port}")
