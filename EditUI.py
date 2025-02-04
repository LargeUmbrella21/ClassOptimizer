import tkinter as tk
from tkinter import ttk, messagebox
import random
from pulp import LpProblem, LpVariable, LpMinimize, lpSum

# Data Storage
classes = {}
students = {}
preferences = {}
availabilities = {}
weight_fill = 50

# Function to Run Optimization
def optimize_schedule():
    rankings = {}
    max_dissatisfaction = 10

    for student, top_5 in preferences.items():
        for class_name in classes:
            if class_name in top_5:
                rankings[(student, class_name)] = top_5.index(class_name) + 1
            elif class_name in availabilities.get(student, []):  # Check availability
                rankings[(student, class_name)] = max_dissatisfaction
            else:
                rankings[(student, class_name)] = float('inf')  # Unavailable classes

    # Optimization setup
    problem = LpProblem("TAAssignment", LpMinimize)

    # Decision variables for assignments
    x = LpVariable.dicts("assign", [(s, c) for s in students for c in classes], cat="Binary")
    
    # Penalty variables for unfilled slots
    unfilled_penalty = LpVariable.dicts("unfilled", classes.keys(), lowBound=0, cat="Continuous")

    # Objective: Minimize dissatisfaction and unfilled class penalties
    problem += (
        lpSum(
            rankings[(s, c)] * x[(s, c)] for s in students for c in classes if rankings[(s, c)] != float('inf')
        ) +
        weight_fill*lpSum(unfilled_penalty[c] for c in classes),  # Add penalty for unfilled slots
        "TotalDissatisfaction"
    )
    
    # Constraints: Each student gets one class
    for s in students:
        problem += lpSum(x[(s, c)] for c in classes if rankings[(s, c)] != float('inf')) == 1, f"OneClassPerStudent_{s}"

    # Constraints: Class capacities
    for c in classes:
        # Define the number of assigned students for each class
        assigned_students = lpSum(x[(s, c)] for s in students if rankings[(s, c)] != float('inf'))
        # Enforce the capacity and track unfilled slots
        problem += assigned_students <= classes[c], f"ClassCapacity_{c}"
        problem += unfilled_penalty[c] >= (classes[c] - assigned_students), f"UnfilledPenalty_{c}"

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
        # Get the ranking of the assigned class for the student from the rankings dictionary
        ranking = rankings.get((student, assigned_class), "N/A")
        results_text += f"{student} -> {assigned_class} (Ranking: {ranking})\n"

    results_text += "\nUnfilled Classes:\n"
    for c in classes:
        results_text += f"{c}: {unfilled_penalty[c].value()} unfilled slots\n"

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
        if selected_class not in availability_listbox.get(0, tk.END):
            availability_listbox.insert(tk.END, selected_class)
        top_5_combobox.set("")

# Add Class to Availability List
def add_available_class():
    selected_class = availability_combobox.get()
    if selected_class and selected_class not in availability_listbox.get(0, tk.END):
        availability_listbox.insert(tk.END, selected_class)
        availability_combobox.set("")
    else:
        messagebox.showerror("Error", "Please select a valid class.")

# Add Student with Edit Button
def add_student():
    student_name = student_name_entry.get()
    top_5 = list(top_5_listbox.get(0, tk.END))
    availability = list(availability_listbox.get(0, tk.END))

    if student_name and top_5 and availability:
        students[student_name] = True
        preferences[student_name] = top_5
        availabilities[student_name] = availability
        
        # Create a frame for each student
        student_frame = tk.Frame(student_listbox)
        
        student_label = tk.Label(student_frame, text=f"{student_name}: Top 5 - {top_5}, Available - {availability}")
        student_label.pack(side=tk.LEFT)

        # Add an Edit button to the frame
        edit_button = tk.Button(student_frame, text="Edit", command=lambda: edit_student(student_name))
        edit_button.pack(side=tk.LEFT)

        # Add the frame to the student list container
        student_frame.pack(fill=tk.X, padx=5, pady=2)

        student_name_entry.delete(0, tk.END)
        top_5_listbox.delete(0, tk.END)
        availability_listbox.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Please enter a valid student name and at least one class in Top 5 and Availability.")

