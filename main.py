from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler, detect_cross_pet_conflicts

TODAY = date.today()

# --- Setup ---
owner = Owner(name="Zachery", available_minutes=120, preferred_start_time="08:00")

# Tasks added intentionally out of priority/time order to stress-test sorting.
lisa = Pet(name="Lisa", species="cat", breed="Domestic Shorthair")
lisa.add_task(Task(title="Enrichment play",  duration_minutes=20, priority="low",    preferred_time="afternoon"))
lisa.add_task(Task(title="Morning feeding",  duration_minutes=10, priority="high",   preferred_time="morning",  due_date=TODAY.strftime("%Y-%m-%d")))
lisa.add_task(Task(title="Brushing",         duration_minutes=10, priority="medium", frequency="weekly"))
lisa.add_task(Task(title="Litter box clean", duration_minutes=15, priority="medium", preferred_time="morning"))

maggie = Pet(name="Maggie", species="cat", breed="Domestic Longhair")
maggie.add_task(Task(title="Lap time",        duration_minutes=25, priority="low",    preferred_time="evening"))
maggie.add_task(Task(title="Medication",      duration_minutes=5,  priority="high",   preferred_time="morning",  due_date=TODAY.strftime("%Y-%m-%d")))
maggie.add_task(Task(title="Vet weight check",duration_minutes=15, priority="medium", frequency="weekly"))
maggie.add_task(Task(title="Breakfast",       duration_minutes=10, priority="high",   preferred_time="morning",  due_date=TODAY.strftime("%Y-%m-%d")))

owner.add_pet(lisa)
owner.add_pet(maggie)

SEP = "=" * 55

# ---------------------------------------------------------------------------
# 1. Generate and display schedules
# ---------------------------------------------------------------------------
print(SEP)
print("        TODAY'S SCHEDULE  (Monday - all frequencies)")
print(f"  Owner: {owner.name}  |  Available: {owner.available_minutes} min")
print(SEP)

schedulers: dict[str, Scheduler] = {}
for pet in owner.pets:
    s = Scheduler(owner=owner, pet=pet)
    s.generate(day_of_week=0)
    schedulers[pet.name] = s
    print()
    print(s.explain())

# ---------------------------------------------------------------------------
# 2. sort_by_time  -- re-print Lisa's schedule sorted by clock time
# ---------------------------------------------------------------------------
print()
print(SEP)
print("  LISA'S SCHEDULE SORTED BY START TIME")
print(SEP)
for st in schedulers["Lisa"].sort_by_time():
    print(f"  {st.start_time} - {st.end_time}  {st.task.title} [{st.task.priority}]")

# ---------------------------------------------------------------------------
# 3. filter_tasks  -- incomplete tasks only, then tasks for a single pet
# ---------------------------------------------------------------------------
print()
print(SEP)
print("  INCOMPLETE TASKS (all pets)")
print(SEP)
for pet_name, task in owner.filter_tasks(completed=False):
    print(f"  [{pet_name}]  {task.title}  ({task.priority})")

print()
print(SEP)
print("  MAGGIE'S TASKS ONLY (any status)")
print(SEP)
for pet_name, task in owner.filter_tasks(pet_name="Maggie"):
    status = "done" if task.completed else "pending"
    print(f"  {task.title}  [{task.priority}]  {status}")

# ---------------------------------------------------------------------------
# 4. detect_conflicts
# ---------------------------------------------------------------------------
print()
print(SEP)
print("  WITHIN-PET CONFLICT DETECTION")
print(SEP)
for pet in owner.pets:
    warnings = schedulers[pet.name].detect_conflicts()
    if warnings:
        for w in warnings:
            print(f"  {w}")
    else:
        print(f"  {pet.name}: no within-pet conflicts detected")

print()
print(SEP)
print("  CROSS-PET CONFLICT DETECTION")
print("  (owner must attend to both pets - overlap = can't do both)")
print(SEP)
cross_warnings = detect_cross_pet_conflicts(list(schedulers.values()))
if cross_warnings:
    for w in cross_warnings:
        print(f"  {w}")
else:
    print("  No cross-pet conflicts detected")

# ---------------------------------------------------------------------------
# 5. Recurrence -- complete a daily and a weekly task, inspect next instances
# ---------------------------------------------------------------------------
print()
print(SEP)
print("  TASK RECURRENCE")
print(SEP)

# Complete Lisa's daily "Morning feeding" -> next due tomorrow
next_feeding = lisa.complete_task("Morning feeding", TODAY)
print(f"  Completed: 'Morning feeding' (daily)")
print(f"  Next occurrence due: {next_feeding.due_date}  (today + 1 day = {TODAY} + 1)")

print()

# Complete Maggie's weekly "Vet weight check" -> next due in 7 days
next_vet = maggie.complete_task("Vet weight check", TODAY)
print(f"  Completed: 'Vet weight check' (weekly)")
print(f"  Next occurrence due: {next_vet.due_date}  (today + 7 days = {TODAY} + 7)")

print()

# Show that both pets now have the queued next-occurrence task
print("  Lisa's task list after completion:")
for t in lisa.tasks:
    status = "done" if t.completed else f"due {t.due_date or 'anytime'}"
    print(f"    {t.title}  [{t.frequency}]  {status}")

print()
print("  Maggie's task list after completion:")
for t in maggie.tasks:
    status = "done" if t.completed else f"due {t.due_date or 'anytime'}"
    print(f"    {t.title}  [{t.frequency}]  {status}")

print()
print("All done.")
