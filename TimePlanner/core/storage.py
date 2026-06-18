import json
from pathlib import Path
from datetime import date

from .models import Block, Task

DATA_FILE = Path(__file__).resolve().parents[0].parent / "data" / "planner.json"


def _serialize_tasks(tasks):
    return [task.to_dict() if isinstance(task, Task) else task for task in tasks]


def _serialize_blocks(blocks):
    return [block.to_dict() if isinstance(block, Block) else block for block in blocks]


class Storage:
    @staticmethod
    def load():
        if not DATA_FILE.exists():
            return None

        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if "days" in data:
            days = {}
            for day, day_data in data.get("days", {}).items():
                days[day] = {
                    "tasks": [Task.from_dict(item) for item in day_data.get("tasks", [])],
                    "blocks": [Block.from_dict(item) for item in day_data.get("blocks", [])],
                }

            selected_date = data.get("date") or date.today().isoformat()
            return {"date": selected_date, "days": days}

        # Backward compatibility for the old single-day planner.json format.
        selected_date = data.get("date") or date.today().isoformat()
        return {
            "date": selected_date,
            "days": {
                selected_date: {
                    "tasks": [Task.from_dict(item) for item in data.get("tasks", [])],
                    "blocks": [Block.from_dict(item) for item in data.get("blocks", [])],
                }
            },
        }

    @staticmethod
    def save(data: dict):
        payload = {
            "date": data["date"],
            "days": {
                day: {
                    "tasks": _serialize_tasks(day_data.get("tasks", [])),
                    "blocks": _serialize_blocks(day_data.get("blocks", [])),
                }
                for day, day_data in data.get("days", {}).items()
            },
        }
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2, ensure_ascii=False)
