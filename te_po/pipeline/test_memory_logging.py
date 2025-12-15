import logging
from metrics import log_memory_usage

def test_memory_logging():
    """Test the log_memory_usage function."""
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    log_memory_usage("test stage")

if __name__ == "__main__":
    test_memory_logging()