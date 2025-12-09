"""
Model reprezentujący zadanie w systemie producent-konsument
"""
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Task:
    """Reprezentacja zadania"""
    id: int
    description: str
    status: str  # pending, in_progress, done
    created_at: str
    started_at: str = ""
    completed_at: str = ""

    def to_dict(self):
        """Konwertuje zadanie do słownika"""
        return asdict(self)

    @staticmethod
    def from_dict(data: dict):
        """Tworzy zadanie z słownika"""
        return Task(**data)

