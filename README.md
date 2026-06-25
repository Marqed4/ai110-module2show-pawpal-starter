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

## 🖥️ Sample Output

```
=======================================================
        TODAY'S SCHEDULE
  Owner: Zachery  |  Available: 120 min
=======================================================

Daily plan for Lisa (cat):
  08:00 - 08:10  Morning feeding (10 min) [high]  -- Priority: high. Fits within remaining window (120 min left).
  08:10 - 08:20  Brushing (10 min) [medium]  -- Priority: medium. Fits within remaining window (110 min left).
  08:20 - 08:35  Litter box clean (15 min) [medium]  -- Priority: medium. Fits within remaining window (100 min left).
  08:35 - 08:55  Enrichment play (20 min) [low]  -- Priority: low. Fits within remaining window (85 min left).

Daily plan for Maggie (cat):
  08:00 - 08:05  Medication (5 min) [high]  -- Priority: high. Fits within remaining window (120 min left).
  08:05 - 08:15  Breakfast (10 min) [high]  -- Priority: high. Fits within remaining window (115 min left).
  08:15 - 08:30  Vet weight check (15 min) [medium]  -- Priority: medium. Fits within remaining window (105 min left).
  08:30 - 08:55  Lap time (25 min) [low]  -- Priority: low. Fits within remaining window (90 min left).

All done.
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sort by clock time | `Scheduler.sort_by_time()` | Sorts `ScheduledTask` objects by `start_time`; "HH:MM" zero-padding means lexicographic order equals chronological order — no datetime parsing needed |
| Sort by priority + time window | `Scheduler._sort_tasks()` | Pre-schedules tasks using a tuple key: preferred time window first (morning → afternoon → evening → any), then priority descending, then duration ascending to break ties |
| Filter by pet or status | `Owner.filter_tasks(pet_name, completed)` | Returns `(pet_name, Task)` pairs; omit either argument to skip that filter. Useful for "show me all pending tasks" or "show only Maggie's tasks" |
| Within-pet conflict detection | `Scheduler.detect_conflicts()` | Compares overlapping time windows after sorting; returns human-readable warning strings, never raises |
| Cross-pet conflict detection | `detect_cross_pet_conflicts(schedulers)` | Module-level function; checks all pets' schedules together since one owner cannot be in two places at once |
| Recurring tasks | `Task.next_occurrence(from_date)` | Returns a cloned `Task` due `timedelta(days=N)` later: daily=+1, weekly=+7, monthly=+30 |
| Complete and re-queue | `Pet.complete_task(title, today)` | Marks the matching task done and appends its next occurrence to the pet's task list automatically |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
