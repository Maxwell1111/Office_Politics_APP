import os
import signal
import subprocess
from contextlib import contextmanager
import time
from warnings import warn
from pathlib import Path
import atexit
from threading import Thread

HERE = Path(__file__).parent
WWW = HERE / "www"
MAX_SPACE_NPM = 256
APP_NAME = "subtext"

os.environ["NODE_OPTIONS"] = f"--max_old_space_size={MAX_SPACE_NPM}"


# Function to clean up background processes
def cleanup(pro: subprocess.Popen):
    print("Cleaning up background processes...")
    pro.terminate()  # Attempt graceful termination
    try:
        pro.wait(timeout=5)  # Wait up to 5 seconds for process to terminate
    except subprocess.TimeoutExpired:
        pro.kill()  # Force kill if not terminated after timeout


# Context manager to handle process start and cleanup
@contextmanager  # type: ignore
def run_background_process() -> subprocess.Popen:  # type: ignore
    pro: subprocess.Popen | None = None
    try:
        # Switch to using the script's current directory:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        # Start background processes
        port = os.environ.get("PORT", "80")
        workers = os.environ.get("WEB_CONCURRENCY", "1")  # Render free tier: use 1 worker

        print(f"Starting uvicorn on port {port} with {workers} workers...")

        pro = subprocess.Popen(
            [
                "uvicorn",
                "--host",
                "0.0.0.0",
                "--port",
                port,
                "--workers",
                workers,
                "--forwarded-allow-ips=*",
                f"{APP_NAME}.app:app",
            ]
        )
        # Trap SIGINT (Ctrl-C) to call the cleanup function
        signal.signal(signal.SIGINT, lambda signum, frame: lambda: cleanup(pro))
        yield pro
    finally:
        if pro:
            cleanup(pro)


def perform_npm_build() -> None:
    """
    Skip npm build in production - it's already built in Dockerfile
    This function is kept for local development compatibility
    """
    if os.path.exists(WWW / "dist"):
        print("Frontend already built (found www/dist). Skipping npm build.")
        return

    print("Warning: www/dist not found. Frontend may not work properly.")
    print("In production, the frontend should be built during Docker build.")


def run_background_tasks() -> None:
    """Run the background tasks."""
    data: list[subprocess.Popen] = list()

    def kill_proc() -> None:
        if data:
            proc = data[0]
            proc.kill()

    atexit.register(kill_proc)
    while True:
        proc = subprocess.Popen(f"python -m {APP_NAME}.background_tasks", shell=True, cwd=HERE)
        if len(data) == 0:
            data.append(proc)
        else:
            data[0] = proc
        while proc.poll() is None:
            time.sleep(1)


def main() -> None:
    # Skip npm build - already done in Dockerfile
    perform_npm_build()

    # Skip background tasks for now - not needed for basic functionality
    # background_task = Thread(target=run_background_tasks, daemon=True, name="background_tasks")
    # background_task.start()

    print("Starting Politico server...")

    # Use the context manager to run and manage the uvicorn process
    process: subprocess.Popen
    with run_background_process() as process:
        # Wait for the uvicorn process to finish
        assert process is not None
        try:
            rtn = process.wait()
            if rtn != 0:
                warn(f"Uvicorn process returned {rtn}")
        except KeyboardInterrupt:
            # Handle Ctrl-C
            print("\nShutting down gracefully...")
            pass


# Main function
if __name__ == "__main__":
    main()
