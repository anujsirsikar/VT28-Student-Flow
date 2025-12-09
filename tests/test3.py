#!/usr/bin/env python3
"""
Driver's-ed scheduler (calendar-aware, ordered prerequisites).

Features implemented:
- Real calendar scheduling: uses actual dates and SKIPS weekends (Sat/Sun).
  You can also add specific holidays to `HOLIDAYS` to skip them.
- Ordered events / prerequisites (skills unlock):
  * Each student must complete CLASS_EVENTS (in order) before any CAR_EVENTS.
  * Events are strictly sequential: a student can only be scheduled for their next required event.
- Resources:
  * CLASSROOMS and CARS each have SLOTS_PER_RESOURCE_PER_DAY uses/day.
  * INSTRUCTORS: 20 instructors, each can teach up to INSTRUCTOR_CAPACITY_PER_DAY sessions/day.
    Each instructor has a daily independent 70% chance of being available.
- New students arrive every NEW_STUDENTS_EVERY days (cohort of NEW_STUDENTS_COUNT).
- Simulation horizon: WEEKS_TO_SIMULATE weeks (calendar-aware).
- Priority rule: students with the longest time since their last event are scheduled first.
- Per-student daily cap (MAX_EVENTS_PER_STUDENT_PER_DAY) — default 1 (changeable).
- Outputs:
  * schedule.csv — full day-by-day assignments (date, type, instructor, student, event_index)
  * student_stats.csv — per-student progress and completion date (if any)

How to tweak:
- Change start_date, counts, capacities, and MAX_EVENTS_PER_STUDENT_PER_DAY at top.
- Add real holiday dates to HOLIDAYS (list of date objects) if you want to skip them.
"""

from datetime import date, timedelta
import random
import csv

# -------------------- PARAMETERS --------------------
SEED = 42
random.seed(SEED)

# Calendar / horizon
START_DATE = date(2025, 12, 1)
WEEKS_TO_SIMULATE = 52
HORIZON_DAYS = WEEKS_TO_SIMULATE * 7

# Cohorts / arrivals
NUM_INITIAL_STUDENTS = 80
NEW_STUDENTS_EVERY = 14         # every other week (days)
NEW_STUDENTS_COUNT = 6

# Event structure (ordered prerequisites)
CLASS_EVENTS = 10               # first 10 events must be in classroom (in order)
CAR_EVENTS = 60                 # then 60 driving events (in order)
EVENTS_PER_STUDENT = CLASS_EVENTS + CAR_EVENTS

# Resources
CLASSROOMS = 10
CARS = 17                       # number of cars available (change as needed)
SLOTS_PER_RESOURCE_PER_DAY = 4  # each classroom/car can be used 4 times/day

CLASSROOM_DAILY_CAP = CLASSROOMS * SLOTS_PER_RESOURCE_PER_DAY
CAR_DAILY_CAP = CARS * SLOTS_PER_RESOURCE_PER_DAY

INSTRUCTORS = 20
INSTRUCTOR_CAPACITY_PER_DAY = 3
INSTRUCTOR_AVAILABILITY_PROB = 0.70

# Limits per student
MAX_EVENTS_PER_STUDENT_PER_DAY = 1  # how many events a student may do in one day (keeps realism)

# Optional: specific holidays to skip (calendar.date objects)
HOLIDAYS = [
    date(2026, 1, 1),  # example: New Year's Day
]

# Output files
SCHEDULE_CSV = "schedule.csv"
STUDENT_STATS_CSV = "student_stats.csv"
# ----------------------------------------------------

# -------------------- DATA STRUCTURES --------------------
class Student:
    def __init__(self, sid, arrival_date):
        self.sid = sid
        self.arrival_date = arrival_date
        self.next_event_index = 0   # 0..EVENTS_PER_STUDENT-1, enforces order/prereqs
        self.last_event_date = None
        self.daily_events_done = 0  # reset each day
        self.finish_date = None

    @property
    def needs_class(self):
        return self.next_event_index < CLASS_EVENTS

    @property
    def completed(self):
        return self.next_event_index >= EVENTS_PER_STUDENT

    def record_event(self, event_date):
        self.next_event_index += 1
        self.last_event_date = event_date
        self.daily_events_done += 1
        if self.completed and self.finish_date is None:
            self.finish_date = event_date

