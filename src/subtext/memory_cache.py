import atexit
import os
import pathlib
from typing import Optional

from pydantic import BaseModel

# Optional imports - gracefully handle if not installed
try:
    from filelock import FileLock
    FILELOCK_AVAILABLE = True
except ImportError:
    FILELOCK_AVAILABLE = False
    print("Warning: filelock package not installed. Shared memory locking disabled.")

try:
    from shared_memory_dict import SharedMemoryDict  # type: ignore
    SHARED_MEMORY_AVAILABLE = True
except ImportError:
    SHARED_MEMORY_AVAILABLE = False
    print("Warning: shared-memory-dict package not installed. Shared memory disabled.")

HERE = pathlib.Path(__file__).parent
LOCKPATH = HERE / "memory_cache.lock"

# Only create lock if filelock is available
LOCK = FileLock(str(LOCKPATH), timeout=1) if FILELOCK_AVAILABLE else None

# flake8: noqa: E402
os.environ["SHARED_MEMORY_USE_LOCK"] = "1"

SHARED_MEMORY_NAME = "subtext"
SHARED_MEMORY_SIZE = 1024 * 1024


class SharedMemoryData(BaseModel):
    initialized: bool = False


def _delete_shared_memory(smd):
    """Delete shared memory when owner exits"""
    if hasattr(smd, 'shm'):
        smd.shm.close()
        smd.shm.unlink()
    del smd


def _release(smd) -> None:
    """Release shared memory when non-owner exits"""
    if hasattr(smd, 'shm'):
        smd.shm.close()
    del smd


def create_shared_memory(owner: bool):
    """Create shared memory dict if available, otherwise return a regular dict"""
    if not SHARED_MEMORY_AVAILABLE:
        print("⚠️ Shared memory not available - using regular dict")
        return {}

    if LOCK:
        # Use the lock decorator if available
        @LOCK
        def _create():
            smd = SharedMemoryDict(name=SHARED_MEMORY_NAME, size=SHARED_MEMORY_SIZE)
            if owner:
                atexit.register(_delete_shared_memory, smd)
            else:
                atexit.register(_release, smd)
            return smd
        return _create()
    else:
        # No lock available, create without locking
        smd = SharedMemoryDict(name=SHARED_MEMORY_NAME, size=SHARED_MEMORY_SIZE)
        if owner:
            atexit.register(_delete_shared_memory, smd)
        else:
            atexit.register(_release, smd)
        return smd
