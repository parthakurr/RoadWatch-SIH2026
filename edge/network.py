"""
Backend reachability checks for the edge daemon.

Wi-Fi being connected is not enough — we probe the configured backend URL.
"""
import logging
from typing import Optional
from urllib.parse import urljoin

import requests

from config import BACKEND_CHECK_TIMEOUT_SEC, HEALTH_ENDPOINT

logger = logging.getLogger(__name__)


class NetworkMonitor:
    """Checks whether the central backend can be reached."""

    def __init__(
        self,
        backend_url: str,
        mock_offline: bool = False,
        timeout_sec: float = BACKEND_CHECK_TIMEOUT_SEC,
    ):
        self.backend_url = backend_url.rstrip("/")
        self.mock_offline = mock_offline
        self.timeout_sec = timeout_sec
        self._last_online: Optional[bool] = None

    def is_backend_reachable(self) -> bool:
        if self.mock_offline:
            self._log_state_change(False)
            logger.debug("[NETWORK] Mock offline mode — treating backend as unreachable")
            return False

        health_url = urljoin(self.backend_url + "/", HEALTH_ENDPOINT.lstrip("/"))
        try:
            response = requests.get(health_url, timeout=self.timeout_sec)
            online = response.status_code < 500
        except requests.RequestException as exc:
            logger.debug("[NETWORK] Backend probe failed: %s", exc)
            online = False

        self._log_state_change(online)
        return online

    def _log_state_change(self, online: bool) -> None:
        if self._last_online is None:
            logger.info("[NETWORK] %s", "Online" if online else "Offline")
        elif online != self._last_online:
            logger.info(
                "[NETWORK] %s",
                "Connection restored" if online else "Offline",
            )
        self._last_online = online
