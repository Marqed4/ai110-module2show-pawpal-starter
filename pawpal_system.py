from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Literal


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Literal["low", "medium", "high"] = "medium"
    frequency: Literal["daily", "weekly"] = "daily"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def priority_rank(self) -> int:
        """Return a numeric rank for sorting: high=3, medium=2, low=1."""
        return {"low": 1, "medium": 2, "high": 3}[self.priority]


@dataclass
class Pet:
    name: str
    species: str
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove all tasks whose title matches the given string."""
        self.tasks = [t for t in self.tasks if t.title != title]


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferred_start_time: str = "08:00"  # "HH:MM"
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all pets, in pet-list order."""
        return [task for pet in self.pets for task in pet.tasks]


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

    def generate(self, day_of_week: int = 0) -> list[ScheduledTask]:
        """Build a greedy schedule for the pet within the owner's available window."""
        self.schedule = []
        remaining = self.owner.available_minutes
        current_time = self.owner.preferred_start_time

        eligible = self._filter_by_frequency(self.pet.tasks, day_of_week)
        eligible = [t for t in eligible if not t.completed]
        sorted_tasks = self._sort_tasks(eligible)

        for task in sorted_tasks:
            if not self._fits_in_window(task, remaining):
                continue
            end_time = self._time_after(current_time, task.duration_minutes)
            reason = (
                f"Priority: {task.priority}. "
                f"Fits within remaining window ({remaining} min left)."
            )
            self.schedule.append(
                ScheduledTask(
                    task=task,
                    start_time=current_time,
                    end_time=end_time,
                    reason=reason,
                )
            )
            current_time = end_time
            remaining -= task.duration_minutes

        return self.schedule

    def _sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority descending, then duration ascending to break ties."""
        return sorted(tasks, key=lambda t: (-t.priority_rank(), t.duration_minutes))

    def _fits_in_window(self, task: Task, remaining_minutes: int) -> bool:
        """Return True if the task duration fits within the remaining time."""
        return task.duration_minutes <= remaining_minutes

    def _filter_by_frequency(self, tasks: list[Task], day_of_week: int) -> list[Task]:
        """Keep daily tasks always; include weekly tasks only on Monday (day 0)."""
        return [
            t for t in tasks
            if t.frequency == "daily" or day_of_week == 0
        ]

    def _time_after(self, start: str, minutes: int) -> str:
        """Return a new HH:MM string that is `minutes` after `start`."""
        dt = datetime.strptime(start, "%H:%M") + timedelta(minutes=minutes)
        return dt.strftime("%H:%M")

    def explain(self) -> str:
        """Return a human-readable summary of the current schedule."""
        if not self.schedule:
            return "No tasks were scheduled."
        lines = [f"Daily plan for {self.pet.name} ({self.pet.species}):"]
        for st in self.schedule:
            lines.append(
                f"  {st.start_time} - {st.end_time}  "
                f"{st.task.title} ({st.task.duration_minutes} min) "
                f"[{st.task.priority}]  -- {st.reason}"
            )
        return "\n".join(lines)