# -------------------- HELPERS --------------------
def is_weekend(d: date) -> bool:
    return d.weekday() >= 5  # Sat=5, Sun=6

def is_holiday(d: date) -> bool:
    return d in HOLIDAYS

def is_workday(d: date) -> bool:
    return (not is_weekend(d)) and (not is_holiday(d))

def daterange(start: date, days: int):
    for i in range(days):
        yield start + timedelta(days=i)

# -------------------- INITIALIZE --------------------
students = []
next_sid = 0

# initial cohort (arrive on START_DATE)
for _ in range(NUM_INITIAL_STUDENTS):
    students.append(Student(next_sid, START_DATE))
    next_sid += 1

# instructor objects: represent by id (0..INSTRUCTORS-1)
instructor_ids = list(range(INSTRUCTORS))

# logs
schedule_entries = []  # rows: date, resource_type, resource_id (classroom/car slot id optional), instructor_id, student_id, event_index
# resource_id: for classroom we use "C{index}" and for car "V{index}" (V for vehicle)

# -------------------- SIMULATION --------------------
current_date = START_DATE
for day_offset in range(HORIZON_DAYS):
    today = START_DATE + timedelta(days=day_offset)

    # arrival of new cohort on exact calendar day (even if weekend/holiday we push arrival to next workday)
    if day_offset != 0 and day_offset % NEW_STUDENTS_EVERY == 0:
        # new students arrive — push their official arrival to the next workday if needed
        arrival = today
        while not is_workday(arrival) and (arrival - START_DATE).days < HORIZON_DAYS:
            arrival = arrival + timedelta(days=1)
        for _ in range(NEW_STUDENTS_COUNT):
            if (arrival - START_DATE).days < HORIZON_DAYS:
                students.append(Student(next_sid, arrival))
                next_sid += 1

    # Skip weekends and holidays (no scheduling)
    if not is_workday(today):
        continue

    # Reset per-student daily counter
    for s in students:
        s.daily_events_done = 0

    # Determine instructor availability this day (random 70% each)
    instructors_available = []
    for iid in instructor_ids:
        if random.random() < INSTRUCTOR_AVAILABILITY_PROB:
            instructors_available.append([iid, INSTRUCTOR_CAPACITY_PER_DAY])
    total_inst_capacity = sum(i[1] for i in instructors_available)

    # Resource capacities for today
    available_class_slots = CLASSROOM_DAILY_CAP
    available_car_slots = CAR_DAILY_CAP

    # Effective total capacity limited by instructors as well (since each session needs an instructor)
    effective_total_slots = min(available_class_slots + available_car_slots, total_inst_capacity)

    # Build waiting list: students who have arrived (arrival_date <= today) and not completed,
    # ordered by (days since last event) descending — those waiting longest first.
    def waiting_key(s: Student):
        if s.last_event_date is None:
            # prioritize by earliest arrival among those with no events yet
            # but also treat as large waiting time: days since arrival
            return ((today - s.arrival_date).days + 1000, -s.arrival_date.toordinal())
        else:
            return ((today - s.last_event_date).days, -s.arrival_date.toordinal())

    waiting_students = [s for s in students if (not s.completed) and (s.arrival_date <= today)]
    waiting_students.sort(key=waiting_key, reverse=True)

    # We'll also track identifiers for classroom and car units (for output clarity).
    classroom_unit_ids = [f"C{i}" for i in range(CLASSROOMS)]
    car_unit_ids = [f"V{i}" for i in range(CARS)]
    # For per-unit daily usage counts:
    class_unit_usage = {uid: 0 for uid in classroom_unit_ids}
    car_unit_usage = {uid: 0 for uid in car_unit_ids}

    # Assignment loop: go down waiting_students and try to assign up to MAX_EVENTS_PER_STUDENT_PER_DAY per student,
    # respecting resource-specific slot availability, instructor capacity, and prerequisites (sequential events).
    for student in waiting_students:
        # allow multiple events per day, but limited by MAX_EVENTS_PER_STUDENT_PER_DAY
        while student.daily_events_done < MAX_EVENTS_PER_STUDENT_PER_DAY:
            # Stop if no instructor capacity left
            instructors_available = [iv for iv in instructors_available if iv[1] > 0]
            if not instructors_available:
                break
            # Decide event type based on prerequisite (ordered)
            if student.needs_class:
                # need classroom event
                if available_class_slots <= 0:
                    break  # no classroom capacity left today
                # pick a classroom unit with remaining per-unit capacity (< SLOTS_PER_RESOURCE_PER_DAY)
                chosen_unit = None
                for uid in classroom_unit_ids:
                    if class_unit_usage[uid] < SLOTS_PER_RESOURCE_PER_DAY:
                        chosen_unit = uid
                        break
                if chosen_unit is None:
                    break  # no classroom unit available
                # assign instructor (first available)
                inst_id = instructors_available[0][0]
                instructors_available[0][1] -= 1
                if instructors_available[0][1] <= 0:
                    # will be filtered on next loop iteration
                    pass
                # record event
                event_index = student.next_event_index
                student.record_event(today)
                class_unit_usage[chosen_unit] += 1
                available_class_slots -= 1
                schedule_entries.append({
                    "date": today.isoformat(),
                    "resource_type": "CLASSROOM",
                    "resource_id": chosen_unit,
                    "instructor_id": inst_id,
                    "student_id": student.sid,
                    "event_index": event_index
                })
            else:
                # need car event (student has finished required classroom events)
                if available_car_slots <= 0:
                    break  # no car capacity left today
                # pick a car unit with remaining per-unit capacity
                chosen_unit = None
                for uid in car_unit_ids:
                    if car_unit_usage[uid] < SLOTS_PER_RESOURCE_PER_DAY:
                        chosen_unit = uid
                        break
                if chosen_unit is None:
                    break  # no car available
                # assign instructor
                instructors_available = [iv for iv in instructors_available if iv[1] > 0]
                if not instructors_available:
                    break
                inst_id = instructors_available[0][0]
                instructors_available[0][1] -= 1
                # record event
                event_index = student.next_event_index
                student.record_event(today)
                car_unit_usage[chosen_unit] += 1
                available_car_slots -= 1
                schedule_entries.append({
                    "date": today.isoformat(),
                    "resource_type": "CAR",
                    "resource_id": chosen_unit,
                    "instructor_id": inst_id,
                    "student_id": student.sid,
                    "event_index": event_index
                })
            # end while loop condition will check if student can take another event today
        # end per-student while
    # end for each waiting student

