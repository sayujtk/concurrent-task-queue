import threading
import signal
from concurrent.futures import ThreadPoolExecutor
from app.database import SessionFactory
from app.worker.executor import poll_and_execute

shutdown_event = threading.Event()

def worker_loop():
    while not shutdown_event.is_set():
        session = SessionFactory()
        try:
            poll_and_execute(session)
        finally:
            SessionFactory.remove()
        shutdown_event.wait(timeout=1.0)

def handle_shutdown(signum, frame):
    print("Shutdown signal received, draining workers...")
    shutdown_event.set()

def start_worker_pool(num_workers: int = 4):
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    with ThreadPoolExecutor(max_workers=num_workers) as pool:
        futures = [pool.submit(worker_loop) for _ in range(num_workers)]
        for f in futures:
            f.result()