# Function to Edit Student Ranking and Availability
def edit_student(student_name):
    if student_name:
        # Show current rankings in the top 5 listbox and availability listbox
        top_5_listbox.delete(0, tk.END)
        availability_listbox.delete(0, tk.END)

        top_5_classes = preferences.get(student_name, [])
        avail_classes = availabilities.get(student_name, [])
        
        for class_name in top_5_classes:
            top_5_listbox.insert(tk.END, class_name)
        for class_name in avail_classes:
            availability_listbox.insert(tk.END, class_name)
        
        # Set up editing for the selected student
        edit_student_window = tk.Toplevel(root)
        edit_student_window.title(f"Edit {student_name}'s Preferences")

        # Ranking Section
        tk.Label(edit_student_window, text="Edit Top 5 Rankings:").grid(row=0, column=0, padx=5, pady=5)
        top_5_combobox = ttk.Combobox(edit_student_window, values=list(classes.keys()), state="readonly")
        top_5_combobox.grid(row=1, column=0, padx=5, pady=5)
        tk.Button(edit_student_window, text="Add to Top 5", command=lambda: add_to_top_5_edit(student_name, top_5_combobox, top_5_listbox)).grid(row=1, column=1, padx=5, pady=5)

        top_5_listbox_edit = tk.Listbox(edit_student_window, width=50, height=5)
        top_5_listbox_edit.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        for item in top_5_classes:
            top_5_listbox_edit.insert(tk.END, item)

        # Availability Section
        tk.Label(edit_student_window, text="Edit Available Classes:").grid(row=3, column=0, padx=5, pady=5)
        availability_combobox = ttk.Combobox(edit_student_window, values=list(classes.keys()), state="readonly")
        availability_combobox.grid(row=4, column=0, padx=5, pady=5)
        tk.Button(edit_student_window, text="Add to Availability", command=lambda: add_to_availability_edit(student_name, availability_combobox, availability_listbox)).grid(row=4, column=1, padx=5, pady=5)

        availability_listbox_edit = tk.Listbox(edit_student_window, width=50, height=5)
        availability_listbox_edit.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
        for item in avail_classes:
            availability_listbox_edit.insert(tk.END, item)

        # Button to save changes
        tk.Button(edit_student_window, text="Save Changes", command=lambda: save_student_changes(student_name, top_5_listbox_edit, availability_listbox_edit)).grid(row=6, column=0, columnspan=2, pady=10)

# Function to add selected class to Top 5 Rankings
def add_to_top_5_edit(student_name, combobox, listbox):
    selected_class = combobox.get()
    if selected_class and selected_class not in listbox.get(0, tk.END) and len(listbox.get(0, tk.END)) < 5:
        listbox.insert(tk.END, selected_class)
        combobox.set("")
    elif len(listbox.get(0, tk.END)) >= 5:
        messagebox.showerror("Error", "You can only add up to 5 classes to the Top 5 list.")
    else:
        messagebox.showerror("Error", "Please select a valid class.")

# Function to add selected class to Availability List
def add_to_availability_edit(student_name, combobox, listbox):
    selected_class = combobox.get()
    if selected_class and selected_class not in listbox.get(0, tk.END):
        listbox.insert(tk.END, selected_class)
        combobox.set("")
    else:
        messagebox.showerror("Error", "Please select a valid class.")

# Function to save changes to the student
def save_student_changes(student_name, top_5_listbox, availability_listbox):
    updated_top_5 = list(top_5_listbox.get(0, tk.END))
    updated_availability = list(availability_listbox.get(0, tk.END))
    
    if updated_top_5 and updated_availability:
        preferences[student_name] = updated_top_5
        availabilities[student_name] = updated_availability
        update_student_listbox(student_name)
        messagebox.showinfo("Success", f"Changes saved for {student_name}.")
    else:
        messagebox.showerror("Error", "Please ensure Top 5 and Availability lists are not empty.")

# Function to update the student listbox with changes
def update_student_listbox(student_name):
    index = next((i for i, item in enumerate(student_listbox.get(0, tk.END)) if item.startswith(student_name)), None)
    if index is not None:
        student_listbox.delete(index)
        student_listbox.insert(index, f"{student_name}: Top 5 - {preferences[student_name]}, Available - {availabilities[student_name]}")

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

tk.Button(manage_students_tab, text="Randomize Students", command=randomize_students).grid(row=0, column=2, padx=5, pady=5)

tk.Label(manage_students_tab, text="Top 5 Classes:").grid(row=1, column=0, padx=5, pady=5)
top_5_combobox = ttk.Combobox(manage_students_tab, state="readonly")
top_5_combobox.grid(row=1, column=1, padx=5, pady=5)
tk.Button(manage_students_tab, text="Add to Top 5", command=add_top_5_class).grid(row=1, column=2, padx=5, pady=5)

top_5_listbox = tk.Listbox(manage_students_tab, width=30, height=5)
top_5_listbox.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

tk.Label(manage_students_tab, text="Available Classes:").grid(row=3, column=0, padx=5, pady=5)
availability_combobox = ttk.Combobox(manage_students_tab, state="readonly")
availability_combobox.grid(row=3, column=1, padx=5, pady=5)
tk.Button(manage_students_tab, text="Add to Availability", command=add_available_class).grid(row=3, column=2, padx=5, pady=5)

availability_listbox = tk.Listbox(manage_students_tab, width=30, height=5)
availability_listbox.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

tk.Button(manage_students_tab, text="Add Student", command=add_student).grid(row=5, column=0, columnspan=3, pady=10)

student_listbox = tk.Frame(manage_students_tab, width=50)  # Frame to hold student list
student_listbox.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

# Optimize Schedule Tab
tk.Button(optimize_tab, text="Optimize Schedule", command=optimize_schedule).pack(pady=20)

# Run the Application
root.mainloop()
