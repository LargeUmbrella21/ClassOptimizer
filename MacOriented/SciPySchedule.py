import pandas as pd
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import numpy as np
from scipy.optimize import linear_sum_assignment

def sanitize_name(name):
    return name.strip().replace("[", "").replace("]", "")

# Create the main Tkinter root window (hidden initially)
root = tk.Tk()
root.withdraw()

def get_file_path(prompt):
    """Opens a file dialog and returns the selected file path using Tkinter."""
    file_path = filedialog.askopenfilename(title=prompt, filetypes=[("Excel Files", "*.xlsx;*.xls")])
    return file_path

def show_results_window(result_text):
    """Displays the optimization results in a scrollable Tkinter window."""
    result_window = tk.Toplevel(root)
    result_window.title("Optimization Results")
    result_window.geometry("600x400")

    text_area = scrolledtext.ScrolledText(result_window, wrap=tk.WORD, width=70, height=20)
    text_area.insert(tk.INSERT, result_text)
    text_area.config(state=tk.DISABLED)
    text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    close_button = tk.Button(result_window, text="Close", command=result_window.destroy)
    close_button.pack(pady=5)

    quit_button = tk.Button(result_window, text="Quit Program", command=root.quit)
    quit_button.pack(pady=5)

def optimize_schedule():
    """Runs the optimization process and displays results using SciPy."""
    student_file = get_file_path("Select Student File")
    class_file = get_file_path("Select Class File")

    if not student_file or not class_file:
        messagebox.showerror("Error", "File selection canceled.")
        return

    student_df = pd.read_excel(student_file)
    class_df = pd.read_excel(class_file, names=["Class", "Capacity"])
    class_df["Class"] = class_df["Class"].apply(sanitize_name)
    
    expanded_classes = []
    class_capacities = {}
    for _, row in class_df.iterrows():
        class_name = row["Class"]
        capacity = int(row["Capacity"])
        for i in range(capacity):
            expanded_classes.append(f"{class_name}_{i+1}")
        class_capacities[class_name] = capacity
    
    students = student_df["First Name"] + " " + student_df["Last Name"]
    preferences = {}
    availabilities = {}
    
    for _, row in student_df.iterrows():
        student_name = row["First Name"] + " " + row["Last Name"]
        ranks = {}
        available_classes = []

        for col in student_df.columns[2:]:
            if "Rank" in col and pd.notna(row[col]):
                class_name = sanitize_name(col.split("[")[1].strip("]") if "[" in col and "]" in col else col.replace("Rank ", "").strip())
                ranks[class_name] = int(row[col])
            elif "Available" in col and row[col] == "Available":
                class_name = sanitize_name(col.split("[")[1].strip("]") if "[" in col and "]" in col else col.replace("Available ", "").strip())
                available_classes.append(class_name)
        
        preferences[student_name] = ranks
        availabilities[student_name] = available_classes
    
    max_dissatisfaction = 10
    num_students = len(students)
    num_expanded_classes = len(expanded_classes)
    cost_matrix = np.full((num_students, num_expanded_classes), np.inf)

    student_list = list(students)
    class_list = expanded_classes
    
    for i, student in enumerate(student_list):
        for j, expanded_class in enumerate(class_list):
            base_class = "_".join(expanded_class.split("_")[:-1])
            if base_class in preferences[student]:
                cost_matrix[i, j] = preferences[student][base_class]
            elif base_class in availabilities.get(student, []):
                cost_matrix[i, j] = max_dissatisfaction
    
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    total_dissatisfaction = cost_matrix[row_ind, col_ind].sum()

    result_lines = []
    assigned_students = set()
    for i, j in zip(row_ind, col_ind):
        result_lines.append(f"{student_list[i]} -> {class_list[j].split('_')[0]} (Rank: {int(cost_matrix[i, j])})")
        assigned_students.add(student_list[i])
    
    unassigned_students = set(student_list) - assigned_students
    for student in unassigned_students:
        result_lines.append(f"{student} -> No Class Assigned")
    
    result_text = f"Total Dissatisfaction: {total_dissatisfaction}\n\nAssignments:\n" + "\n".join(result_lines)
    show_results_window(result_text)

if __name__ == "__main__":
    optimize_schedule()
    root.mainloop()
