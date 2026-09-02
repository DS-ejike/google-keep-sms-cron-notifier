from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Config:
    keep_backend: str
    mock_notes_file: Path
    keep_google_email: str
    keep_master_token: str
    keep_device_id: str | None
    keep_filter_label: str | None
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_from_number: str
    twilio_to_number: str
    dry_run: bool
    notify_existing: bool
    state_file: Path
    log_level: str

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            keep_backend=os.getenv("KEEP_BACKEND", "mock").strip().lower(),
            mock_notes_file=Path(os.getenv("KEEP_MOCK_NOTES_FILE", "demo/notes.json")),
            keep_google_email=os.getenv("KEEP_GOOGLE_EMAIL", ""),
            keep_master_token=os.getenv("KEEP_MASTER_TOKEN", ""),
            keep_device_id=os.getenv("KEEP_DEVICE_ID") or None,
            keep_filter_label=os.getenv("KEEP_FILTER_LABEL") or None,
            twilio_account_sid=os.getenv("TWILIO_ACCOUNT_SID", ""),
            twilio_auth_token=os.getenv("TWILIO_AUTH_TOKEN", ""),
            twilio_from_number=os.getenv("TWILIO_FROM_NUMBER", ""),
            twilio_to_number=os.getenv("TWILIO_TO_NUMBER", ""),
            dry_run=_env_bool("DRY_RUN", True),
            notify_existing=_env_bool("NOTIFY_EXISTING", False),
            state_file=Path(os.getenv("STATE_FILE", ".state/keep-sms-cron.json")),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        )

    def validate(self) -> None:
        if self.keep_backend not in {"mock", "gkeepapi"}:
            raise ValueError("KEEP_BACKEND must be 'mock' or 'gkeepapi'")

        if self.keep_backend == "gkeepapi":
            missing = [
                name
                for name, value in {
                    "KEEP_GOOGLE_EMAIL": self.keep_google_email,
                    "KEEP_MASTER_TOKEN": self.keep_master_token,
                }.items()
                if not value
            ]
            if missing:
                raise ValueError(f"Missing Google Keep settings: {', '.join(missing)}")

        if not self.dry_run:
            missing = [
                name
                for name, value in {
                    "TWILIO_ACCOUNT_SID": self.twilio_account_sid,
                    "TWILIO_AUTH_TOKEN": self.twilio_auth_token,
                    "TWILIO_FROM_NUMBER": self.twilio_from_number,
                    "TWILIO_TO_NUMBER": self.twilio_to_number,
                }.items()
                if not value or value == "replace-me"
            ]
            if missing:
                raise ValueError(f"Missing Twilio settings: {', '.join(missing)}")

