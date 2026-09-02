from __future__ import annotations

import logging

from keep_sms_cron.keep_clients import KeepClient, Note
from keep_sms_cron.sms import SmsSender
from keep_sms_cron.state import NotifierState


def build_message(note: Note) -> str:
    title = note.title.strip() or "Untitled note"
    preview = " ".join(note.text.split())
    if len(preview) > 100:
        preview = preview[:97].rstrip() + "..."
    if preview:
        return f"New Google Keep note: {title} - {preview}"
    return f"New Google Keep note: {title}"


def run_once(
    keep_client: KeepClient,
    sms_sender: SmsSender,
    state: NotifierState,
    notify_existing: bool,
    label: str | None,
    logger: logging.Logger,
) -> int:
    notes = keep_client.list_notes(label=label)
    current_ids = {note.id for note in notes}

    first_run = not state.seen_note_ids and not state.notified_note_ids
    if first_run and not notify_existing:
        state.seen_note_ids.update(current_ids)
        logger.info("Initialized state with %s existing note(s)", len(current_ids))
        return 0

    new_notes = [note for note in notes if note.id not in state.seen_note_ids]
    sent_count = 0

    for note in new_notes:
        message_id = sms_sender.send(build_message(note))
        logger.info("Sent notification for note %s with message id %s", note.id, message_id)
        state.notified_note_ids.add(note.id)
        sent_count += 1

    state.seen_note_ids.update(current_ids)
    logger.info("Checked %s note(s), sent %s notification(s)", len(notes), sent_count)
    return sent_count
