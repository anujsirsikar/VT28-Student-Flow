'''
Running this file allows the user to step through and compare specific days
to see which resources were used (etc...) and to get the full picture of 
what took place each day. How many students were scheduled and how many aircraft
were used for example. 
'''
import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from datetime import datetime
import os
import json
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Global Variables
selected_date1 = None
selected_date2 = None
data_by_date = {}
valid_dates = set()

def open_calendar(label, date_number):
    global selected_date1, selected_date2

    win = tk.Toplevel(root)
    win.title(f"Select Date {date_number}")

    # ---- force window to front ----
    win.transient(root)      # associate with parent
    win.lift()               # bring to front
    win.focus_force()        # grab focus
    win.grab_set()
    # --------------------------------

    cal = Calendar(win, selectmode="day")
    cal.pack(padx=10, pady=10)

    for d in valid_dates:
        try:
            dt = datetime.strptime(d, "%Y-%m-%d")
            cal.calevent_create(dt, "available", "available")
        except ValueError:
            pass

    cal.tag_config("available", background="white", foreground="lightblue")

    def confirm_date():
        # Calendar returns MM/DD/YY

        global selected_date1, selected_date2
        date_str = cal.get_date()
        date = datetime.strptime(date_str, "%m/%d/%y").strftime("%Y-%m-%d")

        if date not in valid_dates:
            print("Selected date has no data:", date)
            return

        set_date(date_number, date, label)
        win.destroy()

        print("Selected date saved:", date)
        label.config(text=f"Selected Date {date_number}: {date}")
        win.destroy()

        current_category = category_var.get()
        if current_category in category_dropdown["values"]:
            display_category(current_category)

    ttk.Button(win, text="Confirm", command=confirm_date).pack(pady=5)


def load_simulation_data(base_dir="outputs"):
    """
    Walks output/pct*/class*/<json>
    Returns dict: date -> list of runs preserving pct/class identity
    """
    data_by_date = {}

    for pct in os.listdir(base_dir):
        pct_path = os.path.join(base_dir, pct)
        if not os.path.isdir(pct_path):
            continue

        for cls in os.listdir(pct_path):
            cls_path = os.path.join(pct_path, cls)
            if not os.path.isdir(cls_path):
                continue

            for file in os.listdir(cls_path):
                if not file.endswith(".json"):
                    continue

                file_path = os.path.join(cls_path, file)
                with open(file_path) as f:
                    data = json.load(f)

                for day in data.get("days", []):
                    date = day["date"]
                    data_by_date.setdefault(date, []).append({
                        "pct": pct,
                        "class": cls,
                        "day": day
                    })

    return data_by_date

def build_run_index(data_by_date):
    data_by_run = defaultdict(dict)  # (pct, cls) -> {date_str: day_dict}
    for date_str, runs in data_by_date.items():
        for r in runs:
            data_by_run[(r["pct"], r["class"])][date_str] = r["day"]
    return data_by_run


def monthly_avg_students_for_run(run_days_by_date):
    """
    run_days_by_date: dict like { 'YYYY-MM-DD': day_dict }
    returns: dict { 'YYYY-MM': average_students_float }
    """
    month_to_daily_totals = defaultdict(list)

    for date_str, day in run_days_by_date.items():
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        month_key = dt.strftime("%Y-%m")

        blocks = day.get("students", {}).get("by_block", {})
        daily_total = sum(blocks.values())
        month_to_daily_totals[month_key].append(daily_total)

    month_avg = {}
    for month_key, totals in month_to_daily_totals.items():
        month_avg[month_key] = sum(totals) / len(totals) if totals else 0.0

    return dict(sorted(month_avg.items()))

