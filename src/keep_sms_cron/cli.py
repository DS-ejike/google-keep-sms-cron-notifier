from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

from keep_sms_cron.config import Config
from keep_sms_cron.keep_clients import build_keep_client
from keep_sms_cron.notifier import run_once
from keep_sms_cron.sms import build_sms_sender
from keep_sms_cron.state import NotifierState


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send SMS alerts for new Google Keep notes.")
    parser.add_argument("--once", action="store_true", help="Run one polling cycle and exit.")
    return parser.parse_args(argv)


def configure_logging(level: str) -> logging.Logger:
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    return logging.getLogger("keep_sms_cron")


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if not args.once:
        print("This command is intended for cron-style single runs. Use --once.", file=sys.stderr)
        return 2

    load_dotenv(Path(".env"))
    config = Config.from_env()
    logger = configure_logging(config.log_level)

    try:
        config.validate()
        keep_client = build_keep_client(
            backend=config.keep_backend,
            mock_notes_file=config.mock_notes_file,
            email=config.keep_google_email,
            master_token=config.keep_master_token,
            device_id=config.keep_device_id,
        )
        sms_sender = build_sms_sender(
            dry_run=config.dry_run,
            logger=logger,
            account_sid=config.twilio_account_sid,
            auth_token=config.twilio_auth_token,
            from_number=config.twilio_from_number,
            to_number=config.twilio_to_number,
        )
        state = NotifierState.load(config.state_file)
        run_once(
            keep_client=keep_client,
            sms_sender=sms_sender,
            state=state,
            notify_existing=config.notify_existing,
            label=config.keep_filter_label,
            logger=logger,
        )
        state.save(config.state_file)
        return 0
    except Exception:
        logger.exception("Notifier run failed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
