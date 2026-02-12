import logging
import time
from logging.handlers import RotatingFileHandler

class SafeFormatter(logging.Formatter):
    converter = time.gmtime
    def format(self, record):
        for attr in ["flex", "user", "cmd"]:
            if not hasattr(record, attr):
                setattr(record, attr, "-")
        return super().format(record)

def setup_logging():
    handler = RotatingFileHandler(
        "veyra.log", maxBytes=5*1024*1024, backupCount=5, encoding="utf-8"
    )
    formatter = SafeFormatter(
        "%(asctime)s |"
        " %(levelname)s |"
        " %(name)s | "
        "%(message)s |"
        " %(module)s:%(funcName)s | "
        "flex=%(flex)s |"
        "user=%(user)s |"
        "cmd=%(cmd)s |"
        )
    handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler]
    )