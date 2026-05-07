import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ApiClient:
    def __init__(self, base_url: str, timeout: int = 10) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout  = timeout
        self._session  = self._build_session()
        logger.info("ApiClient ready | base_url=%s", self._base_url)

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "Content-Type": "application/json",
            "Accept":       "application/json",
        })
        retry = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist={500, 502, 503, 504},
        )
        session.mount("https://", HTTPAdapter(max_retries=retry))
        session.mount("http://",  HTTPAdapter(max_retries=retry))
        return session

    def get(self, path: str, params: dict | None = None) -> requests.Response:
        url = f"{self._base_url}{path}"
        logger.info("GET  %s | params=%s", url, params)
        resp = self._session.get(url, params=params, timeout=self._timeout)
        self._log(resp)
        return resp

    def post(self, path: str, body: dict) -> requests.Response:
        url = f"{self._base_url}{path}"
        logger.info("POST %s | body=%s", url, body)
        resp = self._session.post(url, json=body, timeout=self._timeout)
        self._log(resp)
        return resp

    def put(self, path: str, body: dict) -> requests.Response:
        url = f"{self._base_url}{path}"
        logger.info("PUT  %s | body=%s", url, body)
        resp = self._session.put(url, json=body, timeout=self._timeout)
        self._log(resp)
        return resp

    def patch(self, path: str, body: dict) -> requests.Response:
        url = f"{self._base_url}{path}"
        logger.info("PATCH %s | body=%s", url, body)
        resp = self._session.patch(url, json=body, timeout=self._timeout)
        self._log(resp)
        return resp

    def delete(self, path: str) -> requests.Response:
        url = f"{self._base_url}{path}"
        logger.info("DEL  %s", url)
        resp = self._session.delete(url, timeout=self._timeout)
        self._log(resp)
        return resp

    def _log(self, resp: requests.Response) -> None:
        lvl = logging.WARNING if resp.status_code >= 400 else logging.DEBUG
        logger.log(lvl, "  → %d | elapsed=%dms",
                   resp.status_code, resp.elapsed.total_seconds() * 1000)

    def close(self) -> None:
        self._session.close()

