from dataclasses import dataclass
from typing import Optional

@dataclass
class Task:
    id: int
    name: str
    duration: int = 0
    color: str = "#74A8FF"
    completed: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "duration": self.duration,
            "color": self.color,
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            id=data["id"],
            name=data["name"],
            duration=data.get("duration", 0),
            color=data.get("color", "#74A8FF"),
            completed=data.get("completed", False),
        )

@dataclass
class Block:
    task_id: int
    start: int
    length: int

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "start": self.start,
            "length": self.length,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Block":
        return cls(
            task_id=data["task_id"],
            start=data["start"],
            length=data["length"],
        )
