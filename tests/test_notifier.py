from __future__ import annotations

import logging
import unittest

from keep_sms_cron.keep_clients import Note
from keep_sms_cron.notifier import build_message, run_once
from keep_sms_cron.state import NotifierState


class FakeKeepClient:
    def __init__(self, notes: list[Note]) -> None:
        self.notes = notes

    def list_notes(self, label: str | None = None) -> list[Note]:
        return self.notes


class FakeSmsSender:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def send(self, body: str) -> str:
        self.messages.append(body)
        return f"message-{len(self.messages)}"


class NotifierTests(unittest.TestCase):
    def test_first_run_baselines_existing_notes_by_default(self) -> None:
        note = Note(id="1", title="Existing", text="Do not send yet", updated="")
        state = NotifierState()
        sender = FakeSmsSender()

        sent = run_once(
            keep_client=FakeKeepClient([note]),
            sms_sender=sender,
            state=state,
            notify_existing=False,
            label=None,
            logger=logging.getLogger("test"),
        )

        self.assertEqual(sent, 0)
        self.assertEqual(sender.messages, [])
        self.assertEqual(state.seen_note_ids, {"1"})

    def test_new_note_sends_sms_after_baseline(self) -> None:
        state = NotifierState(seen_note_ids={"1"})
        sender = FakeSmsSender()
        notes = [
            Note(id="1", title="Old", text="", updated=""),
            Note(id="2", title="New idea", text="Ship the cron project", updated=""),
        ]

        sent = run_once(
            keep_client=FakeKeepClient(notes),
            sms_sender=sender,
            state=state,
            notify_existing=False,
            label=None,
            logger=logging.getLogger("test"),
        )

        self.assertEqual(sent, 1)
        self.assertEqual(sender.messages, ["New Google Keep note: New idea - Ship the cron project"])
        self.assertEqual(state.seen_note_ids, {"1", "2"})
        self.assertEqual(state.notified_note_ids, {"2"})

    def test_message_preview_is_shortened(self) -> None:
        note = Note(id="1", title="Long", text="x" * 140, updated="")

        message = build_message(note)

        self.assertLessEqual(len(message), 145)
        self.assertTrue(message.endswith("..."))


if __name__ == "__main__":
    unittest.main()

