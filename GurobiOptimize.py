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
    max_dissatisfaction = 10
    for student, top_5 in preferences.items():
        for class_name in classes:
            if class_name in top_5:
                rankings[(student, class_name)] = top_5.index(class_name) + 1
            elif class_name in availabilities[student]:
                rankings[(student, class_name)] = max_dissatisfaction
            else:
                rankings[(student, class_name)] = float('inf')  # Unavailable classes

    # Optimization setup
    problem = LpProblem("TAAssignment", LpMinimize)
    x = LpVariable.dicts("assign", [(s, c) for s in students for c in classes], cat="Binary")

    # Objective: Minimize dissatisfaction
    problem += lpSum(rankings[(s, c)] * x[(s, c)] for s in students for c in classes if rankings[(s, c)] != float('inf')), "TotalDissatisfaction"

    # Constraints: Each student gets one class
    for s in students:
        problem += lpSum(x[(s, c)] for c in classes if rankings[(s, c)] != float('inf')) == 1, f"OneClassPerStudent_{s}"

    # Constraints: Class capacities
    for c in classes:
        problem += lpSum(x[(s, c)] for s in students if rankings[(s, c)] != float('inf')) <= classes[c], f"ClassCapacity_{c}"

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
        update_class_dropdowns()
    else:
        messagebox.showerror("Error", "Please enter a valid class name and capacity.")

# Update Dropdowns for Classes
def update_class_dropdowns():
    class_list = list(classes.keys())
    top_5_combobox["values"] = class_list
    availability_combobox["values"] = class_list

# Add Class to Top 5 List
def add_top_5_class():
    selected_class = top_5_combobox.get()
    if selected_class and selected_class not in top_5_listbox.get(0, tk.END) and len(top_5_listbox.get(0, tk.END)) < 5:
        top_5_listbox.insert(tk.END, selected_class)
        # Automatically add the class to the availability list
        if selected_class not in availability_listbox.get(0, tk.END):
            availability_listbox.insert(tk.END, selected_class)
        top_5_combobox.set("")
    elif len(top_5_listbox.get(0, tk.END)) >= 5:
        messagebox.showerror("Error", "You can only add up to 5 classes to the Top 5 list.")
    else:
        messagebox.showerror("Error", "Please select a valid class.")

# Add Class to Availability List
def add_available_class():
    selected_class = availability_combobox.get()
    if selected_class and selected_class not in availability_listbox.get(0, tk.END):
        availability_listbox.insert(tk.END, selected_class)
        availability_combobox.set("")
    else:
        messagebox.showerror("Error", "Please select a valid class.")

# Add Student
def add_student():
    student_name = student_name_entry.get()
    top_5 = list(top_5_listbox.get(0, tk.END))
    availability = list(availability_listbox.get(0, tk.END))

    if student_name and top_5 and availability:
        students[student_name] = True
        preferences[student_name] = top_5
        availabilities[student_name] = availability
        student_listbox.insert(tk.END, f"{student_name}: Top 5 - {top_5}, Available - {availability}")
        student_name_entry.delete(0, tk.END)
        top_5_listbox.delete(0, tk.END)
        availability_listbox.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Please enter a valid student name and at least one class in Top 5 and Availability.")

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

# Top 5 Classes Section
tk.Label(manage_students_tab, text="Top 5 Classes:").grid(row=1, column=0, padx=5, pady=5)
top_5_combobox = ttk.Combobox(manage_students_tab, state="readonly")
top_5_combobox.grid(row=1, column=1, padx=5, pady=5)
tk.Button(manage_students_tab, text="Add to Top 5", command=add_top_5_class).grid(row=1, column=2, padx=5, pady=5)

top_5_listbox = tk.Listbox(manage_students_tab, width=30, height=5)
top_5_listbox.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

# Availability Section
tk.Label(manage_students_tab, text="Available Classes:").grid(row=3, column=0, padx=5, pady=5)
availability_combobox = ttk.Combobox(manage_students_tab, state="readonly")
availability_combobox.grid(row=3, column=1, padx=5, pady=5)
tk.Button(manage_students_tab, text="Add to Availability", command=add_available_class).grid(row=3, column=2, padx=5, pady=5)

availability_listbox = tk.Listbox(manage_students_tab, width=30, height=5)
availability_listbox.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

tk.Button(manage_students_tab, text="Add Student", command=add_student).grid(row=5, column=0, columnspan=3, pady=10)

student_listbox = tk.Listbox(manage_students_tab, width=50)
student_listbox.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

# Optimize Schedule Tab
tk.Button(optimize_tab, text="Optimize Schedule", command=optimize_schedule).pack(pady=20)

# Run the Application
root.mainloop()
