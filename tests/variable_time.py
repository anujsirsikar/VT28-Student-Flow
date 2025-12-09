import csv
import random
import matplotlib.pyplot as plt


# ============================================================
# Config
# ============================================================
DAYTIME_HOURS = 10           # 8am–6pm
NIGHT_HOURS = 4              # 6pm–10pm (for sunset events)
INSTRUCTORS = 20
INSTRUCTOR_DAILY_HOURS = 8
INSTRUCTOR_AVAILABLE_RATE = 0.7

MAX_DAYS = 365               # safety cutoff for sim

# ============================================================
# Data Structures
# ============================================================

class Event:
    def __init__(self, name, duration, sunset_required, resource):
        self.name = name
        self.duration = duration
        self.sunset = sunset_required
        self.resource = resource
        self.completed_day = None


class Student:
    def __init__(self, events_list, current_index=0, is_new=True):
        self.events = list(events_list)
        self.idx = current_index
        self.is_new = is_new
        self.finish_day = None

    def next_event(self):
        return None if self.idx >= len(self.events) else self.events[self.idx]


# ============================================================
# CSV loading
# ============================================================

def load_events_from_csv(path):
    """
    CSV format example:
    event_id,duration_hours,sunset,resource
    intro,2,False,classroom
    drive1,3,False,car
    night-park,2,True,car
    """

    ev_list = []
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ev_list.append(Event(
                row["event_id"],
                float(row["duration_hours"]),
                row["sunset"].lower()=="true",
                row["resource"]
            ))
    return ev_list


# ============================================================
# Scheduling Logic
# ============================================================

def schedule_one_day(students, day, classrooms, cars):
    events_to_attempt = []

    for s in students:
        nxt = s.next_event()
        if nxt and s.finish_day is None:
            events_to_attempt.append((s, nxt))

    # resource daily hour capacity
    classroom_hours = {c: DAYTIME_HOURS for c in classrooms}
    car_day_hours   = {c: DAYTIME_HOURS for c in cars}
    car_night_hours = {c: NIGHT_HOURS  for c in cars}

    instructors_available = int(INSTRUCTORS * INSTRUCTOR_AVAILABLE_RATE)
    instructor_hours = {i: INSTRUCTOR_DAILY_HOURS for i in range(instructors_available)}

    random.shuffle(events_to_attempt)

    for s, ev in events_to_attempt:

        need = ev.duration

        # pick resource pool
        if ev.resource=="classroom":
            pool = classroom_hours
        else:
            pool = car_night_hours if ev.sunset else car_day_hours

        rooms = [r for r,hrs in pool.items() if hrs>=need]
        if not rooms: 
            continue

        inst = [i for i,h in instructor_hours.items() if h>=need]
        if not inst:
            continue

        r = random.choice(rooms)
        i = random.choice(inst)

        pool[r] -= need
        instructor_hours[i] -= need

        ev.completed_day = day
        s.idx += 1

        if s.idx >= len(s.events):
            s.finish_day = day


# ============================================================
# Simulation Runner
# ============================================================

def simulate(intake_size, base_events, initial_students=70, runs=3):
    """
    intake_size = new students every 14 days
    initial_students detected as existing and don't affect stats
    """

    results=[]

    for _ in range(runs):
        
        # build student pool
        students=[]

        # Load initial students at random progress
        for _ in range(initial_students):
            start = random.randint(0, len(base_events)-1)
            students.append(Student(base_events, current_index=start, is_new=False))

        # New intake simulation
        day=0
        while day < MAX_DAYS:
            # Intake every 14 days
            if day % 14 == 0:
                for _ in range(intake_size):
                    students.append(Student(base_events, is_new=True))

            schedule_one_day(students, day, classrooms=["C1","C2","C3"], cars=["A","B","C","D","E"])

            # Stop early if all new students finished
            if all(s.finish_day is not None for s in students if s.is_new):
                break

            day += 1

        # collect completion times ONLY from new students
        new_times=[s.finish_day for s in students if s.is_new and s.finish_day is not None]

        results.append(sum(new_times)/len(new_times) if new_times else None)

    # average across runs
    return sum(r for r in results if r is not None)/len([r for r in results if r is not None])


# ============================================================
# Run Comparison + Plot
# ============================================================

def run_and_graph(base_events_csv):

    base_events = load_events_from_csv(base_events_csv)

    test_sizes=[1,2,3,4,5,6,7,8,9,10,11]
    averages=[]

    for size in test_sizes:
        avg = simulate(size, base_events)
        print(f"Intake {size:<3} → Avg completion {avg:.1f} days")
        averages.append(avg)

    # Plot
    plt.plot(test_sizes, averages, marker='o')
    plt.xlabel("Weekly New Student Intake Size")
    plt.ylabel("Average Completion Time (days)")
    plt.title("Student Throughput vs Class Size")
    plt.grid(True)
    plt.show()


# ============================================================
# Run
# ============================================================
run_and_graph("events.csv")