def monthly_avg_students_by_block_for_run(run_days_by_date):
    """
    returns:
      months_sorted: ['YYYY-MM', ...]
      block_to_series: { 'Contacts': [..], 'Aero': [..], ... } aligned to months_sorted
    """
    month_block_vals = defaultdict(lambda: defaultdict(list))  # month -> block -> [counts]
    all_blocks = set()

    for date_str, day in run_days_by_date.items():
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        month_key = dt.strftime("%Y-%m")

        blocks = day.get("students", {}).get("by_block", {})
        for block, val in blocks.items():
            month_block_vals[month_key][block].append(val)
            all_blocks.add(block)

        # ensure missing blocks count as 0 on that day (optional but usually desired)
        # We'll handle missing later when building series.

    months = sorted(month_block_vals.keys())
    blocks_sorted = sorted(all_blocks)

    block_to_series = {}
    for block in blocks_sorted:
        series = []
        for m in months:
            vals = month_block_vals[m].get(block, [])
            # If block wasn't present that month/day, treat as 0 (common for consistency)
            avg = (sum(vals) / len(vals)) if vals else 0.0
            series.append(avg)
        block_to_series[block] = series

    return months, block_to_series


# ---------------- Display category ----------------
def display_category(category):
    # Clear both trees
    for tree in (tree1, tree2):
        for item in tree.get_children():
            tree.delete(item)

    def populate_tree(tree, date):
        if not date:
            return

        runs = data_by_date.get(date, [])
        if not runs:
            return

        grouped = {}

        # -------- build grouped structure --------
        for run in runs:
            pct = run["pct"]
            cls = run["class"]
            day = run["day"]

            if category == "students":
                blocks = day.get("students", {}).get("by_block", {})
                summary = day.get("students", {}).get("summary", {})  # expects {'started':..,'completed':..,'remaining':..}

                grouped.setdefault(pct, {})
                if cls not in grouped[pct] or not isinstance(grouped[pct][cls], dict):
                    grouped[pct][cls] = {"blocks": [], "summary": {}}

                for k, v in blocks.items():
                    grouped[pct][cls]["blocks"].append((k, v))

                grouped[pct][cls]["summary"] = summary

            else:
                resources = day.get("resources", {}).get(category, {})

                grouped.setdefault(pct, {}).setdefault(cls, [])
                for name, vals in resources.items():
                    grouped[pct][cls].append((
                        name,
                        f"used (hours) ={vals['hours_used']:.2f} "
                        f"avail (hours) ={vals['hours_available']:.2f} "
                        f"uses={vals['uses']}"
                    ))

        # -------- render grouped structure --------
        for pct in sorted(grouped):
            try:
                pct_num = int(pct.replace("pct", ""))
                pct_label = f"Percentage {pct_num}%"
            except Exception:
                pct_label = pct

            pct_id = tree.insert("", "end", text=pct_label, open=True)

            for cls in sorted(grouped[pct]):
                try:
                    cls_num = int(cls.replace("class", ""))
                    cls_label = f"Class up size: {cls_num}"
                except Exception:
                    cls_label = cls

                if category == "students":
                    blocks = grouped[pct][cls].get("blocks", [])
                    summary = grouped[pct][cls].get("summary", {})

                    # SIT total (sum of by_block)
                    total = sum(v for _, v in blocks)
                    cls_id = tree.insert(pct_id, "end", text=f"{cls_label}: SIT: {total}", open=True)

                    # Block totals
                    for block, val in blocks:
                        tree.insert(cls_id, "end", text=f"{block}: {val}")

                    # Summary at bottom
                    if summary:
                        tree.insert(cls_id, "end", text="---")
                        tree.insert(cls_id, "end", text=f"Started: {summary.get('started', 0)}")
                        tree.insert(cls_id, "end", text=f"Completed: {summary.get('completed', 0)}")
                        tree.insert(cls_id, "end", text=f"Remaining: {summary.get('remaining', 0)}")

                else:
                    lines = grouped[pct][cls]
                    if not lines:
                        continue

                    # Insert class label only
                    cls_id = tree.insert(pct_id, "end", text=cls_label, open=True)

                    # Insert ALL resource lines under it
                    for name, info in lines:
                        tree.insert(cls_id, "end", text=f"{name} | {info}")



                    # cls_id = tree.insert(
                    #     pct_id, "end",
                    #     text=f"{cls_label}: {lines[0][0]} | {lines[0][1]}",
                    #     open=True
                    # )
                    # for name, info in lines[1:]:
                    #     tree.insert(cls_id, "end", text=f"{name} | {info}")

    populate_tree(tree1, selected_date1)
    populate_tree(tree2, selected_date2)


