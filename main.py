"""Temporary testing ground: run the PawPal+ logic in the terminal."""

from pawpal_system import Owner, Pet, Scheduler, Task

# Owner with 90 minutes available today
owner = Owner(name="Jordan", available_minutes=90)

# Two pets
mochi = Pet(name="Mochi", species="dog")
luna = Pet(name="Luna", species="cat")
owner.add_pet(mochi)
owner.add_pet(luna)

# Tasks with different preferred times
mochi.add_task(Task("Morning walk", 30, "high", time="07:30"))
mochi.add_task(Task("Grooming", 45, "low", time="16:00"))
luna.add_task(Task("Feeding", 10, "high", time="08:00"))
luna.add_task(Task("Play session", 20, "medium", time="18:00"))

# Build and print the plan
plan = Scheduler(owner).generate_plan()

print(f"Today's Schedule for {owner.name} ({owner.available_minutes} min available)")
print("=" * 50)
print(plan.explain())
