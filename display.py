import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import os, json
from datetime import date

# ------------------ LOAD DATA ------------------

def load_all_runs(base="outputs"):
    records = []
    valid_dates = set()

    for pct_folder in os.listdir(base):
        if not pct_folder.startswith("pct"):
            continue
        percent = int(pct_folder.replace("pct", ""))
        pct_path = os.path.join(base, pct_folder)

        for class_folder in os.listdir(pct_path):
            if not class_folder.startswith("class"):
                continue
            class_size = int(class_folder.replace("class", ""))
            class_path = os.path.join(pct_path, class_folder)

            for fname in os.listdir(class_path):
                if not fname.endswith(".json"):
                    continue

                run_id = int(fname.split("_")[1].split(".")[0])

                with open(os.path.join(class_path, fname)) as f:
                    data = json.load(f)

                for day in data["days"]:
                    valid_dates.add(day["date"])
                    records.append({
                        "percent": percent,
                        "class_size": class_size,
                        "run": run_id,
                        "date": day["date"],
                        "resources": day["resources"],
                        "students": day["students"]
                    })

    return records, sorted(valid_dates)

# ------------------ SUMMARIES ------------------

def summarize_students(students):
    return {
        "scheduled": len(students["scheduled"]),
        "waiting": len(students["waiting"]),
        "completed": len(students["completed"]),
        "incomplete": len(students["scheduled"]) + len(students["waiting"])
    }

def resource_hours(resources, resource_type):
    return round(sum(resources.get(resource_type, {}).values()), 2)

# ------------------ UI ------------------

class SimulationExplorer:
    def __init__(self, root, records, valid_dates):
        self.records = records
        self.valid_dates = valid_dates
        self.selected_date = None

        root.title("Simulation Explorer")

        top = tk.Frame(root)
        top.pack(padx=10, pady=10, fill="x")

        tk.Button(top, text="Select Date", command=self.pick_date).pack(side="left")

        self.resource_var = tk.StringVar(value="aircraft")
        ttk.Combobox(
            top,
            textvariable=self.resource_var,
            values=["aircraft", "instructor", "classroom", "utd", "oft", "vtd", "mr"],
            state="readonly",
            width=12
        ).pack(side="left", padx=10)

        self.resource_var.trace_add("write", lambda *_: self.refresh())

        # Text output + scrollbar
        frame = tk.Frame(root)
        frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        self.text = tk.Text(frame, height=25, width=100, yscrollcommand=scrollbar.set)
        self.text.pack(fill="both", expand=True)

        scrollbar.config(command=self.text.yview)

    def pick_date(self):
        top = tk.Toplevel()
        cal = Calendar(top, selectmode="day", date_pattern="yyyy-mm-dd")
        cal.pack(padx=10, pady=10)

        # highlight valid dates
        for d in self.valid_dates:
            y, m, d2 = map(int, d.split("-"))
            cal.calevent_create(date(y, m, d2), "valid", "valid")

        cal.tag_config("valid", background="lightgreen")

        def select():
            selected = cal.selection_get()
            date = selected.strftime("%Y-%m-%d")

            if date in self.valid_dates:
                self.selected_date = date
                self.refresh()
                top.destroy()
            else:
                self.text.delete(1.0, tk.END)
                self.text.insert(tk.END, "Selected date has no simulation data.\n")

        tk.Button(top, text="Select", command=select).pack()

    def refresh(self):
        print("REFRESH CALLED FOR", self.selected_date)
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)

        found = False

        for r in self.records:
            if r["date"] != self.selected_date:
                continue

            found = True

            self.text.insert(
                tk.END,
                f"Percent {r['percent']}% | "
                f"Class {r['class_size']} | "
                f"Run {r['run']}\n"
            )

            for res, usage in r["resources"].items():
                total = round(sum(usage.values()), 2)
                self.text.insert(tk.END, f"  {res}: {total} hrs\n")

            self.text.insert(tk.END, "-" * 60 + "\n")

        if not found:
            self.text.insert(tk.END, "No data for selected date.\n")

        self.text.config(state=tk.DISABLED)


# ------------------ MAIN ------------------

def main():
    records, valid_dates = load_all_runs()

    root = tk.Tk()
    SimulationExplorer(root, records, valid_dates)
    root.mainloop()

if __name__ == "__main__":
    main()
