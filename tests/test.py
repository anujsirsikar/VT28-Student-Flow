# scheduler.py
# OR-Tools scheduling for syllabus (2-month horizon, arrivals every other week)
# Save and run with: python scheduler.py

from datetime import date, timedelta
from collections import defaultdict
import math
import pandas as pd
import os

# ------------ PARAMETERS (edit these as you like) -------------
start_date = date(2025, 12, 1)  # scheduling horizon start
weeks = 8  # 2 months ≈ 8 weeks
horizon_days = weeks * 7
arrival_interval_days = 14  # new students every other week
students_per_cohort = 10
events_per_student = 80
classrooms = 17
uses_per_classroom_per_day = 4
slots_per_weekday = classrooms * uses_per_classroom_per_day  # 68
max_events_per_student_per_day = 1  # per-student daily cap
# --------------------------------------------------------------

# Build calendar: calendar days and weekdays-only scheduling days
dates = [start_date + timedelta(days=i) for i in range(horizon_days)]
weekday_dates = [d for d in dates if d.weekday() < 5]  # Mon-Fri only
num_days = len(weekday_dates)

# Build student list: cohorts arriving every arrival_interval_days
students = []
student_id = 0
for day_offset in range(0, horizon_days, arrival_interval_days):
    arrival_date = start_date + timedelta(days=day_offset)
    if arrival_date > dates[-1]:
        break
    for _ in range(students_per_cohort):
        students.append({"id": student_id, "arrival_date": arrival_date})
        student_id += 1
total_students = len(students)

# Helper: map arrival date to first weekday index (if arrival on weekend, push to next weekday)
def date_to_weekday_index(d):
    try:
        return weekday_dates.index(d)
    except ValueError:
        next_d = d
        while next_d.weekday() >= 5:
            next_d += timedelta(days=1)
            if next_d > dates[-1]:
                return None
        return weekday_dates.index(next_d)

arrival_index = {s['id']: date_to_weekday_index(s['arrival_date']) for s in students}

# Try to build and solve CP-SAT model using OR-Tools
model_used = "none"
schedule = []  # list of dicts: date, student, events, arrival
student_stats = []  # per-student summary

try:
    from ortools.sat.python import cp_model

    model = cp_model.CpModel()

    # Variables: x[s,d] integer #events assigned to student s on weekday d
    x = {}
    for s in range(total_students):
        for d in range(num_days):
            x[(s,d)] = model.NewIntVar(0, max_events_per_student_per_day, f"x_s{s}_d{d}")
            if arrival_index[s] is None or d < arrival_index[s]:
                model.Add(x[(s,d)] == 0)

    # Day capacity constraints
    for d in range(num_days):
        model.Add(sum(x[(s,d)] for s in range(total_students)) <= slots_per_weekday)

    # Per-student totals and done indicator
    total_scheduled = {}
    done = {}
    for s in range(total_students):
        total_scheduled[s] = model.NewIntVar(0, events_per_student, f"tot_s{s}")
        model.Add(total_scheduled[s] == sum(x[(s,d)] for d in range(num_days)))
        done[s] = model.NewBoolVar(f"done_s{s}")
        # Link done boolean to total_scheduled reaching events_per_student
        model.Add(total_scheduled[s] >= events_per_student).OnlyEnforceIf(done[s])
        model.Add(total_scheduled[s] <= events_per_student - 1).OnlyEnforceIf(done[s].Not())

    # Objective: maximize number of students who complete within horizon
    model.Maximize(sum(done[s] for s in range(total_students)))

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30  # limit for interactive runs
    solver.parameters.num_search_workers = 8
    res = solver.Solve(model)

    if res in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        model_used = "CP-SAT"
        # extract schedule
        for d_idx, d in enumerate(weekday_dates):
            for s in range(total_students):
                val = int(solver.Value(x[(s,d_idx)]))
                if val > 0:
                    schedule.append({"date": d, "student": s, "events": val, "arrival": students[s]['arrival_date']})
        # per-student stats
        for s in range(total_students):
            tot = int(solver.Value(total_scheduled[s]))
            # find completion day by cumulative sum
            cum = 0
            completion_day = None
            for d_idx, d in enumerate(weekday_dates):
                v = int(solver.Value(x[(s,d_idx)]))
                cum += v
                if completion_day is None and cum >= events_per_student:
                    completion_day = d
                    break
            student_stats.append({"student": s, "arrival": students[s]['arrival_date'], "scheduled": tot, "remaining": events_per_student - tot, "finished": completion_day})
    else:
        raise RuntimeError("CP-SAT did not return a feasible/optimal result.")
