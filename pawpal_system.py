from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Literal


TIME_WINDOWS: dict[str, str] = {
    "morning": "06:00",
    "afternoon": "12:00",
    "evening": "17:00",
    "any": "",
}


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Literal["low", "medium", "high"] = "medium"
    frequency: Literal["daily", "weekly", "monthly"] = "daily"
    preferred_time: Literal["morning", "afternoon", "evening", "any"] = "any"
    completed: bool = False
    due_date: str | None = None  # "YYYY-MM-DD"

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def priority_rank(self) -> int:
        """Return a numeric rank for sorting: high=3, medium=2, low=1."""
        return {"low": 1, "medium": 2, "high": 3}[self.priority]

    def next_occurrence(self, from_date: date) -> "Task":
        """Return a new incomplete Task due on the next recurrence date.

        Uses timedelta so daily=+1 day, weekly=+7 days, monthly=+30 days.
        """
        intervals = {"daily": 1, "weekly": 7, "monthly": 30}
        next_due = from_date + timedelta(days=intervals[self.frequency])
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            preferred_time=self.preferred_time,
            completed=False,
            due_date=next_due.strftime("%Y-%m-%d"),
        )


@dataclass
class Pet:
    name: str
    species: str
    breed: str = ""
    age: int | None = None
    gender: Literal["male", "female", "unknown"] = "unknown"
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove all tasks whose title matches the given string."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def complete_task(self, title: str, today: date) -> Task | None:
        """Mark the first matching incomplete task done and queue its next occurrence.

        Returns the newly created Task, or None if no matching pending task was found.
        Monthly tasks also recur — only one-off tasks with no frequency would not.
        """
        for task in self.tasks:
            if task.title == title and not task.completed:
                task.mark_complete()
                next_task = task.next_occurrence(today)
                self.tasks.append(next_task)
                return next_task
        return None


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

    def filter_tasks(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
    ) -> list[tuple[str, Task]]:
        """Return (pet_name, task) pairs filtered by pet name and/or completion status.

        Pass pet_name to restrict to one pet. Pass completed=True/False to restrict
        by done state. Omit either to skip that filter.
        """
        results: list[tuple[str, Task]] = []
        for pet in self.pets:
            if pet_name is not None and pet.name != pet_name:
                continue
            for task in pet.tasks:
                if completed is not None and task.completed != completed:
                    continue
                results.append((pet.name, task))
        return results


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
            start_time = self._earliest_start(current_time, task.preferred_time)
            if not self._fits_in_window(task, remaining):
                continue
            end_time = self._time_after(start_time, task.duration_minutes)
            time_note = f" Preferred time: {task.preferred_time}." if task.preferred_time != "any" else ""
            reason = (
                f"Priority: {task.priority}.{time_note} "
                f"Fits within remaining window ({remaining} min left)."
            )
            self.schedule.append(
                ScheduledTask(
                    task=task,
                    start_time=start_time,
                    end_time=end_time,
                    reason=reason,
                )
            )
            current_time = end_time
            remaining -= task.duration_minutes

        return self.schedule

    def _sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort by preferred time window first, then priority descending, then duration ascending."""
        time_order = {"morning": 0, "afternoon": 1, "evening": 2, "any": 3}
        return sorted(
            tasks,
            key=lambda t: (time_order[t.preferred_time], -t.priority_rank(), t.duration_minutes),
        )

    def _fits_in_window(self, task: Task, remaining_minutes: int) -> bool:
        """Return True if the task duration fits within the remaining time."""
        return task.duration_minutes <= remaining_minutes

    def _filter_by_frequency(self, tasks: list[Task], day_of_week: int) -> list[Task]:
        """Keep daily tasks always; weekly and monthly only on Monday (day 0)."""
        return [
            t for t in tasks
            if t.frequency == "daily" or day_of_week == 0
        ]

    def _earliest_start(self, current_time: str, preferred_time: str) -> str:
        """Return current_time or the window start, whichever is later."""
        window_start = TIME_WINDOWS.get(preferred_time, "")
        if not window_start:
            return current_time
        fmt = "%H:%M"
        current_dt = datetime.strptime(current_time, fmt)
        window_dt = datetime.strptime(window_start, fmt)
        return window_start if window_dt > current_dt else current_time

    def _time_after(self, start: str, minutes: int) -> str:
        """Return a new HH:MM string that is `minutes` after `start`."""
        dt = datetime.strptime(start, "%H:%M") + timedelta(minutes=minutes)
        return dt.strftime("%H:%M")

    def sort_by_time(self) -> list[ScheduledTask]:
        """Return self.schedule sorted ascending by start_time.

        "HH:MM" strings are zero-padded, so lexicographic order equals
        chronological order — no datetime parsing needed.
        """
        return sorted(self.schedule, key=lambda st: st.start_time)

    def detect_conflicts(self) -> list[str]:
        """Return human-readable warnings for overlapping tasks within this pet's schedule.

        Compares time windows (start/end) rather than exact start matches, so a task
        that begins mid-way through another is still caught. Returns an empty list when
        there are no conflicts — never raises.
        """
        sorted_sched = self.sort_by_time()
        warnings: list[str] = []
        for i, a in enumerate(sorted_sched):
            for b in sorted_sched[i + 1:]:
                if b.start_time >= a.end_time:
                    break
                warnings.append(
                    f"WARNING [{self.pet.name}]: '{a.task.title}' "
                    f"({a.start_time}-{a.end_time}) overlaps "
                    f"'{b.task.title}' ({b.start_time}-{b.end_time})"
                )
        return warnings

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


def detect_cross_pet_conflicts(schedulers: list[Scheduler]) -> list[str]:
    """Return warnings for tasks across different pets that overlap in the owner's time.

    Because one owner must handle all pets, two tasks from different pets that share
    a time window cannot both be done at once. Collects every ScheduledTask from all
    schedulers, sorts by start time, then checks adjacent windows for overlap.
    Returns an empty list when there are no conflicts — never raises.
    """
    entries: list[tuple[str, ScheduledTask]] = [
        (s.pet.name, st)
        for s in schedulers
        for st in s.schedule
    ]
    entries.sort(key=lambda e: e[1].start_time)

    warnings: list[str] = []
    for i, (pet_a, a) in enumerate(entries):
        for pet_b, b in entries[i + 1:]:
            if b.start_time >= a.end_time:
                break
            if pet_a != pet_b:
                warnings.append(
                    f"WARNING [cross-pet]: '{pet_a}/{a.task.title}' "
                    f"({a.start_time}-{a.end_time}) overlaps "
                    f"'{pet_b}/{b.task.title}' ({b.start_time}-{b.end_time})"
                )
    return warnings
