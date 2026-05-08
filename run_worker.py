from app.worker.pool import start_worker_pool

if __name__ == "__main__":
    start_worker_pool(num_workers=4)