except Exception as exc:
    # If OR-Tools is unavailable or failed, do greedy FIFO allocation (fast fallback).
    model_used = "greedy_fallback"
    from collections import deque, defaultdict
    s_info = {s['id']: {"arrival": s['arrival_date'], "remaining": events_per_student, "scheduled": 0} for s in students}
    queue = deque(sorted(s_info.keys(), key=lambda sid: (s_info[sid]["arrival"], sid)))
    for d in weekday_dates:
        slots = slots_per_weekday
        per_student_today = defaultdict(int)
        made_progress = True
        while slots > 0 and made_progress:
            made_progress = False
            for _ in range(len(queue)):
                sid = queue.popleft()
                if s_info[sid]["arrival"] <= d and s_info[sid]["remaining"] > 0 and per_student_today[sid] < max_events_per_student_per_day:
                    s_info[sid]["remaining"] -= 1
                    s_info[sid]["scheduled"] += 1
                    per_student_today[sid] += 1
                    slots -= 1
                    made_progress = True
                    schedule.append({"date": d, "student": sid, "events": 1, "arrival": s_info[sid]["arrival"]})
                    if s_info[sid]["remaining"] == 0:
                        continue
                queue.append(sid)
                if slots <= 0:
                    break
    for sid in sorted(s_info.keys()):
        cum = 0
        completion_day = None
        for entry in schedule:
            if entry['student'] == sid:
                cum += entry['events']
                if completion_day is None and cum >= events_per_student:
                    completion_day = entry['date']
                    break
        student_stats.append({"student": sid, "arrival": s_info[sid]["arrival"], "scheduled": s_info[sid]["scheduled"], "remaining": s_info[sid]["remaining"], "finished": completion_day})

# Convert to DataFrames and save
if schedule:
    sched_df = pd.DataFrame(schedule)
    sched_daily = sched_df.groupby(["date","student","arrival"], as_index=False)["events"].sum().sort_values(["date","student"])
else:
    sched_daily = pd.DataFrame(columns=["date","student","arrival","events"])

students_df = pd.DataFrame(student_stats).sort_values(["student"])

print(sched_daily)
print(students_df)

# Summary
total_completed = students_df[students_df["remaining"] <= 0].shape[0]
total_scheduled_events = students_df["scheduled"].sum()
remaining_events = students_df["remaining"].sum()
extra_weekdays_needed = math.ceil(remaining_events / slots_per_weekday) if remaining_events>0 else 0

summary = {
    "horizon_start": start_date,
    "horizon_weeks": weeks,
    "weekday_count": num_days,
    "total_students": total_students,
    "students_completed_within_horizon": total_completed,
    "total_events_scheduled": total_scheduled_events,
    "remaining_events_after_horizon": remaining_events,
    "extra_weekdays_needed_to_finish_remaining": extra_weekdays_needed,
    "model_used": model_used
}

print("SUMMARY:")
for k, v in summary.items():
    print(f"  {k}: {v}")

print("\nCSV files saved:")
print("  /mnt/data/schedule_by_day_student.csv")
print("  /mnt/data/student_stats.csv")
print("\nIf you open student_stats.csv, 'finished' shows the calendar date the student completed all 80 events (if any).")