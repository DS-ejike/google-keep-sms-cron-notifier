from __future__ import annotations

import logging
from typing import Protocol


class SmsSender(Protocol):
    def send(self, body: str) -> str:
        """Send an SMS message and return a provider message id."""


class DryRunSmsSender:
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def send(self, body: str) -> str:
        self.logger.info("DRY_RUN SMS: %s", body)
        return "dry-run"


class TwilioSmsSender:
    def __init__(
        self,
        account_sid: str,
        auth_token: str,
        from_number: str,
        to_number: str,
    ) -> None:
        try:
            from twilio.rest import Client
        except ImportError as exc:
            raise RuntimeError("Install twilio before setting DRY_RUN=false") from exc

        self._client = Client(account_sid, auth_token)
        self._from_number = from_number
        self._to_number = to_number

    def send(self, body: str) -> str:
        message = self._client.messages.create(
            body=body,
            from_=self._from_number,
            to=self._to_number,
        )
        return str(message.sid)


def build_sms_sender(
    dry_run: bool,
    logger: logging.Logger,
    account_sid: str,
    auth_token: str,
    from_number: str,
    to_number: str,
) -> SmsSender:
    if dry_run:
        return DryRunSmsSender(logger)
    return TwilioSmsSender(account_sid, auth_token, from_number, to_number)

