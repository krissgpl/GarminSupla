"""Failed administrator login rate limiting.

No credentials, session tokens or recovery codes are stored.
The counters are local to one application process.
"""

from collections import OrderedDict, deque
from ipaddress import ip_address
from math import ceil
from threading import Lock
from time import monotonic
from typing import Callable


def _canonical_ip(value: str | None) -> str | None:
    if not value:
        return None

    try:
        return str(ip_address(value))
    except ValueError:
        return None


def resolve_client_key(
    peer_host: str | None,
    x_real_ip: str | None,
    trusted_proxy_ips: frozenset[str],
) -> str:
    """Trust X-Real-IP only from an explicitly trusted peer."""

    peer_ip = _canonical_ip(peer_host)

    if peer_ip is not None and peer_ip in trusted_proxy_ips:
        forwarded_ip = _canonical_ip(x_real_ip)

        if forwarded_ip is not None:
            return forwarded_ip

    if peer_ip is not None:
        return peer_ip

    # Used for malformed or unavailable peer identities.
    # Never trust a forwarded header in this case.
    return "peer:" + (peer_host or "unknown")


class AdminLoginRateLimiter:
    """Bounded, process-local sliding window of failed logins."""

    def __init__(
        self,
        *,
        failure_limit: int = 8,
        window_seconds: int = 300,
        max_clients: int = 4096,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        if (
            failure_limit < 1
            or window_seconds < 1
            or max_clients < 1
        ):
            raise ValueError("Limiter settings must be positive.")

        self.failure_limit = failure_limit
        self.window_seconds = window_seconds
        self.max_clients = max_clients
        self._clock = clock
        self._lock = Lock()
        self._failures: OrderedDict[
            str, deque[float]
        ] = OrderedDict()

    def _get_active(
        self,
        key: str,
        now: float,
    ) -> deque[float] | None:
        failures = self._failures.get(key)

        if failures is None:
            return None

        cutoff = now - self.window_seconds

        while failures and failures[0] <= cutoff:
            failures.popleft()

        if not failures:
            del self._failures[key]
            return None

        self._failures.move_to_end(key)
        return failures

    def retry_after(self, key: str) -> int:
        """Return zero if allowed; otherwise seconds to retry."""

        with self._lock:
            now = self._clock()
            failures = self._get_active(key, now)

            if (
                failures is None
                or len(failures) < self.failure_limit
            ):
                return 0

            return max(
                1,
                ceil(
                    self.window_seconds
                    - (now - failures[0])
                ),
            )

    def record_failure(self, key: str) -> None:
        """Record one unsuccessful authentication attempt."""

        with self._lock:
            now = self._clock()
            failures = self._get_active(key, now)

            if failures is None:
                if len(self._failures) >= self.max_clients:
                    self._failures.popitem(last=False)

                failures = deque()
                self._failures[key] = failures

            if len(failures) < self.failure_limit:
                failures.append(now)
