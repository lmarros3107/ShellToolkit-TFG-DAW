import os
import multiprocessing

bind = "0.0.0.0:8000"
workers = int(os.getenv("WEB_CONCURRENCY", "1"))
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "gthread")
threads = int(os.getenv("GUNICORN_THREADS", "2"))
timeout = 90
graceful_timeout = 30
keepalive = 5

accesslog = "-"
errorlog = "-"
loglevel = "info"

# Use temporary memory-backed directory for worker heartbeats.
worker_tmp_dir = "/dev/shm"
