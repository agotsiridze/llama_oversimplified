import time
from contextlib import contextmanager
from typing import Any, Generator


@contextmanager
def time_tracker(chat_history_length: int) -> Generator[None, Any, None]:
    """
    A clean context manager to track elapsed time of block operations.
    """

    start_time = time.time()
    print(chat_history_length, "=" * 20)

    print("-" * 20)
    try:
        # This yields control back to the block inside the 'with' statement
        yield
    finally:
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"Time: {elapsed:.2f}s")
        print("-" * 20)