def fmt_pct(pct):
    try:
        return f"Percentage {int(pct.replace('pct', ''))}%"
    except Exception:
        return pct


def fmt_class(cls):
    try:
        return f"Class up size: {int(cls.replace('class', ''))}"
    except Exception:
        return cls


def on_pct_selected(_event=None):
    p = pct_var.get()
    # Filter classes for selected pct
    
    classes_for_pct = sorted(
        {cls for (pct, cls) in data_by_run.keys() if pct == p},
        key=lambda x: (
            0 if x.startswith("class") else 1,   # class entries first
            int(x.replace("class", "")) if x.startswith("class") else x
        )
    )

    cls_dropdown["values"] = classes_for_pct
    cls_var.set("Select class")

def clear_frame(frame):
    for w in frame.winfo_children():
        w.destroy()

def show_monthly_avg_chart_popup():
    # Requires: pct_var, cls_var, pct_dropdown, cls_dropdown, data_by_run
    p = pct_var.get()
    c = cls_var.get()

    if p not in pct_dropdown["values"] or c not in cls_dropdown["values"]:
        print("Select pct and class first")
        return

    run_days = data_by_run.get((p, c))
    if not run_days:
        print("No data for selected pct/class")
        return

    avgs = monthly_avg_students_for_run(run_days)  # {'YYYY-MM': float}
    if not avgs:
        print("No monthly data to plot")
        return

    months = list(avgs.keys())
    values = [avgs[m] for m in months]

    # --- Popup window ---
    win = tk.Toplevel(root)
    win.title(f"Monthly Avg Students - {fmt_pct(p)} / {fmt_class(c)}")
    win.geometry("800x500")

    win.transient(root)
    win.lift()
    win.focus_force()

    # --- Matplotlib figure ---
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(months, values, marker="o")
    ax.set_xlabel("Month")
    ax.set_ylabel("Avg students in training")
    ax.set_title(f"{fmt_pct(p)} / {fmt_class(c)}")
    ax.tick_params(axis="x", rotation=45)

    # Show a label every 4 months
    step = 4
    ax.set_xticks(range(len(months)))
    pretty_months = [
        datetime.strptime(m, "%Y-%m").strftime("%b %Y") for m in months
    ]

    ax.set_xticklabels(
        [pm if i % step == 0 else "" for i, pm in enumerate(pretty_months)],
        rotation=45,
        ha="right"
    )

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    # Optional: clean close button
    ttk.Button(win, text="Close", command=win.destroy).pack(pady=6)


def show_monthly_block_chart_popup():
    p = pct_var.get()
    c = cls_var.get()

    if p not in pct_dropdown["values"] or c not in cls_dropdown["values"]:
        print("Select pct and class first")
        return

    run_days = data_by_run.get((p, c))
    if not run_days:
        print("No data for selected pct/class")
        return

    months, block_to_series = monthly_avg_students_by_block_for_run(run_days)
    if not months or not block_to_series:
        print("No block data to plot")
        return

    win = tk.Toplevel(root)
    win.title(f"Monthly Avg Students by Block - {fmt_pct(p)} / {fmt_class(c)}")
    win.geometry("950x600")
    win.transient(root)
    win.lift()
    win.focus_force()

    fig, ax = plt.subplots(figsize=(9.5, 5.5))

    BLOCK_ORDER = [
    "Ground School",
    "Contacts",
    "Aero",
    "Instrument Ground",
    "Instruments",
    "Forms",
    "Capstone",
]

    # Plot each block as a separate line
    for block in BLOCK_ORDER:
        if block in block_to_series:
            ax.plot(
                months,
                block_to_series[block],
                linewidth=1.5,
                label=block
            )

    ax.set_xlabel("Month")
    ax.set_ylabel("Avg students in training")
    ax.set_title(f"{fmt_pct(p)} / {fmt_class(c)}")
    ax.tick_params(axis="x", rotation=45)

    # Show a label every 4 months
    step = 4
    ax.set_xticks(range(len(months)))
    pretty_months = [
        datetime.strptime(m, "%Y-%m").strftime("%b %Y") for m in months
    ]

    ax.set_xticklabels(
        [pm if i % step == 0 else "" for i, pm in enumerate(pretty_months)],
        rotation=45,
        ha="right"
    )

    # Legend can get big; put it outside
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5))
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    ttk.Button(win, text="Close", command=win.destroy).pack(pady=6)


