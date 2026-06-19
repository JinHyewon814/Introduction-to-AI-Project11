import random

from .constants import TASK_COLORS


def random_task_color() -> str:
    return random.choice(TASK_COLORS)
