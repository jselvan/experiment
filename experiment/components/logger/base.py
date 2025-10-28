from experiment.components.components import BaseComponent


import logging
import json
import sys
from datetime import datetime

class JSONLFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "time": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record, ensure_ascii=False)

def setup_logger(name="experiment", jsonl_path="log.jsonl"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # capture all messages

    # ---- Console Handler (WARN and above) ----
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_fmt = logging.Formatter("[%(levelname)s] %(message)s")
    console_handler.setFormatter(console_fmt)

    # ---- File Handler (DEBUG and above, JSONL) ----
    file_handler = logging.FileHandler(jsonl_path, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JSONLFormatter())

    # ---- Add Handlers ----
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


class BaseLogger(BaseComponent):
    COMPONENT_TYPE = "logger"
    def initialize(self):
        if not self.manager:
            raise RuntimeError("Logger must be registered with a Manager before initialization.")
        session_directory = self.manager.get_session_directory()
        log_path = session_directory / "log.jsonl"
        self.logger = setup_logger(name="experiment", jsonl_path=log_path)
    def log(self, level: str, message: str):
        if not hasattr(self, 'logger'):
            raise RuntimeError("Logger must be initialized before logging messages.")
        log_method = getattr(self.logger, level.lower(), None)
        if log_method is None:
            raise ValueError(f"Invalid log level: {level}")
        log_method(message)
    def log_event(self, event_type: str, data: dict):
        event_message = {
            "event_type": event_type,
            "data": data
        }
        self.log("info", f"Event: {json.dumps(event_message)}")