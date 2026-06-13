from typing import List

from .models import Block

class Scheduler:
    @staticmethod
    def can_place(blocks: List[Block], candidate_start: int, candidate_length: int, ignore_block_id: int | None = None) -> bool:
        candidate_end = candidate_start + candidate_length
        for block in blocks:
            if ignore_block_id is not None and block.task_id == ignore_block_id and block.start == candidate_start:
                continue
            existing_start = block.start
            existing_end = block.start + block.length
            if candidate_start < existing_end and existing_start < candidate_end:
                return False
        return True

    @staticmethod
    def get_occupied_cells(blocks: List[Block]) -> set[int]:
        occupied = set()
        for block in blocks:
            occupied.update(range(block.start, block.start + block.length))
        return occupied
