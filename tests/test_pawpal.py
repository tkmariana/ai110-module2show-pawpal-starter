from datetime import date, timedelta

import pytest

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


# ---- Sorting ----

def test_sort_by_time_is_chronological_with_untimed_last():
    owner = _owner_with(
        ("Mochi", [Task("Dinner", 10, "low", time="18:00"), Task("Litter", 5, "low")]),
        ("Luna", [Task("Walk", 30, "high", time="07:30"), Task("Lunch", 10, "low", time="12:15")]),
    )

    ordered = Scheduler(owner).sort_by_time(owner.get_all_tasks())

    assert [t.title for t in ordered] == ["Walk", "Lunch", "Dinner", "Litter"]


def test_sort_by_time_keeps_original_order_for_ties():
    a = Task("A", 10, "low", time="09:00")
    b = Task("B", 10, "high", time="09:00")
    owner = _owner_with(("Mochi", [a, b]))

    assert Scheduler(owner).sort_by_time([a, b]) == [a, b]


def test_sort_by_time_handles_empty_list():
    assert Scheduler(Owner("Jordan", 60)).sort_by_time([]) == []


# ---- Filtering ----

def test_filter_by_pet_and_status():
    done = Task("Walk", 30, "high", completed=True)
    owner = _owner_with(
        ("Mochi", [done, Task("Feed", 10, "high")]),
        ("Luna", [Task("Play", 10, "low")]),
    )

    assert owner.filter_tasks(pet_name="Mochi") == owner.pets[0].tasks
    assert owner.filter_tasks(completed=True) == [done]
    assert [t.title for t in owner.filter_tasks(pet_name="Mochi", completed=False)] == ["Feed"]
    assert owner.filter_tasks(pet_name="Nobody") == []


# ---- Recurrence edge cases ----

def test_completing_unknown_or_already_completed_task_raises():
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task("Walk", 30, "high", frequency="once"))
    pet.mark_task_complete("Walk")

    with pytest.raises(KeyError):
        pet.mark_task_complete("Walk")  # already done
    with pytest.raises(KeyError):
        pet.mark_task_complete("Nope")


def test_recurring_task_with_no_due_date_recurs_from_today():
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task("Walk", 30, "high", frequency="daily"))

    nxt = pet.mark_task_complete("Walk")

    assert nxt.due_date == date.today() + timedelta(days=1)


def test_next_occurrence_is_a_separate_task_that_can_recur_again():
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task("Walk", 30, "high", due_date=date(2026, 1, 1)))

    second = pet.mark_task_complete("Walk")
    third = pet.mark_task_complete("Walk")

    assert second is not pet.tasks[0]
    assert third.due_date == date(2026, 1, 3)
    assert len(pet.tasks) == 3


# ---- Conflict edge cases ----

def test_two_tasks_for_same_pet_at_exact_same_time_conflict():
    owner = _owner_with(
        ("Mochi", [Task("Walk", 30, "high", time="09:00"), Task("Bath", 20, "low", time="09:00")])
    )

    warnings = Scheduler(owner).detect_conflicts()

    assert len(warnings) == 1
    assert "for Mochi" in warnings[0]


def test_one_long_task_conflicts_with_each_task_inside_it():
    owner = _owner_with(
        ("Mochi", [
            Task("Grooming", 90, "low", time="10:00"),
            Task("Meds", 5, "high", time="10:15"),
            Task("Treat", 5, "low", time="11:00"),
        ])
    )

    assert len(Scheduler(owner).detect_conflicts()) == 2


def test_pet_with_no_tasks_and_owner_with_no_pets_have_no_conflicts():
    assert Scheduler(Owner("Jordan", 60)).detect_conflicts() == []
    assert Scheduler(_owner_with(("Mochi", []))).detect_conflicts() == []