def set_date(date_number, new_date, label):
    global selected_date1, selected_date2

    if new_date not in valid_dates:
        return

    if date_number == 1:
        selected_date1 = new_date
    else:
        selected_date2 = new_date

    label.config(text=f"Selected Date {date_number}: {new_date}")

    # refresh trees if a category is selected
    current_category = category_var.get()
    if current_category in category_dropdown["values"]:
        display_category(current_category)


def step_date(date_number, direction, label):
    """
    direction: +1 for next date, -1 for previous date
    """
    current = selected_date1 if date_number == 1 else selected_date2
    if not current:
        # If nothing selected yet, pick first/last depending on direction
        new_date = sorted_valid_dates[0] if direction > 0 else sorted_valid_dates[-1]
        set_date(date_number, new_date, label)
        return

    try:
        idx = sorted_valid_dates.index(current)
    except ValueError:
        # current isn't in the list (shouldn't happen), reset to nearest end
        new_date = sorted_valid_dates[0] if direction > 0 else sorted_valid_dates[-1]
        set_date(date_number, new_date, label)
        return

    new_idx = idx + direction
    if new_idx < 0 or new_idx >= len(sorted_valid_dates):
        return  # clamp at ends (do nothing)

    set_date(date_number, sorted_valid_dates[new_idx], label)



