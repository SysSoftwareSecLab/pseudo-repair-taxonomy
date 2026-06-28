"""Input/output helpers."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from .schema import RepairTrajectory


def load_trajectory(path: str | Path) -> RepairTrajectory:
    with Path(path).open("r", encoding="utf-8") as f:
        data = json.load(f)
    return RepairTrajectory.from_mapping(data)


def load_trajectories(path: str | Path) -> List[RepairTrajectory]:
    p = Path(path)
    if p.is_dir():
        return [load_trajectory(item) for item in sorted(p.glob("*.json"))]
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return [RepairTrajectory.from_mapping(item) for item in data]
    return [RepairTrajectory.from_mapping(data)]


def write_json(path: str | Path, payload) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")


def write_text(path: str | Path, text: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
