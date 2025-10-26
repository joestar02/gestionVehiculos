import logging
import uuid

def log_exception(exc: Exception, logger_name: str = __name__) -> str:
    """Log exception with traceback and return a short error id."""
    err_id = uuid.uuid4().hex[:8]
    logger = logging.getLogger(logger_name)
    logger.exception('[%s] Unexpected exception: %s', err_id, exc)
    return err_id
