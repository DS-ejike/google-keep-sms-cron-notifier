from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class Note:
    id: str
    title: str
    text: str
    updated: str


class KeepClient(Protocol):
    def list_notes(self, label: str | None = None) -> list[Note]:
        """Return notes that should be considered for notifications."""


class MockKeepClient:
    def __init__(self, notes_file: Path) -> None:
        self.notes_file = notes_file

    def list_notes(self, label: str | None = None) -> list[Note]:
        if not self.notes_file.exists():
            return []

        raw_notes = json.loads(self.notes_file.read_text(encoding="utf-8"))
        notes: list[Note] = []
        for raw in raw_notes:
            labels = set(raw.get("labels", []))
            if label and label not in labels:
                continue
            notes.append(
                Note(
                    id=str(raw["id"]),
                    title=str(raw.get("title") or "Untitled note"),
                    text=str(raw.get("text") or ""),
                    updated=str(raw.get("updated") or ""),
                )
            )
        return notes


class GKeepApiClient:
    def __init__(self, email: str, master_token: str, device_id: str | None = None) -> None:
        try:
            import gkeepapi
        except ImportError as exc:
            raise RuntimeError("Install gkeepapi before using KEEP_BACKEND=gkeepapi") from exc

        self._keep = gkeepapi.Keep()
        self._keep.authenticate(email, master_token, device_id=device_id)

    def list_notes(self, label: str | None = None) -> list[Note]:
        self._keep.sync()
        notes: list[Note] = []

        for note in self._keep.all():
            if getattr(note, "trashed", False):
                continue
            if label and not self._has_label(note, label):
                continue

            timestamps = getattr(note, "timestamps", None)
            updated = str(getattr(timestamps, "updated", "") or "")
            notes.append(
                Note(
                    id=str(note.id),
                    title=str(note.title or "Untitled note"),
                    text=str(getattr(note, "text", "") or ""),
                    updated=updated,
                )
            )

        return notes

    @staticmethod
    def _has_label(note: object, label: str) -> bool:
        labels = getattr(note, "labels", None) or []
        return any(getattr(item, "name", "") == label for item in labels)


def build_keep_client(
    backend: str,
    mock_notes_file: Path,
    email: str,
    master_token: str,
    device_id: str | None,
) -> KeepClient:
    if backend == "mock":
        return MockKeepClient(mock_notes_file)
    if backend == "gkeepapi":
        return GKeepApiClient(email, master_token, device_id)
    raise ValueError(f"Unsupported Keep backend: {backend}")

