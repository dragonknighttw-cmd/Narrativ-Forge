import logging

from pythonjsonlogger import jsonlogger


def configure_logging() -> None:
    """Configure one JSON stream handler for application logs."""
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    if any(getattr(handler, "_narrativ_json", False) for handler in root.handlers):
        return

    handler = logging.StreamHandler()
    handler._narrativ_json = True
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)
