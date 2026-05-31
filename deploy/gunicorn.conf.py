"""
Gunicorn configuration for Market Mapper.
Deploy target: Ubuntu LXC behind Cloudflare Tunnel.
"""

# Server socket
bind = "127.0.0.1:8000"

# Worker processes
workers = 3
worker_class = "gthread"
threads = 2
worker_tmp_dir = "/dev/shm"

# Timeout
timeout = 120
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "/var/log/marketmapper/gunicorn-access.log"
errorlog = "/var/log/marketmapper/gunicorn-error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)s'

# Process naming
proc_name = "marketmapper"

# Server mechanics
preload_app = True
max_requests = 1000
max_requests_jitter = 50