# -------------------- OUTPUT / CSV --------------------
# Save schedule CSV
with open(SCHEDULE_CSV, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "date", "resource_type", "resource_id", "instructor_id", "student_id", "event_index"
    ])
    writer.writeheader()
    for e in schedule_entries:
        # align keys to header names
        writer.writerow({
            "date": e["date"],
            "resource_type": e["resource_type"],
            "resource_id": e["resource_id"],
            "instructor_id": e["instructor_id"],
            "student_id": e["student_id"],
            "event_index": e["event_index"]
        })

# Save student stats CSV
with open(STUDENT_STATS_CSV, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "student_id", "arrival_date", "events_completed", "finished", "finish_date"
    ])
    writer.writeheader()
    for s in students:
        writer.writerow({
            "student_id": s.sid,
            "arrival_date": s.arrival_date.isoformat(),
            "events_completed": s.next_event_index,
            "finished": s.completed,
            "finish_date": s.finish_date.isoformat() if s.finish_date else ""
        })

# Basic console summary
total_students = len(students)
finished_count = sum(1 for s in students if s.completed)
print(f"Simulation complete ({WEEKS_TO_SIMULATE} weeks).")
print(f"Total students simulated: {total_students}")
print(f"Students finished: {finished_count}")
print(f"Schedule rows written: {len(schedule_entries)}")
print(f"Schedule CSV: {SCHEDULE_CSV}")
print(f"Student stats CSV: {STUDENT_STATS_CSV}")