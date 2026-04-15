import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
threads = 2
timeout = 90
graceful_timeout = 30
keepalive = 5

accesslog = "-"
errorlog = "-"
loglevel = "info"

# Use temporary memory-backed directory for worker heartbeats.
worker_tmp_dir = "/dev/shm"

