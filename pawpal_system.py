"""PawPal+ logic layer: backend classes for owners, pets, tasks, and scheduling."""

from dataclasses import dataclass, field

VALID_PRIORITIES = ("low", "medium", "high")
PRIORITY_ORDER = {"low": 1, "medium": 2, "high": 3}


def _format_time(minute: int) -> str:
    """Turn minutes from midnight into an HH:MM string."""
    return f"{minute // 60:02d}:{minute % 60:02d}"


@dataclass
class Task:
    """A single pet care activity (walk, feeding, meds, etc.)."""

    title: str
    duration_minutes: int
    priority: str  # one of VALID_PRIORITIES
    frequency: str = "daily"
    time: str | None = None  # optional preferred time, "HH:MM"
    completed: bool = False

    def __post_init__(self) -> None:
        """Reject priorities that aren't low, medium, or high."""
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(
                f"priority must be one of {VALID_PRIORITIES}, got {self.priority!r}"
            )

    def priority_value(self) -> int:
        """Convert the priority label into a number for sorting."""
        return PRIORITY_ORDER[self.priority]

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True


@dataclass
class Pet:
    """A pet and its list of care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        self.tasks.append(task)

    def edit_task(self, title: str, duration: int, priority: str) -> None:
        """Update the duration and priority of an existing task."""
        if priority not in VALID_PRIORITIES:
            raise ValueError(
                f"priority must be one of {VALID_PRIORITIES}, got {priority!r}"
            )
        for task in self.tasks:
            if task.title == title:
                task.duration_minutes = duration
                task.priority = priority
                return
        raise KeyError(f"No task titled {title!r} for {self.name}")

    def remove_task(self, title: str) -> None:
        """Remove a task by its title."""
        for task in self.tasks:
            if task.title == title:
                self.tasks.remove(task)
                return
        raise KeyError(f"No task titled {title!r} for {self.name}")


@dataclass
class Owner:
    """A pet owner with available time, preferences, and pets."""

    name: str
    available_minutes: int
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of the owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


@dataclass
class DailyPlan:
    """The result of scheduling: what got scheduled, what got skipped, and why."""

    # (task, start time in minutes from midnight), in the order they run
    scheduled_tasks: list[tuple[Task, int]] = field(default_factory=list)
    # (task, reason it was skipped)
    skipped_tasks: list[tuple[Task, str]] = field(default_factory=list)
    total_minutes: int = 0

    def add_scheduled(self, task: Task, start_minute: int) -> None:
        """Add a task at the given start time and add its duration to total_minutes."""
        self.scheduled_tasks.append((task, start_minute))
        self.total_minutes += task.duration_minutes

    def add_skipped(self, task: Task, reason: str) -> None:
        """Record a task that didn't fit, along with the reason."""
        self.skipped_tasks.append((task, reason))

    def explain(self) -> str:
        """Return the plan as text: scheduled tasks with times, then skipped tasks with reasons."""
        lines = []
        if self.scheduled_tasks:
            lines.append("Scheduled:")
            for task, start in self.scheduled_tasks:
                end = start + task.duration_minutes
                lines.append(
                    f"  {_format_time(start)}-{_format_time(end)}  {task.title} "
                    f"({task.duration_minutes} min) [priority: {task.priority}]"
                )
        else:
            lines.append("Nothing could be scheduled.")
        if self.skipped_tasks:
            lines.append("Skipped:")
            for task, reason in self.skipped_tasks:
                lines.append(f"  {task.title} - {reason}")
        lines.append(f"Total time: {self.total_minutes} min")
        return "\n".join(lines)


class Scheduler:
    """Builds a daily plan from the owner's tasks and available time."""

    def __init__(self, owner: Owner):
        """Store the owner whose pets' tasks will be scheduled."""
        self.owner = owner

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority (highest first), shorter tasks first within a priority."""
        return sorted(tasks, key=lambda t: (-t.priority_value(), t.duration_minutes))

    def generate_plan(self, start_minute: int = 8 * 60) -> DailyPlan:
        """Sort all pending tasks by priority and fit them into the owner's available time."""
        plan = DailyPlan()
        pending = [t for t in self.owner.get_all_tasks() if not t.completed]
        remaining = self.owner.available_minutes
        current = start_minute

        for task in self.sort_tasks(pending):
            if task.duration_minutes <= remaining:
                plan.add_scheduled(task, current)
                current += task.duration_minutes
                remaining -= task.duration_minutes
            else:
                plan.add_skipped(
                    task,
                    f"needs {task.duration_minutes} min but only {remaining} min left",
                )
        return plan