def main():
    global root, category_var, category_dropdown, tree1, tree2, data_by_date, valid_dates, data_by_run
    global pct_var, pct_dropdown, cls_var ,cls_dropdown, sorted_valid_dates

    data_by_date = load_simulation_data()
    valid_dates = set(data_by_date.keys())
    sorted_valid_dates = sorted(valid_dates)
    data_by_run = build_run_index(data_by_date)

    root = tk.Tk()
    root.title("Simulation Viewer")
    root.geometry("1000x600")

    # ---------------- Top control bar (2 rows) ----------------
    top_frame = ttk.Frame(root)
    top_frame.pack(fill="x", padx=10, pady=10)

    row1 = ttk.Frame(top_frame)
    row1.pack(fill="x", pady=(0, 6))  # first row

    row2 = ttk.Frame(top_frame)
    row2.pack(fill="x")               # second row

    row3 = ttk.Frame(top_frame)
    row3.pack(fill="x")                # Resource selector


    # ---------------- Row 1: Monthly averages controls ----------------
    pct_class_frame = ttk.Frame(row1)
    pct_class_frame.pack(side="left", padx=(0, 10))

    ttk.Label(pct_class_frame, text="Run:").pack(side="left", padx=(0, 6))

    pct_var = tk.StringVar()
    pct_dropdown = ttk.Combobox(pct_class_frame, textvariable=pct_var, state="readonly", width=10)
    pct_dropdown.pack(side="left", padx=(0, 8))

    cls_var = tk.StringVar()
    cls_dropdown = ttk.Combobox(pct_class_frame, textvariable=cls_var, state="readonly", width=10)
    cls_dropdown.pack(side="left")

    # Populate pct list
    all_run_keys = list(data_by_run.keys())
    all_pcts = sorted(
        {pct for pct, _ in all_run_keys},
        key=lambda x: int(x.replace("pct", "")) if x.startswith("pct") else x
    )
    pct_dropdown["values"] = all_pcts
    pct_dropdown.set("Select pct")
    cls_dropdown.set("Select class")
    cls_dropdown["values"] = []

    pct_dropdown.bind("<<ComboboxSelected>>", on_pct_selected)

    ttk.Button(row1, text="Monthly Avg Chart", command=show_monthly_avg_chart_popup).pack(side="left")
    ttk.Button(row1, text="Monthly Block Chart", command=show_monthly_block_chart_popup).pack(side="left", padx=(8, 0))


    # ---------------- Row 2: Date selectors + resource dropdown ----------------
  
    date1_frame = ttk.Frame(row2)  # or top_frame if you haven’t split rows yet
    date1_frame.pack(side="left", padx=(0, 15))

    selected_label1 = ttk.Label(date1_frame, text="Selected Date 1: None")
    

    ttk.Button(date1_frame, text="Select Date 1",
            command=lambda: open_calendar(selected_label1, 1)).pack(side="left", padx=(40, 4))

    ttk.Button(date1_frame, text="<", width=1,
            command=lambda: step_date(1, -1, selected_label1)).pack(side="left")

    selected_label1.pack(side="left", padx=(0, 4))

    ttk.Button(date1_frame, text=">", width=1,
            command=lambda: step_date(1, +1, selected_label1)).pack(side="left")



    date2_frame = ttk.Frame(row2)
    date2_frame.pack(side="left", padx=(0, 15))

    selected_label2 = ttk.Label(date2_frame, text="Selected Date 2: None")
    

    ttk.Button(date2_frame, text="Select Date 2",
            command=lambda: open_calendar(selected_label2, 2)).pack(side="left", padx=(4, 4))

    ttk.Button(date2_frame, text="<", width=1,
            command=lambda: step_date(2, -1, selected_label2)).pack(side="left")
    selected_label2.pack(side="left", padx=(0, 4))

    ttk.Button(date2_frame, text=">", width=1,
            command=lambda: step_date(2, +1, selected_label2)).pack(side="left")


    category_var = tk.StringVar()
    category_dropdown = ttk.Combobox(row3, textvariable=category_var, state="readonly", width=20)
    category_dropdown["values"] = ["students", "utd", "oft", "vtd", "mr", "aircraft", "classroom", "instructor"]
    category_dropdown.set("Select category")
    category_dropdown.pack(side="left", padx=(37,0))

    category_dropdown.bind("<<ComboboxSelected>>",
                        lambda e: display_category(category_var.get()))


    # ---------------- Treeviews ----------------
    tree_frame = ttk.Frame(root)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=(0,10))


    # Treeview 1
    tree1 = ttk.Treeview(tree_frame)
    tree1.pack(side="left", fill="both", expand=True)

    # Treeview 2
    tree2 = ttk.Treeview(tree_frame)
    tree2.pack(side="left", fill="both", expand=True)


    # Shared scroll function
    def sync_scroll(*args):
        tree1.yview(*args)
        tree2.yview(*args)

    # Scrollbar (vertical, shared)
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=sync_scroll)
    scrollbar.pack(side="left", fill="y")

    # Configure trees to update scrollbar
    tree1.configure(yscrollcommand=scrollbar.set)
    tree2.configure(yscrollcommand=scrollbar.set)

    # Optional: also scroll both when using mousewheel
    def on_mousewheel(event):
        tree1.yview_scroll(int(-1*(event.delta/120)), "units")
        tree2.yview_scroll(int(-1*(event.delta/120)), "units")
        return "break"

    tree1.bind("<MouseWheel>", on_mousewheel)
    tree2.bind("<MouseWheel>", on_mousewheel)

    root.mainloop()

if __name__ == "__main__":
    main()