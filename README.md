# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🛠️ Implementation Summary

I built the logic layer for PawPal+ in `pawpal_system.py`. It has five classes that work together:

- **Task** is one care activity (title, duration, priority, frequency, optional time, and whether it's done).
- **Pet** holds a pet's info and its list of tasks.
- **Owner** holds the owner's available time and all of their pets. `get_all_tasks()` collects every pet's tasks into one list.
- **Scheduler** gets the tasks from the owner (not from a single pet), sorts them by priority, and fits as many as it can into the available time.
- **DailyPlan** is the result: what got scheduled with start times, what got skipped and why, and an `explain()` method that prints it.

`main.py` is a quick terminal demo, and `tests/test_pawpal.py` has the first tests. The Streamlit app (`app.py`) isn't connected to the logic yet.

## 🖥️ Sample Output

Output from running `python main.py`:

```
Today's Schedule for Jordan (90 min available)
==================================================
Scheduled:
  08:00-08:10  Feeding (10 min) [priority: high]
  08:10-08:40  Morning walk (30 min) [priority: high]
  08:40-09:00  Play session (20 min) [priority: medium]
Skipped:
  Grooming - needs 45 min but only 30 min left
Total time: 60 min
```

## 🧪 Testing PawPal+

Run the tests from the project root:

```bash
python -m pytest
```

The 18 tests in `tests/test_pawpal.py` cover:

- **Sorting:** `sort_by_time()` returns chronological order, puts untimed tasks last, keeps ties in their original order, and handles an empty list.
- **Filtering:** `filter_tasks()` by pet, by status, by both, and with an unknown pet name.
- **Recurring tasks:** daily tasks recur the next day and weekly tasks 7 days later. One-off tasks don't recur. A task with no due date recurs from today. The next occurrence can recur again. Completing an unknown or already-finished task raises `KeyError`.
- **Conflict detection:** same-time tasks (same pet and different pets), partial overlaps, one long task covering several others, back-to-back tasks (not a conflict), completed and untimed tasks ignored, and a pet or owner with no tasks.
- **Basics:** marking a task complete and adding a task to a pet.

Test output:

```
============================= test session starts =============================
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\tkmar\Documents\codepath\ai110-module2show-pawpal-starter
plugins: anyio-4.15.1, platformdirs-4.13.0
collected 18 items

tests\test_pawpal.py ..................                                  [100%]

============================= 18 passed in 0.06s ==============================
```

**Confidence Level: ⭐⭐⭐⭐ (4/5)**

All 18 tests pass, and the sorting, recurrence, and conflict logic is covered including its edge cases. I'm not giving 5 because `Task.time` and `frequency` aren't validated (a bad value like `"abc"` would crash `detect_conflicts()`), `generate_plan()` isn't tested for how it handles preferred times or due dates, and the Streamlit UI has no tests.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_tasks()` | By time of day, or by priority then duration |
| Filtering | `Owner.filter_tasks()` | By pet name and/or completion status |
| Conflict detection | `Scheduler.detect_conflicts()` | Warns about overlapping timed tasks |
| Recurring tasks | `Task.mark_complete()`, `Pet.mark_task_complete()` | Daily and weekly tasks |

### Sorting
- **`Scheduler.sort_by_time(tasks)`** orders tasks by their `"HH:MM"` time, earliest first. Zero-padded times sort correctly as plain strings, so the key is `(t.time is None, t.time or "")`. Tasks with no time go last, and ties keep their original order.
- **`Scheduler.sort_tasks(tasks)`** is what `generate_plan()` uses. It orders by priority (high first), then shorter tasks first.

### Filtering
- **`Owner.filter_tasks(pet_name=None, completed=None)`** returns the matching tasks across all pets. Each argument is optional and `None` means "don't filter on this", so they combine: `filter_tasks(pet_name="Mochi", completed=False)` gives Mochi's pending tasks. An unknown pet name returns an empty list.

### Conflict detection
- **`Scheduler.detect_conflicts()`** returns a list of warning strings, one per overlapping pair. It never raises, and an empty list means no conflicts.
- It looks at pending tasks that have a time, across **all pets** (the owner can only be in one place). Two tasks conflict when one starts before the other ends. Tasks that only touch, like 09:00-09:30 and 09:30-10:00, don't conflict.
- Tasks are sorted by start time, and the inner loop stops at the first task that starts after the current one ends, so it doesn't compare every pair.
- Tradeoff: it only warns. It doesn't move tasks, and `generate_plan()` doesn't use preferred times yet.

```
WARNING: Conflict (Mochi and Luna): 'Grooming' 16:00-16:45 overlaps 'Vet call' starting 16:00
WARNING: Conflict for Mochi: 'Grooming' 16:00-16:45 overlaps 'Medication' starting 16:30
```

### Recurring tasks
- **`Task.mark_complete()`** marks the task done. For `daily` or `weekly` tasks it also returns a new, uncompleted copy with `due_date` moved forward 1 or 7 days. Other frequencies return `None`.
- **`Pet.mark_task_complete(title)`** is the method to call from the app. It completes the first pending task with that title and adds the next occurrence to the pet's task list. It raises `KeyError` if there is no pending task with that title.
- The next due date is counted from the task's own `due_date` (or today if it has none), so finishing a task late doesn't shift the routine.
- Tradeoff: `generate_plan()` doesn't filter by `due_date` yet, so future occurrences still appear in today's plan.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
