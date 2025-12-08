import sys
import ortools
from ortools.sat.python import cp_model

print("Python version:", sys.version)
print("OR-Tools version:", ortools.__version__)

print("Importing CP-SAT model...", flush=True)
try:
    m = cp_model.CpModel()
    print("CP-SAT model imported OK")
except Exception as e:
    print("CP-SAT failed:", e)

print("Creating solver...", flush=True)
try:
    solver = cp_model.CpSolver()
    print("Solver created OK")
except Exception as e:
    print("Solver creation failed:", e)

print("Calling Solve() on an empty model...", flush=True)
try:
    result = solver.Solve(cp_model.CpModel())
    print("Solve returned:", result)
except Exception as e:
    print("Solve() crashed:", e)
