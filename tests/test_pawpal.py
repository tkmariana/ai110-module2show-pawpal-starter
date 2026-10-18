from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    task = Task("Morning walk", 30, "high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Feeding", 10, "high"))

    assert len(pet.tasks) == 1


def test_daily_task_creates_next_occurrence_tomorrow():
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task("Walk", 30, "high", frequency="daily", due_date=date(2026, 1, 1)))

    nxt = pet.mark_task_complete("Walk")

    assert pet.tasks[0].completed is True
    assert nxt is not None and nxt.completed is False
    assert nxt.due_date == date(2026, 1, 2)
    assert pet.tasks == [pet.tasks[0], nxt]


def test_weekly_task_creates_next_occurrence_in_seven_days():
    pet = Pet(name="Luna", species="cat")
    pet.add_task(Task("Grooming", 20, "low", frequency="weekly", due_date=date(2026, 1, 1)))

    nxt = pet.mark_task_complete("Grooming")

    assert nxt.due_date == date(2026, 1, 8)


def test_one_off_task_does_not_recur():
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task("Vet visit", 60, "high", frequency="once"))

    assert pet.mark_task_complete("Vet visit") is None
    assert len(pet.tasks) == 1


def _owner_with(*pet_tasks):
    owner = Owner(name="Jordan", available_minutes=120)
    for pet_name, tasks in pet_tasks:
        pet = Pet(name=pet_name, species="dog")
        for task in tasks:
            pet.add_task(task)
        owner.add_pet(pet)
    return owner


def test_conflict_detected_across_pets_at_same_time():
    owner = _owner_with(
        ("Mochi", [Task("Walk", 30, "high", time="09:00")]),
        ("Luna", [Task("Vet call", 15, "medium", time="09:00")]),
    )

    warnings = Scheduler(owner).detect_conflicts()

    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Vet call" in warnings[0]


def test_back_to_back_tasks_are_not_a_conflict():
    owner = _owner_with(
        ("Mochi", [Task("Walk", 30, "high", time="09:00"), Task("Feed", 10, "high", time="09:30")])
    )

    assert Scheduler(owner).detect_conflicts() == []


def test_untimed_and_completed_tasks_are_ignored():
    done = Task("Walk", 30, "high", time="09:00", completed=True)
    owner = _owner_with(
        ("Mochi", [done, Task("Feed", 10, "high", time="09:00"), Task("Play", 10, "low")])
    )

    assert Scheduler(owner).detect_conflicts() == []
