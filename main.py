from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Zachery", available_minutes=120, preferred_start_time="08:00")

lisa = Pet(name="Lisa", species="cat", breed="Domestic Shorthair")
lisa.add_task(Task(title="Morning feeding",   duration_minutes=10, priority="high"))
lisa.add_task(Task(title="Litter box clean",  duration_minutes=15, priority="medium"))
lisa.add_task(Task(title="Enrichment play",   duration_minutes=20, priority="low"))
lisa.add_task(Task(title="Brushing",          duration_minutes=10, priority="medium", frequency="weekly"))

maggie = Pet(name="Maggie", species="cat", breed="Domestic Longhair")
maggie.add_task(Task(title="Breakfast",       duration_minutes=10, priority="high"))
maggie.add_task(Task(title="Medication",      duration_minutes=5,  priority="high"))
maggie.add_task(Task(title="Lap time",        duration_minutes=25, priority="low"))
maggie.add_task(Task(title="Vet weight check",duration_minutes=15, priority="medium", frequency="weekly"))

owner.add_pet(lisa)
owner.add_pet(maggie)

# --- Schedule ---
print("=" * 55)
print("        TODAY'S SCHEDULE")
print(f"  Owner: {owner.name}  |  Available: {owner.available_minutes} min")
print("=" * 55)

for pet in owner.pets:
    scheduler = Scheduler(owner=owner, pet=pet)
    scheduler.generate(day_of_week=0)  # 0 = Monday, so weekly tasks are included
    print()
    print(scheduler.explain())

print()
print("All done.")
