import tkinter as tk
from tkinter import ttk, messagebox
from pulp import LpProblem, LpVariable, LpMinimize, lpSum

# Data Storage
classes = {}
students = {}
preferences = {}
availabilities = {}

# Function to Run Optimization
def optimize_schedule():
    # Create the rankings dictionary based on preferences and availabilities
    rankings = {}
    max_dissatisfaction = 50  # Adjust for a high dissatisfaction penalty
    unavailability_dissatisfaction = 1000  # Very high for unavailable classes
    empty_slot_dissatisfaction = 200  # High dissatisfaction for empty class slots

    for student, top_5 in preferences.items():
        for class_name in classes:
            if class_name in top_5:
                rankings[(student, class_name)] = top_5.index(class_name) + 1
            elif class_name in availabilities[student]:
                rankings[(student, class_name)] = max_dissatisfaction
            else:
                rankings[(student, class_name)] = unavailability_dissatisfaction  # Unavailable classes
'''
    # Optimization setup
    problem = LpProblem("TAAssignment", LpMinimize)
    x = LpVariable.dicts("assign", [(s, c) for s in students for c in classes], cat="Binary")
    y = LpVariable.dicts("empty_slot", classes.keys(), lowBound=0, cat="Integer")  # Unfilled slots per class

    # Objective: Minimize dissatisfaction
    problem += (
        lpSum(
            rankings[(s, c)] * x[(s, c)]
            for s in students
            for c in classes
            if rankings[(s, c)] != unavailability_dissatisfaction
        )
        + lpSum(empty_slot_dissatisfaction * y[c] for c in classes),
        "TotalDissatisfaction",
    )

    # Constraints: Each student gets one class
    for s in students:
        problem += lpSum(x[(s, c)] for c in classes if rankings[(s, c)] != unavailability_dissatisfaction) == 1, f"OneClassPerStudent_{s}"

    # Constraints: Class capacities and empty slots
    for c in classes:
        problem += lpSum(x[(s, c)] for s in students if rankings[(s, c)] != unavailability_dissatisfaction) + y[c] == classes[c], f"ClassCapacity_{c}"

    # Solve the problem
    problem.solve()

    # Output results
    assignments = {}
    for s in students:
        for c in classes:
            if x[(s, c)].value() == 1:
                assignments[s] = c

    # Display Results
    results_window = tk.Toplevel(root)
    results_window.title("Optimization Results")
    results_text = f"Total Dissatisfaction: {problem.objective.value()}\n\nAssignments:\n"
    for student, assigned_class in assignments.items():
        results_text += f"{student} -> {assigned_class}\n"
    results_text += "\nUnfilled Slots:\n"
    for c in classes:
        if y[c].value() > 0:
            results_text += f"{c}: {int(y[c].value())} slots unfilled\n"

    tk.Label(results_window, text=results_text, justify="left").pack(padx=10, pady=10)
'''
def optimize_schedule():
    # Create the rankings dictionary based on preferences and availabilities
    rankings = {}
    max_dissatisfaction = 10  # High dissatisfaction for available but not preferred classes
    unavailability_dissatisfaction = float('inf')  # Infinite dissatisfaction for unavailable classes

    for student, top_5 in preferences.items():
        for class_name in classes:
            if class_name in top_5:
                rankings[(student, class_name)] = top_5.index(class_name) + 1
            elif class_name in availabilities[student]:
                rankings[(student, class_name)] = max_dissatisfaction
            else:
                rankings[(student, class_name)] = unavailability_dissatisfaction  # Unavailable classes

    # Initialize the problem
    problem = LpProblem("TAAssignment", LpMinimize)

    # Decision variables: x[s, c] = 1 if student s gets class c, 0 otherwise
    x = LpVariable.dicts("assign", [(s, c) for s in students for c in classes], cat="Binary")

    # Objective function: Minimize total dissatisfaction
    problem += lpSum(rankings[(s, c)] * x[(s, c)] for s in students for c in classes if rankings[(s, c)] != unavailability_dissatisfaction), "TotalDissatisfaction"

    # Constraints
    # Each student gets exactly one class
    for s in students:
        problem += lpSum(x[(s, c)] for c in classes if rankings[(s, c)] != unavailability_dissatisfaction) == 1, f"OneClassPerStudent_{s}"

    # Each class is assigned according to its capacity
    for c in classes:
        problem += lpSum(x[(s, c)] for s in students if rankings[(s, c)] != unavailability_dissatisfaction) <= classes[c], f"ClassCapacity_{c}"

    # Solve the problem
    problem.solve()

    # Output results
    assignments = {}
    for s in students:
        for c in classes:
            if x[(s, c)].value() == 1:
                assignments[s] = c

    # Display Results
    results_window = tk.Toplevel(root)
    results_window.title("Optimization Results")
    results_text = f"Total Dissatisfaction: {problem.objective.value()}\n\nAssignments:\n"
    for student, assigned_class in assignments.items():
        rank = rankings[(student, assigned_class)]
        if rank <= 5:
            rank_status = f"Rank {rank}"
        else:
            rank_status = "Available (High Dissatisfaction)"
        results_text += f"{student} -> {assigned_class} ({rank_status})\n"

    # Check for unassignable students
    unassignable = [s for s in students if s not in assignments]
    if unassignable:
        results_text += "\nUnassignable Students (No Available Classes):\n"
        results_text += "\n".join(unassignable)

    tk.Label(results_window, text=results_text, justify="left").pack(padx=10, pady=10)


