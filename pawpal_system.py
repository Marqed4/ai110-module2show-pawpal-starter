from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low" | "medium" | "high"
    frequency: str = "daily"  # "daily" | "weekly"
    completed: bool = False

    def mark_complete(self) -> None:
        pass

    def priority_rank(self) -> int:
        pass


@dataclass
class Pet:
    name: str
    species: str
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, title: str) -> None:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferred_start_time: str = "08:00"  # "HH:MM"
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass


@dataclass
class ScheduledTask:
    task: Task
    start_time: str
    end_time: str
    reason: str


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet) -> None:
        self.owner = owner
        self.pet = pet
        self.schedule: list[ScheduledTask] = []

    def generate(self) -> list[ScheduledTask]:
        pass

    def _sort_tasks(self, tasks: list[Task]) -> list[Task]:
        pass

    def _fits_in_window(self, task: Task, remaining_minutes: int) -> bool:
        pass

    def explain(self) -> str:
        pass
