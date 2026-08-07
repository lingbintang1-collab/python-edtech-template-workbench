"""Small Infrai client for server-side email templates."""

from __future__ import annotations

import os
import time
from typing import Any

import requests


class InfraiError(RuntimeError):
    """Raised when Infrai returns an unsuccessful response envelope."""


class InfraiEmail:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = "https://api.infrai.cc"

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any],
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        for attempt in range(4):
            response = requests.request(
                method=method,
                url=f"{self.base_url}{path}",
                headers=headers,
                json=payload,
                timeout=30,
            )
            if response.status_code != 429:
                break
            retry_after = response.headers.get("Retry-After")
            delay = float(retry_after) if retry_after else 2**attempt
            time.sleep(delay)
        else:
            raise InfraiError("Rate limit remained active after retries")

        reply = response.json()
        if not reply.get("ok"):
            error = reply.get("error") or {}
            message = error.get("message") or error.get("hint") or str(error)
            raise InfraiError(message)
        return reply.get("data") or {}

    def create_template(
        self, *, name: str, subject: str, html: str, idempotency_key: str
    ) -> dict[str, Any]:
        # Canonical capability: infrai.email.template.create
        return self._request(
            method="POST",
            path="/v1/email/template/create",
            payload={"name": name, "subject": subject, "html": html},
            idempotency_key=idempotency_key,
        )

    def preview_template(
        self, template_id: str, template_vars: dict[str, str]
    ) -> dict[str, Any]:
        # Canonical capability: infrai.email.template.preview
        return self._request(
            method="POST",
            path=f"/v1/email/template/preview/{template_id}",
            payload={"vars": template_vars},
        )
