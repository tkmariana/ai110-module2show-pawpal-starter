# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked it, in steps, to build the "smarter scheduling" layer on top of my basic classes: sort tasks by time, filter by pet and status, create the next task when a daily or weekly task is completed, warn about conflicting times, and then (challenge) add a third algorithm, `Scheduler.find_next_available_slot()`, which finds the earliest gap where a new task fits. I also asked it to write tests, docstrings, the README sections, and to connect the features to the Streamlit app.

**What did the agent do?**

Files modified:
- `pawpal_system.py`: added `Task.due_date`, `Task.mark_complete()` (returns the next occurrence), `Pet.mark_task_complete()`, `Owner.filter_tasks()`, `Scheduler.sort_by_time()`, `Scheduler.detect_conflicts()`, and `Scheduler.find_next_available_slot()`, with docstrings.
- `app.py`: time and repeat inputs, a sorted and filtered task table, conflict warnings, and a "Mark complete" button.
- `main.py`: demo with tasks added out of order, two deliberate conflicts, and the next free slot.
- `tests/test_pawpal.py`: grew from 2 to 22 tests.
- `README.md`, `reflection.md`, `diagrams/uml_final.mmd`: documentation.

It also ran `pytest` after each change, ran `main.py`, and drove the Streamlit app with Streamlit's `AppTest` to check the screens.

**What did you have to verify or fix manually?**

- The agent found and fixed a crash in `app.py` (a `KeyError` after "Mark complete", because the pet lookup was built before the new task existed). I only knew about it because the app test was run.
- Its first edit to `main.py` had a broken f-string, which showed up as a `SyntaxError` and was fixed.
- I stopped one file write (the UML diagram) so I could ask what it would change first, then approved it.
- I kept my own `detect_conflicts()` loop instead of a shorter `itertools.combinations` version it suggested, because mine stops early and reads better.
- Known gap I decided to leave: `generate_plan()` still ignores preferred times and due dates, so the plan and the conflict warnings can disagree.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
