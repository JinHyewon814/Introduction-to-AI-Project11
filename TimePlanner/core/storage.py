import json
from pathlib import Path
from typing import List

from .models import Block, Task

DATA_FILE = Path(__file__).resolve().parents[0].parent / "data" / "planner.json"

class Storage:
    @staticmethod
    def load():
        if not DATA_FILE.exists():
            return None

        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        tasks = [Task.from_dict(item) for item in data.get("tasks", [])]
        blocks = [Block.from_dict(item) for item in data.get("blocks", [])]
        return {
            "date": data.get("date", ""),
            "tasks": tasks,
            "blocks": blocks,
        }

    @staticmethod
    def save(date: str, tasks: List[Task], blocks: List[Block]):
        payload = {
            "date": date,
            "tasks": [task.to_dict() if isinstance(task, Task) else task for task in tasks],
            "blocks": [block.to_dict() if isinstance(block, Block) else block for block in blocks],
        }
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2, ensure_ascii=False)
