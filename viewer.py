
import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from datetime import datetime
import os
import json

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

    cal.tag_config("available", background="lightblue", foreground="lightblue")

    def confirm_date():
        # Calendar returns MM/DD/YY

        global selected_date1, selected_date2
        date_str = cal.get_date()
        date = datetime.strptime(date_str, "%m/%d/%y").strftime("%Y-%m-%d")

        if date not in valid_dates:
            print("Selected date has no data:", date)
            return
    
        if date_number == 1:
            selected_date1 = date
        else:
            selected_date2 = date

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


# ---------------- Display category ----------------
def display_category(category):
    for tree in [tree1, tree2]:
        for item in tree.get_children():
            tree.delete(item)

    # Helper to populate a treeview for a given date
    def populate_tree(tree, date):
        if not date:
            return
        runs = data_by_date.get(date, [])
        if not runs:
            return
        grouped = {}
        for run in runs:
            pct = run["pct"]
            cls = run["class"]
            day = run["day"]
            grouped.setdefault(pct, {}).setdefault(cls, [])

            if category == "students":
                blocks = day.get("students", {}).get("by_block", {})
                for k, v in blocks.items():
                    grouped[pct][cls].append((k, v))
            else:
                resources = day.get("resources", {}).get(category, {})
                for name, vals in resources.items():
                    grouped[pct][cls].append((
                        name,
                        f"used={vals['hours_used']:.2f} avail={vals['hours_available']:.2f} uses={vals['uses']}"
                    ))

        for pct in sorted(grouped):
            try:
                pct_num = int(pct.replace("pct",""))
                pct_label = f"Percentage {pct_num}%"
            except:
                pct_label = pct
            pct_id = tree.insert("", "end", text=pct_label, open=True)
            for cls in sorted(grouped[pct]):
                try:
                    cls_num = int(cls.replace("class",""))
                    cls_label = f"Class up size: {cls_num}"
                except:
                    cls_label = cls

                if category == "students":
                    total = sum([v for _, v in grouped[pct][cls]])
                    cls_id = tree.insert(pct_id, "end", text=f"{cls_label}: SIT: {total}", open=True)
                    for block, val in grouped[pct][cls]:
                        tree.insert(cls_id, "end", text=f"{block}: {val}")
                else:
                    if not grouped[pct][cls]:
                        continue
                    cls_id = tree.insert(pct_id, "end", text=f"{cls_label}: {grouped[pct][cls][0][0]} | {grouped[pct][cls][0][1]}", open=True)
                    for name, info in grouped[pct][cls][1:]:
                        tree.insert(cls_id, "end", text=f"{name} | {info}")

    populate_tree(tree1, selected_date1)
    populate_tree(tree2, selected_date2)

  
def main():
    global root, category_var, category_dropdown, tree1, tree2, data_by_date, valid_dates

    data_by_date = load_simulation_data()
    valid_dates = set(data_by_date.keys())
    # print("Valid dates loaded:", sorted(valid_dates))

    root = tk.Tk()
    root.title("Simulation Viewer")
    root.geometry("1000x600")

    # ---------------- Top control bar ----------------
    top_frame = ttk.Frame(root)
    top_frame.pack(fill="x", padx=10, pady=10)

    #   # Date 1
    # selected_label1 = ttk.Label(top_frame, text="Selected Date 1: None")
    # selected_label1.pack(side="right", padx=(10,0))
    # ttk.Button(top_frame, text="Select Date 1", command=lambda: open_calendar(selected_label1, 1)).pack(side="left", padx=(0,10))

    # # Date 2
    # selected_label2 = ttk.Label(top_frame, text="Selected Date 2: None")
    # selected_label2.pack(side="right", padx=(10,0))
    # ttk.Button(top_frame, text="Select Date 2", command=lambda: open_calendar(selected_label2, 2)).pack(side="left", padx=(0,10))

    # ---- Date 1 button + label ----
    date1_frame = ttk.Frame(top_frame)
    date1_frame.pack(side="left", padx=(0, 20))  # small padding between Date 1 and Date 2

    select_date_btn1 = ttk.Button(date1_frame, text="Select Date 1",
                                command=lambda: open_calendar(selected_label1, 1))
    select_date_btn1.pack(side="left")

    selected_label1 = ttk.Label(date1_frame, text="None")
    selected_label1.pack(side="left", padx=(5,0))  # small gap after button

    # ---- Date 2 button + label ----
    date2_frame = ttk.Frame(top_frame)
    date2_frame.pack(side="left", padx=(0, 20))

    select_date_btn2 = ttk.Button(date2_frame, text="Select Date 2",
                                command=lambda: open_calendar(selected_label2, 2))
    select_date_btn2.pack(side="left")

    selected_label2 = ttk.Label(date2_frame, text="None")
    selected_label2.pack(side="left", padx=(5,0))



    # Category dropdown
    category_var = tk.StringVar()
    category_dropdown = ttk.Combobox(
        top_frame,
        textvariable=category_var,
        state="readonly",
        width=20
    )
    category_dropdown["values"] = [
        "students",
        "utd",
        "oft",
        "vtd",
        "mr",
        "aircraft",
        "instructor"
    ]
    category_dropdown.set("Select category")
    category_dropdown.pack(side="left")

    # Trigger display when category is selected
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