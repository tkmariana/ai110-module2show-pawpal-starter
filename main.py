"""Temporary testing ground: run the PawPal+ logic in the terminal."""

from pawpal_system import Owner, Pet, Scheduler, Task

# Owner with 90 minutes available today
owner = Owner(name="Jordan", available_minutes=90)

# Two pets
mochi = Pet(name="Mochi", species="dog")
luna = Pet(name="Luna", species="cat")
owner.add_pet(mochi)
owner.add_pet(luna)

# Tasks added deliberately out of time order (one with no time at all)
mochi.add_task(Task("Grooming", 45, "low", time="16:00"))
luna.add_task(Task("Play session", 20, "medium", time="18:00"))
mochi.add_task(Task("Morning walk", 30, "high", time="07:30"))
luna.add_task(Task("Litter box", 5, "medium"))
luna.add_task(Task("Feeding", 10, "high", time="08:00"))
# Deliberate conflicts: same time for a different pet, and an overlap within one pet
luna.add_task(Task("Vet call", 15, "medium", time="16:00"))
mochi.add_task(Task("Medication", 10, "high", time="16:30"))

# Mark one task done so the status filter has something to show
mochi.mark_task_complete("Morning walk")  # daily, so tomorrow's walk is added

scheduler = Scheduler(owner)


def show(label, tasks):
    print(f"\n{label}")
    for t in tasks:
        status = "done" if t.completed else "todo"
        print(f"  {t.time or '--:--'}  {t.title} ({status})")


show("As added:", owner.get_all_tasks())
show("Sorted by time:", scheduler.sort_by_time(owner.get_all_tasks()))
show("Mochi only:", owner.filter_tasks(pet_name="Mochi"))
show("Luna only, sorted:", scheduler.sort_by_time(owner.filter_tasks(pet_name="Luna")))
show("Pending:", owner.filter_tasks(completed=False))
show("Completed:", owner.filter_tasks(completed=True))
show("Mochi + pending:", owner.filter_tasks(pet_name="Mochi", completed=False))

print("\nConflict check:")
conflicts = scheduler.detect_conflicts()
for warning in conflicts:
    print(f"  WARNING: {warning}")
if not conflicts:
    print("  No conflicts.")

# Build and print the plan
plan = scheduler.generate_plan()

print(f"\nToday's Schedule for {owner.name} ({owner.available_minutes} min available)")
print("=" * 50)
print(plan.explain())
