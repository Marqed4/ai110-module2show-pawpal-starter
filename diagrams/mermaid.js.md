```mermaid
classDiagram
    class Owner {
        +str name
        +int available_minutes
        +str preferred_start_time
        +list~Pet~ pets
        +add_pet(pet: Pet) void
        +get_all_tasks() list~Task~
    }

    class Pet {
        +str name
        +str species
        +str breed
        +int|None age
        +Literal gender
        +list~Task~ tasks
        +add_task(task: Task) void
        +remove_task(title: str) void
    }

    class Task {
        +str title
        +int duration_minutes
        +Literal priority
        +Literal frequency
        +Literal preferred_time
        +bool completed
        +mark_complete() void
        +priority_rank() int
    }

    class ScheduledTask {
        +Task task
        +str start_time
        +str end_time
        +str reason
    }

    class Scheduler {
        +Owner owner
        +Pet pet
        +list~ScheduledTask~ schedule
        +generate(day_of_week: int) list~ScheduledTask~
        +_sort_tasks(tasks: list) list
        +_fits_in_window(task: Task, remaining: int) bool
        +_filter_by_frequency(tasks: list, day_of_week: int) list
        +_earliest_start(current_time: str, preferred_time: str) str
        +_time_after(start: str, minutes: int) str
        +explain() str
    }

    Owner "1" --> "1..*" Pet : owns
    Pet "1" --> "0..*" Task : has
    Scheduler --> Owner : uses
    Scheduler --> Pet : schedules for
    Scheduler "1" --> "0..*" ScheduledTask : produces
    ScheduledTask --> Task : wraps
```
