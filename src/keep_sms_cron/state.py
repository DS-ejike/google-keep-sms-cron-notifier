from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class NotifierState:
    seen_note_ids: set[str] = field(default_factory=set)
    notified_note_ids: set[str] = field(default_factory=set)

    @classmethod
    def load(cls, path: Path) -> "NotifierState":
        if not path.exists():
            return cls()

        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            seen_note_ids=set(data.get("seen_note_ids", [])),
            notified_note_ids=set(data.get("notified_note_ids", [])),
        )

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "seen_note_ids": sorted(self.seen_note_ids),
            "notified_note_ids": sorted(self.notified_note_ids),
        }
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

