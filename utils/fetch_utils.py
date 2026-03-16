import time
import logging
from constants.fetch_constants import QUOTA_SIGNALS

logger = logging.getLogger(__name__)


class FetchUtils:
    """Utility methods for HTTP fetching with retry and backoff logic."""

    @staticmethod
    def is_quota_error(exc: Exception) -> bool:
        """Return True if the exception looks like a quota / rate-limit error."""
        return any(signal in str(exc).lower() for signal in QUOTA_SIGNALS)

    @staticmethod
    def fetch_with_backoff(fn, *args, max_retries: int = 5, base_delay: float = 2.0, **kwargs):
        """
        Call fn(*args, **kwargs) with exponential backoff on quota/rate-limit errors.
        Delays: 2s, 4s, 8s, 16s, 32s. Raises on non-quota errors or exhausted retries.
        """
        delay = base_delay
        for attempt in range(max_retries):
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                if FetchUtils.is_quota_error(exc) and attempt < max_retries - 1:
                    logger.warning(
                        "Rate limit hit calling %s — waiting %.0fs before retry (attempt %d of %d)",
                        fn.__name__, delay, attempt + 1, max_retries - 1,
                    )
                    time.sleep(delay)
                    delay *= 2
                else:
                    raise


# Module-level aliases so fetchers can call the functions directly
is_quota_error = FetchUtils.is_quota_error
fetch_with_backoff = FetchUtils.fetch_with_backoff
