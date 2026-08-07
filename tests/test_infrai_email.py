"""Focused checks for retry and envelope handling."""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from infrai_email import InfraiEmail, InfraiError  # noqa: E402


class InfraiEmailTest(unittest.TestCase):
    @patch("infrai_email.time.sleep")
    @patch("infrai_email.requests.request")
    def test_retries_429_then_reads_data(self, request: Mock, sleep: Mock) -> None:
        limited = Mock(status_code=429, headers={"Retry-After": "2"})
        accepted = Mock(
            status_code=200,
            headers={},
            json=lambda: {"ok": True, "data": {"template_id": "tpl_42"}},
        )
        request.side_effect = [limited, accepted]

        client = InfraiEmail(api_key="test-key")
        data = client.create_template(
            name="academy-enrollment-run42",
            subject="Welcome",
            html="<p>Welcome</p>",
            idempotency_key="template:academy-enrollment-run42",
        )

        self.assertEqual(data["template_id"], "tpl_42")
        self.assertEqual(request.call_count, 2)
        sleep.assert_called_once_with(2.0)

    @patch("infrai_email.requests.request")
    def test_surfaces_envelope_error(self, request: Mock) -> None:
        request.return_value = Mock(
            status_code=400,
            headers={},
            json=lambda: {"ok": False, "error": {"message": "Invalid template"}},
        )
        client = InfraiEmail(api_key="test-key")

        with self.assertRaisesRegex(InfraiError, "Invalid template"):
            client.preview_template("tpl_42", {"student_name": "Mina"})


if __name__ == "__main__":
    unittest.main()
