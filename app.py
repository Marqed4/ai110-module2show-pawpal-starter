import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, detect_cross_pet_conflicts

'''
Later when expanding this project consider
RAG or SQLite for data persistence.
'''

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state bootstrap
# st.session_state acts as a persistent dictionary across reruns.
# We check for "owner" before creating one so reruns don't wipe existing data.
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Zachery", available_minutes=120)

owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# 1. Owner settings
# ---------------------------------------------------------------------------
with st.expander("Owner Settings", expanded=False):
    new_name = st.text_input("Owner name", value=owner.name)
    new_minutes = st.number_input(
        "Available minutes per day", min_value=10, max_value=480, value=owner.available_minutes
    )
    new_start = st.text_input("Start time (HH:MM)", value=owner.preferred_start_time)
    if st.button("Save owner info"):
        owner.name = new_name
        owner.available_minutes = int(new_minutes)
        owner.preferred_start_time = new_start
        st.success(f"Saved — {owner.name}, {owner.available_minutes} min starting {owner.preferred_start_time}")

# ---------------------------------------------------------------------------
# 2. Pets
# ---------------------------------------------------------------------------
st.subheader("Pets")

with st.form("add_pet_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        new_pet_name = st.text_input("Pet name")
    with col2:
        new_species = st.selectbox("Species", ["cat", "dog", "other"])
    with col3:
        new_breed = st.text_input("Breed (optional)")
    col4, col5 = st.columns(2)
    with col4:
        new_age = st.number_input("Age (years)", min_value=0, max_value=30, value=0, step=1)
    with col5:
        new_gender = st.selectbox("Gender", ["unknown", "male", "female"])
    submitted_pet = st.form_submit_button("Add pet")

if submitted_pet and new_pet_name.strip():
    existing_names = [p.name for p in owner.pets]
    if new_pet_name.strip() in existing_names:
        st.warning(f"{new_pet_name} is already added.")
    else:
        owner.add_pet(Pet(
            name=new_pet_name.strip(),
            species=new_species,
            breed=new_breed.strip(),
            age=int(new_age) if new_age > 0 else None,
            gender=new_gender,
        ))
        st.success(f"Added {new_pet_name}!")

if owner.pets:
    for pet in owner.pets:
        label = f"{pet.name} - {pet.species}"
        if pet.breed:
            label += f" ({pet.breed})"
        if pet.age is not None:
            label += f", {pet.age}yr"
        if pet.gender != "unknown":
            label += f", {pet.gender}"
        label += f" - {len(pet.tasks)} task(s)"
        st.caption(label)
else:
    st.info("No pets yet. Add one above.")

# ---------------------------------------------------------------------------
# 3. Tasks
# ---------------------------------------------------------------------------
st.subheader("Tasks")

if not owner.pets:
    st.info("Add a pet first before adding tasks.")
else:
    pet_names = [p.name for p in owner.pets]

    with st.form("add_task_form", clear_on_submit=True):
        target_pet_name = st.selectbox("Add task to", pet_names)
        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Task title")
        with col2:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=15)
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)
        col4, col5 = st.columns(2)
        with col4:
            frequency = st.radio("Frequency", ["daily", "weekly", "monthly"], horizontal=True)
        with col5:
            preferred_time = st.radio(
                "Time of day", ["any", "morning", "afternoon", "evening"], horizontal=True
            )
        submitted_task = st.form_submit_button("Add task")

    if submitted_task and task_title.strip():
        target_pet = next(p for p in owner.pets if p.name == target_pet_name)
        target_pet.add_task(
            Task(
                title=task_title.strip(),
                duration_minutes=int(duration),
                priority=priority,
                frequency=frequency,
                preferred_time=preferred_time,
            )
        )
        st.success(f"Added '{task_title}' to {target_pet_name}.")

    for pet in owner.pets:
        if pet.tasks:
            st.markdown(f"**{pet.name}'s tasks**")
            rows = [
                {
                    "Title": t.title,
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority,
                    "Frequency": t.frequency,
                    "Time of Day": t.preferred_time,
                    "Done": t.completed,
                }
                for t in pet.tasks
            ]
            st.table(rows)

# ---------------------------------------------------------------------------
# 4. Generate schedule
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Generate Schedule")

if not owner.pets:
    st.info("Add a pet and some tasks first.")
else:
    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    sched_pet_name = st.selectbox("Schedule for", [p.name for p in owner.pets], key="sched_select")
    day_label = st.selectbox("Day of week", DAYS)
    day_idx = DAYS.index(day_label)

    if st.button("Generate schedule"):
        sched_pet = next(p for p in owner.pets if p.name == sched_pet_name)
        scheduler = Scheduler(owner=owner, pet=sched_pet)
        result = scheduler.generate(day_of_week=day_idx)

        if not result:
            st.warning("No tasks could be scheduled — check task durations vs. available minutes.")
        else:
            st.success(f"Scheduled {len(result)} task(s) for {sched_pet.name} on {day_label}.")
            rows = [
                {
                    "Start": st_task.start_time,
                    "End": st_task.end_time,
                    "Task": st_task.task.title,
                    "Duration (min)": st_task.task.duration_minutes,
                    "Priority": st_task.task.priority,
                    "Reason": st_task.reason,
                }
                for st_task in result
            ]
            st.table(rows)
