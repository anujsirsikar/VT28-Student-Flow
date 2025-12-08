## Output from running this program

# Student 0:
#   Event 0 on Day 0
#   Event 1 on Day 2

# Student 1:
#   Event 0 on Day 1
#   Event 1 on Day 3

# Student 2:
#   Event 0 on Day 2
#   Event 1 on Day 4


from ortools.sat.python import cp_model

# ------------------ Inputs ----------------------
num_students = 3
events_per_student = 2
days = range(7)  # 7 possible days indexed 0..6

classID = [0, 1, 2]  # lower starts first

def is_valid_day(day):
    return day not in [5, 6]  # no weekend

valid_days = [d for d in days if is_valid_day(d)]

# ------------------ Model -----------------------
model = cp_model.CpModel()

x = {}
for s in range(num_students):
    for e in range(events_per_student):
        for d in days:
            x[s, e, d] = model.NewBoolVar(f"x_s{s}_e{e}_d{d}")

# 1. Each event happens once
for s in range(num_students):
    for e in range(events_per_student):
        model.Add(sum(x[s,e,d] for d in days) == 1)

# 2. Respect valid days
for s in range(num_students):
    for e in range(events_per_student):
        for d in days:
            if d not in valid_days:
                model.Add(x[s,e,d] == 0)

# 3. Order events (event 0 before event 1)
for s in range(num_students):
    for d1 in days:
        for d2 in days:
            if d2 <= d1:
                model.Add(x[s,0,d1] + x[s,1,d2] <= 1)

# 4. Only 1 start per day across all students
for d in days:
    model.Add(sum(x[s,0,d] for s in range(num_students)) <= 1)

# 5. Priority ordering
start_day = {}
for s in range(num_students):
    start_day[s] = model.NewIntVar(0, len(days)-1, f"start{s}")
    model.Add(start_day[s] == sum(d * x[s,0,d] for d in days))

for s in range(num_students):
    for t in range(num_students):
        if classID[s] < classID[t]:
            model.Add(start_day[s] <= start_day[t])

# Objective: minimize maximum start day
latest_start = model.NewIntVar(0, len(days)-1, "latest_start")
for s in range(num_students):
    model.Add(latest_start >= start_day[s])

model.Minimize(latest_start)


# ------------------ Solve -----------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 5
result = solver.Solve(model)

# ------------------ Output ----------------------
print((num_students))
for s in range(num_students):
    print(f"\nStudent {s}:")
    for e in range(events_per_student):
        for d in days:
            if solver.Value(x[s,e,d]):
                print(f"  Event {e} on Day {d}")



