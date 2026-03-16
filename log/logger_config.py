"""
Shared logging configuration for the Mutual Fund Analyzer.

Provides a custom Filter that injects the class name into log records,
enabling format strings like: module.ClassName::method_name
"""

import logging
import inspect


class ClassNameFilter(logging.Filter):
    """
    Injects a 'className' attribute into each LogRecord.

    Walks the call stack to find the first frame that belongs to a class
    (i.e. has 'self' or 'cls' in its locals). Falls back to an empty string
    so the format string is always safe to use.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        class_name = ""
        frame = inspect.currentframe()
        try:
            # Walk up the stack past logging internals to find the caller's frame
            while frame is not None:
                local_self = frame.f_locals.get("self")
                local_cls = frame.f_locals.get("cls")
                owner = local_self or local_cls
                if owner is not None:
                    candidate = type(owner).__name__ if local_self else owner.__name__
                    # Skip logging framework classes
                    if not candidate.startswith("Logger") and candidate != "ClassNameFilter":
                        class_name = candidate
                        break
                frame = frame.f_back
        finally:
            del frame  # avoid reference cycles

        record.className = class_name
        return True


def configure_logging(level: int = logging.INFO) -> None:
    """
    Configure root logger with ClassNameFilter and a consistent format.

    Format: YYYY-MM-DD HH:MM:SS  LEVEL     module.ClassName::func_name — message
    Safe to call multiple times (basicConfig is a no-op if already configured).
    """
    fmt = "%(asctime)s  %(levelname)-8s  %(name)s%(className)s::%(funcName)s — %(message)s"

    handler = logging.StreamHandler()
    handler.addFilter(ClassNameFilter())
    handler.setFormatter(logging.Formatter(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S"))

    root = logging.getLogger()
    if not root.handlers:
        root.setLevel(level)
        root.addHandler(handler)
