from ortools.sat.python import cp_model
import pandas as pd
import random
from datetime import timedelta, date

# -------------------- Parameters -------------------------
starting_students = 80      ##number of students already classes up
class_up_frequency = 14        # every 2 weeks in days
class_up_per_week = 6          #number students classing up per week. Should be able to make this a list and read in. 
EVENTS_PER_STUDENT = 80         # random number I made up, Will have to check size of list in program (which will allow for events to be added)

aircraft = 17           # just a base level with no contraints. 
num_flight_aircraft_per_Day = 4
slots_per_Day = aircraft * num_flight_aircraft_per_Day  # 68/day

INSTRUCTORS = 20
INSTRUCTOR_CAPACITY_PER_DAY = 3
INSTRUCTOR_AVAILABILITY_PROB = 0.70  # 70% chance available

SIMULATION_DAYS = 365  # ~2 months

# -------------------- Data Structures ---------------------
class Student:
    def __init__(self, sid, start_day):
        self.sid = sid
        self.events_done = 0
        self.last_event_day = -999
        self.start_day = start_day
        self.finish_day = None

students = []
sid_counter = 0

# initial students
for _ in range(starting_students):
    students.append(Student(sid_counter, 0))
    sid_counter += 1

# schedule logs
schedule_log = []       # (day, slot, instructor, student)
completion_stats = []   # (student_id, start_day, finish_day, total_days)

# -------------------- Scheduling Loop --------------------
current_date = date.today()

for day in range(SIMULATION_DAYS):

    # Add new students every 2 weeks
    if day % class_up_frequency == 0 and day != 0:
        for _ in range(class_up_per_week):
            students.append(Student(sid_counter, day))
            sid_counter += 1

    # ---------- Determine instructor availability ----------
    instructors_available = []
    for iid in range(INSTRUCTORS):
        if random.random() < INSTRUCTOR_AVAILABILITY_PROB:
            instructors_available.append([iid, INSTRUCTOR_CAPACITY_PER_DAY])

    # total instructor teaching capacity today
    total_instructor_capacity = sum(inst[1] for inst in instructors_available)

    # the true limit is whichever runs out first
    available_slots_today = min(slots_per_Day, total_instructor_capacity)

    # ---------- Student Priority (longest since last event wins) ----------
    waiting_list = sorted(
        [s for s in students if s.events_done < EVENTS_PER_STUDENT],
        key=lambda s: (day - s.last_event_day),
        reverse=True
    )

    slot_count = 0

    for s in waiting_list:
        if slot_count >= available_slots_today: 
            break

        # pick instructor with remaining capacity
        instructors_available = [x for x in instructors_available if x[1] > 0]
        if not instructors_available:
            break  # no instructors left → stop scheduling today

        instructor_id = instructors_available[0][0]
        instructors_available[0][1] -= 1

        # assign event
        s.events_done += 1
        s.last_event_day = day
        schedule_log.append((day, slot_count, instructor_id, s.sid))
        slot_count += 1

        if s.events_done == EVENTS_PER_STUDENT:
            s.finish_day = day
            total = day - s.start_day
            completion_stats.append((s.sid, s.start_day, s.finish_day, total))

# -------------------- Results --------------------
schedule_df = pd.DataFrame(schedule_log,
    columns=["Day","Slot","InstructorID","StudentID"])
completion_df = pd.DataFrame(completion_stats,
    columns=["StudentID","StartDay","FinishDay","DaysToFinish"])

print("\n--- Simulation Complete ---")
print("Total Students:", len(students))
print("Finished:", len(completion_df))
print("Still In Progress:", len(students) - len(completion_df))
print("Students per instructor capacity added.")

if len(completion_df)>0:
    print("Average Completion Time:", completion_df["DaysToFinish"].mean(), "days")

# Optional CSVs
schedule_df.to_csv("schedule.csv", index=False)
completion_df.to_csv("student_completion_stats.csv", index=False)

print("\nFiles saved:")
print(" schedule.csv")
print(" student_completion_stats.csv")