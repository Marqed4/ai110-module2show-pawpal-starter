from pawpal_system import Task, Pet


def test_mark_complete_changes_status():
    task = Task(title="Morning feeding", duration_minutes=10, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Lisa", species="cat")
    assert len(pet.tasks) == 0
    pet.add_task(Task(title="Litter box clean", duration_minutes=15, priority="medium"))
    assert len(pet.tasks) == 1
    pet.add_task(Task(title="Enrichment play", duration_minutes=20, priority="low"))
    assert len(pet.tasks) == 2
