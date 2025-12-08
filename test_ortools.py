from ortools.sat.python import cp_model

def main():
    print("OR-Tools test starting...", flush=True)

    model = cp_model.CpModel()

    students = ["A", "B", "C"]
    blocks = ["Morning", "Afternoon", "Evening"]

    block_available = {
        "Morning": True,
        "Afternoon": True,
        "Evening": False,
    }

    x = {}
    for s in students:
        for b in blocks:
            x[(s, b)] = model.NewBoolVar(f"{s}_{b}")

    for s in students:
        model.Add(sum(x[(s, b)] for b in blocks) <= 1)

    for b in blocks:
        if block_available[b]:
            model.Add(sum(x[(s, b)] for s in students) <= 1)
        else:
            for s in students:
                model.Add(x[(s, b)] == 0)

    model.Maximize(
        sum(x[(s, b)] for s in students for b in blocks)
    )

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 2

    print("Solving...", flush=True)
    result = solver.Solve(model)
    print("Solver result:", result, flush=True)

    if result in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("\nFlight Assignments:", flush=True)
        for b in blocks:
            assigned = [s for s in students if solver.Value(x[(s, b)]) == 1]
            if assigned:
                print(f"{b}: {assigned[0]}", flush=True)
            else:
                print(f"{b}: (unused)", flush=True)
    else:
        print("No solution found.", flush=True)

if __name__ == "__main__":
    print("Running main()", flush=True)
    main()
