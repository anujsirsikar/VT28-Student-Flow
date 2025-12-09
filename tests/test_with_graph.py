import pandas as pd
import random
import matplotlib.pyplot as plt

# ==========================================================
# CONFIG — Modify these for global settings
# ==========================================================

CLASS_EVENTS = 10
CAR_EVENTS = 60
EVENTS_PER_STUDENT = CLASS_EVENTS + CAR_EVENTS

CLASSROOMS = 17
CARS = 10
SLOTS_PER_RESOURCE_PER_DAY = 4

INSTRUCTORS = 20
INSTRUCTOR_CAPACITY_PER_DAY = 3
INSTRUCTOR_AVAILABILITY_PROB = 0.70


# ==========================================================
# Student Class
# ==========================================================

class Student:
    def __init__(self, sid, start_day):
        self.sid = sid
        self.start_day = start_day
        self.class_events_done = 0
        self.car_events_done = 0
        self.last_event_day = -999
        self.finish_day = None

    @property
    def total_events(self):
        return self.class_events_done + self.car_events_done

    @property
    def completed(self):
        return self.total_events >= EVENTS_PER_STUDENT


# ==========================================================
# SIMULATION FUNCTION
# ==========================================================

def run_simulation(
        initial_students=10,
        new_students_count=10,
        new_students_every=14,
        sim_days=120,
        return_details=False,
        seed=None):

    if seed is not None:
        random.seed(seed)

    students = []
    sid_counter = 0

    for _ in range(initial_students):
        students.append(Student(sid_counter, 0))
        sid_counter += 1

    schedule_log = []
    completion_log = []

    for day in range(sim_days):

        # --- Skip weekends (Sat/Sun) ---
        if day % 7 in (5, 6):
            continue

        # --- Add new students bi-weekly ---
        if day % new_students_every == 0 and day != 0:
            for _ in range(new_students_count):
                students.append(Student(sid_counter, day))
                sid_counter += 1

        # --- Instructor availability ---
        instructors = []
        for i in range(INSTRUCTORS):
            if random.random() < INSTRUCTOR_AVAILABILITY_PROB:
                instructors.append([i, INSTRUCTOR_CAPACITY_PER_DAY])

        total_instructor_capacity = sum(x[1] for x in instructors)

        remaining_class_slots = CLASSROOMS * SLOTS_PER_RESOURCE_PER_DAY
        remaining_car_slots = CARS * SLOTS_PER_RESOURCE_PER_DAY

        # Students ordered by longest time waiting
        waiting = sorted(
            [s for s in students if not s.completed],
            key=lambda s: (day - s.last_event_day),
            reverse=True
        )

        # --- Assign events for the day ---
        for s in waiting:
            if total_instructor_capacity <= 0:
                break

            # Determine which track of syllabus student is in
            if s.class_events_done < CLASS_EVENTS and remaining_class_slots > 0:
                event_type = "CLASS"
                remaining_class_slots -= 1

            elif s.class_events_done >= CLASS_EVENTS and s.car_events_done < CAR_EVENTS and remaining_car_slots > 0:
                event_type = "CAR"
                remaining_car_slots -= 1

            else:
                continue

            # Assign instructor
            instructors = [i for i in instructors if i[1] > 0]
            if not instructors:
                break

            inst_id = instructors[0][0]
            instructors[0][1] -= 1
            total_instructor_capacity -= 1

            # Update student progress
            if event_type == "CLASS":
                s.class_events_done += 1
            else:
                s.car_events_done += 1

            s.last_event_day = day
            schedule_log.append((day, event_type, inst_id, s.sid))

            if s.completed and s.finish_day is None:
                s.finish_day = day
                completion_log.append(
                    (s.sid, s.start_day, s.finish_day, s.finish_day - s.start_day)
                )

    completion_df = pd.DataFrame(completion_log, columns=["StudentID", "StartDay", "FinishDay", "DaysToFinish"])

    if return_details:
        schedule_df = pd.DataFrame(schedule_log, columns=["Day", "Type", "Instructor", "StudentID"])
        return completion_df, schedule_df

    return completion_df["DaysToFinish"].mean() if len(completion_df) else None


# ==========================================================
# EXPERIMENT + GRAPHING
# ==========================================================

if __name__ == "__main__":

    class_sizes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]   # <--- Try different intake volumes
    results = []

    print("\nTesting class sizes:")
    for size in class_sizes:
        avg_time = run_simulation(
            initial_students=70,
            new_students_count=size,
            new_students_every=14,
            sim_days=365
        )
        results.append(avg_time)
        
        if avg_time is None:
            print(f"  Intake {size}: ❗ No students finished within time window")
        else:
            print(f"  Intake {size}: Avg completion = {avg_time:.2f} days")


    # --------- Plot ---------
    plt.figure(figsize=(10,5))
    plt.plot(class_sizes, results, marker='o', linewidth=2)
    plt.xlabel("New Students Every Other Week")
    plt.ylabel("Average Days to Complete Syllabus")
    plt.title("Effect of Class Size on Completion Time")
    plt.grid(True)
    plt.show()