# Add Class
def add_class():
    class_name = class_name_entry.get()
    capacity = capacity_entry.get()
    if class_name and capacity.isdigit():
        classes[class_name] = int(capacity)
        class_listbox.insert(tk.END, f"{class_name} (Capacity: {capacity})")
        class_name_entry.delete(0, tk.END)
        capacity_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Please enter a valid class name and capacity.")

# Add Student
def add_student():
    student_name = student_name_entry.get()
    top_5 = top_5_entry.get().split(",")
    availability = availability_entry.get().split(",")
    if student_name and top_5 and availability:
        students[student_name] = True
        preferences[student_name] = top_5
        availabilities[student_name] = availability
        student_listbox.insert(tk.END, f"{student_name}: Top 5 - {top_5}, Available - {availability}")
        student_name_entry.delete(0, tk.END)
        top_5_entry.delete(0, tk.END)
        availability_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Please enter valid student details.")

# GUI
root = tk.Tk()
root.title("TA Assignment Scheduler")

# Tabs
tab_control = ttk.Notebook(root)
manage_classes_tab = ttk.Frame(tab_control)
manage_students_tab = ttk.Frame(tab_control)
optimize_tab = ttk.Frame(tab_control)
tab_control.add(manage_classes_tab, text="Manage Classes")
tab_control.add(manage_students_tab, text="Manage Students")
tab_control.add(optimize_tab, text="Optimize Schedule")
tab_control.pack(expand=1, fill="both")

# Manage Classes Tab
tk.Label(manage_classes_tab, text="Class Name:").grid(row=0, column=0, padx=5, pady=5)
class_name_entry = tk.Entry(manage_classes_tab)
class_name_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(manage_classes_tab, text="Capacity:").grid(row=1, column=0, padx=5, pady=5)
capacity_entry = tk.Entry(manage_classes_tab)
capacity_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Button(manage_classes_tab, text="Add Class", command=add_class).grid(row=2, column=0, columnspan=2, pady=5)

class_listbox = tk.Listbox(manage_classes_tab, width=50)
class_listbox.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

# Manage Students Tab
tk.Label(manage_students_tab, text="Student Name:").grid(row=0, column=0, padx=5, pady=5)
student_name_entry = tk.Entry(manage_students_tab)
student_name_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(manage_students_tab, text="Top 5 Classes (comma-separated):").grid(row=1, column=0, padx=5, pady=5)
top_5_entry = tk.Entry(manage_students_tab)
top_5_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(manage_students_tab, text="Availability (comma-separated):").grid(row=2, column=0, padx=5, pady=5)
availability_entry = tk.Entry(manage_students_tab)
availability_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Button(manage_students_tab, text="Add Student", command=add_student).grid(row=3, column=0, columnspan=2, pady=5)

student_listbox = tk.Listbox(manage_students_tab, width=50)
student_listbox.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

# Optimize Schedule Tab
tk.Button(optimize_tab, text="Optimize Schedule", command=optimize_schedule).pack(pady=20)

# Run the Application
root.mainloop()
