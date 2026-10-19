import streamlit as st

from datetime import datetime

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# Streamlit reruns this whole script on every click, so keep the Owner in
# session_state and only create it the first time.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=90)
owner = st.session_state.owner

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
# These write straight into the stored Owner object
owner.name = st.text_input("Owner name", value=owner.name)
owner.available_minutes = int(
    st.number_input(
        "Time available today (minutes)",
        min_value=1,
        max_value=1440,
        value=owner.available_minutes,
    )
)

st.subheader("Pets")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    add_pet_clicked = st.form_submit_button("Add pet")

if add_pet_clicked:
    if not pet_name.strip():
        st.error("Please enter a pet name.")
    else:
        owner.add_pet(Pet(name=pet_name.strip(), species=species))
        st.success(f"Added {pet_name.strip()}!")

if owner.pets:
    st.write("Your pets: " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")

if owner.pets:
    col0, col1, col2, col3 = st.columns(4)
    with col0:
        task_pet_name = st.selectbox("Pet", [p.name for p in owner.pets])
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    col4, col5 = st.columns(2)
    with col4:
        task_time = st.text_input("Preferred time (HH:MM, optional)", placeholder="07:30")
    with col5:
        frequency = st.selectbox("Repeats", ["daily", "weekly", "once"])

    if st.button("Add task"):
        time_value = task_time.strip() or None
        try:
            if time_value:
                time_value = datetime.strptime(time_value, "%H:%M").strftime("%H:%M")
        except ValueError:
            st.error("Time must look like HH:MM, for example 07:30.")
        else:
            pet = next(p for p in owner.pets if p.name == task_pet_name)
            pet.add_task(
                Task(
                    title=task_title,
                    duration_minutes=int(duration),
                    priority=priority,
                    frequency=frequency,
                    time=time_value,
                )
            )
            st.success(f"Added '{task_title}' for {pet.name}.")
else:
    st.caption("Add a pet first, then you can add tasks for it.")

scheduler = Scheduler(owner)

if owner.get_all_tasks():
    pending = {
        f"{pet.name}: {t.title}": (pet, t)
        for pet in owner.pets
        for t in pet.tasks
        if not t.completed
    }
    if pending:
        st.markdown("#### Mark a task done")
        done_label = st.selectbox("Task", list(pending))
        if st.button("Mark complete"):
            pet, task = pending[done_label]
            next_task = pet.mark_task_complete(task.title)
            if next_task is not None:
                st.success(
                    f"Done! Next '{task.title}' for {pet.name} is scheduled for "
                    f"{next_task.due_date:%a %b %d}."
                )
            else:
                st.success(f"Done! '{task.title}' won't repeat.")

    # Built after "Mark complete" runs so a newly created next occurrence is included
    pet_of = {id(t): pet.name for pet in owner.pets for t in pet.tasks}
    st.markdown("#### Your tasks")
    filter_pet, filter_status = st.columns(2)
    with filter_pet:
        pet_choice = st.selectbox("Show pet", ["All pets"] + [p.name for p in owner.pets])
    with filter_status:
        status_choice = st.selectbox("Show status", ["All", "Pending", "Completed"])

    shown = owner.filter_tasks(
        pet_name=None if pet_choice == "All pets" else pet_choice,
        completed={"All": None, "Pending": False, "Completed": True}[status_choice],
    )
    shown = scheduler.sort_by_time(shown)  # earliest first, untimed tasks last

    if shown:
        st.table(
            [
                {
                    "time": t.time or "-",
                    "pet": pet_of[id(t)],
                    "title": t.title,
                    "duration_minutes": t.duration_minutes,
                    "priority": t.priority,
                    "repeats": t.frequency,
                    "due": t.due_date.isoformat() if t.due_date else "today",
                    "status": "done" if t.completed else "pending",
                }
                for t in shown
            ]
        )
    else:
        st.info("No tasks match those filters.")

    # Conflict warnings: say which tasks clash, then what the owner can do about it
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        st.warning(f"{len(conflicts)} scheduling conflict(s) found. You can't be in two places at once!")
        for message in conflicts:
            st.warning(message, icon="⚠️")
        st.caption("To fix: change one task's preferred time, or shorten a task, then check again.")
    elif any(t.time and not t.completed for t in owner.get_all_tasks()):
        st.success("No time conflicts between your timed tasks.")

else:
    st.info("No tasks yet.")

st.divider()

st.subheader("Build Schedule")
st.caption("Builds a plan from every pet's tasks, highest priority first, within your available time.")

if st.button("Generate schedule"):
    if not owner.get_all_tasks():
        st.warning("Add at least one task first.")
    else:
        plan = scheduler.generate_plan()

        def clock(minute):
            return f"{minute // 60:02d}:{minute % 60:02d}"

        if plan.scheduled_tasks:
            st.success(f"Scheduled {len(plan.scheduled_tasks)} task(s), {plan.total_minutes} min total.")
            st.table(
                [
                    {
                        "time": f"{clock(start)}-{clock(start + t.duration_minutes)}",
                        "pet": pet_of[id(t)],
                        "task": t.title,
                        "priority": t.priority,
                    }
                    for t, start in plan.scheduled_tasks
                ]
            )
        for t, reason in plan.skipped_tasks:
            st.warning(f"Skipped '{t.title}' ({pet_of[id(t)]}): {reason}")
