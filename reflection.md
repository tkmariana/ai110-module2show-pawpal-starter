# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

**Core user actions**

Based on the PawPal+ scenario, the three core actions a user should be able to perform are:

1. **Enter owner and pet information** – The user sets up a profile with basic owner details (name, how much time they have available each day, preferences) and their pet's info (name, species/breed). This gives the scheduler the context it needs.
2. **Add and edit care tasks** – The user creates pet care tasks such as walks, feeding, medication, enrichment, or grooming. Each task needs at least a duration and a priority, and the user can update them later as needs change.
3. **Generate and view today's plan** – The user asks the app to build a daily schedule that fits their available time and puts higher-priority tasks first. The plan is displayed clearly, along with an explanation of why tasks were chosen, ordered, or skipped.

**Initial UML design**

My design is pretty simple. An owner has pets, each pet has tasks, and a scheduler looks at the tasks and the owner's free time to make a daily plan. I kept all the scheduling logic in one class so it's easier to test.

**Classes and responsibilities**

- **Owner** – keeps the owner's name, how much time they have today, and their pets.
- **Pet** – keeps the pet's name and species, and its list of tasks.
- **Task** – one care activity (walk, feeding, meds, etc.) with a duration and priority.
- **Scheduler** – sorts tasks by priority and fits them into the available time.
- **DailyPlan** – the final schedule, plus which tasks got skipped and why.

**b. Design changes**

Yes. AI generated the class skeleton from my UML, and then I asked it to review its own skeleton for missing pieces. Based on that feedback I changed a few things:

- `DailyPlan` now saves the reason a task was skipped, because before it accepted a reason but had nowhere to store it.
- `DailyPlan` now saves a start time for each scheduled task, so the plan can say when things happen.
- A task's priority can only be low, medium, or high, so a typo doesn't break the sorting.

I made these changes so the plan can explain itself, and I updated `uml.mmd` to match.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler looks at the owner's available minutes, each task's priority and duration, and whether a task is already done. Preferred times are used for sorting and conflict warnings, but not yet for building the plan. The `preferences` field exists but isn't used.

I put priority first and available time second, because a pet's essential care (meds, feeding) has to happen before extras like play or grooming. Shorter tasks go first within a priority so more of them fit.

**b. Tradeoffs**

My conflict check only warns the owner; it never moves or drops a task. `detect_conflicts()` flags any overlapping timed tasks across all pets, but `generate_plan()` still ignores preferred times. This is reasonable because only the owner knows which task can move, and auto-fixing could quietly reschedule something important like medication. The cost is that the owner has to resolve conflicts by hand.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI to turn my idea into a UML diagram, generate the class skeleton from it, fill in the methods, and write the first tests and the `main.py` demo. The most helpful prompt was asking it to review its own skeleton for missing relationships and logic problems, because that is how I found the gaps in `DailyPlan`.

**b. Judgment and verification**

When AI reviewed the skeleton, it first suggested saving skipped reasons and start times in a dictionary keyed by task. I didn't use that, because dataclasses can't be dictionary keys by default, so it would have crashed. I used lists of pairs instead. To check the code, I ran `main.py` with two pets and read the schedule it printed, and I wrote two pytest tests that both pass.

**c. AI strategy**

- **Most effective features:** asking the AI to review its own work (it found the gaps in `DailyPlan`), having it write tests next to each new method, and letting it run the tests and the app after every change so I could see things actually working.
- **A suggestion I didn't take:** for `detect_conflicts()`, the AI offered a shorter version using `itertools.combinations`. I kept my own nested loop because it stops early once tasks are sorted, and it is easier for me to read and explain.

---

## 4. Testing and Verification

**a. What you tested**

I wrote 18 pytest tests. They cover sorting by time (including untimed tasks and ties), filtering by pet and status, daily and weekly recurrence, conflict detection (same time, partial overlap, back-to-back, completed tasks), and errors like completing a task that doesn't exist. I tested these because they are the parts with real logic, and the edge cases are where a scheduler usually breaks.

**b. Confidence**

I'm fairly confident (4 out of 5) in sorting, filtering, recurrence and conflict detection, since all 18 tests pass. I'm less sure about `generate_plan()` and the app screen, which have no tests for preferred times or due dates. Next I would test invalid times like `"25:99"`, tasks that run past midnight, and two pets with the same name.

---

## 5. Reflection

**a. What went well**

I'm happiest with the conflict warnings. They catch overlaps between different pets, not just identical times, and they show up in the app in plain language instead of crashing.

**b. What you would improve**

I would make `generate_plan()` use preferred times and due dates, so the plan and the conflict warnings agree. I would also add a task id so tasks with the same title don't get mixed up, and validate `time` and `frequency` when a task is created.

**c. Key takeaway**

The AI writes code fast, but the design choices were still mine to make: should conflicts warn or block, does a preferred time anchor a task, and which class owns recurring tasks. Being the lead architect meant deciding those first, then checking each result by running the tests instead of trusting that it looked right.
