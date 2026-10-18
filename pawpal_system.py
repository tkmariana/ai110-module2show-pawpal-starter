"""PawPal+ logic layer: backend classes for owners, pets, tasks, and scheduling."""

from dataclasses import dataclass, field


VALID_PRIORITIES = ("low", "medium", "high")


@dataclass
class Task:
    """A single pet care activity (walk, feeding, meds, etc.)."""

    title: str
    duration_minutes: int
    priority: str  # one of VALID_PRIORITIES
    frequency: str = "daily"

    def __post_init__(self) -> None:
        """Validate that priority is one of VALID_PRIORITIES (raise ValueError if not)."""
        pass

    def priority_value(self) -> int:
        """Convert the priority label into a number for sorting."""
        pass


@dataclass
class Pet:
    """A pet and its list of care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        pass

    def edit_task(self, title: str, duration: int, priority: str) -> None:
        """Update the duration and priority of an existing task."""
        pass

    def remove_task(self, title: str) -> None:
        """Remove a task by its title."""
        pass


@dataclass
class Owner:
    """A pet owner with available time, preferences, and pets."""

    name: str
    available_minutes: int
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of the owner's pets."""
        pass


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
        pass

    def add_skipped(self, task: Task, reason: str) -> None:
        """Record a task that didn't fit, along with the reason."""
        pass

    def explain(self) -> str:
        """Return a multi-line string: each scheduled task with its time range,
        then each skipped task with its reason."""
        pass


class Scheduler:
    """Builds a daily plan from the owner's tasks and available time."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority (highest first)."""
        pass

    def generate_plan(self, start_minute: int = 8 * 60) -> DailyPlan:
        """Build the day's plan.

        Steps: get all tasks from the owner, sort them with sort_tasks(), then walk
        through them tracking elapsed time. A task that fits within
        owner.available_minutes is added at the next start time; one that doesn't is
        skipped with a reason.
        """
        pass
