import pandas as pd
from tkinter import Tk, filedialog
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, PULP_CBC_CMD
from collections import defaultdict

cbc_path = "cbc.exe"  # Ensure this is the correct relative path
solver = PULP_CBC_CMD(path=cbc_path)

def get_file_path(prompt):
    """Opens a file dialog and returns the selected file path."""
    Tk().withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(title=prompt, filetypes=[("Excel files", "*.xlsx;*.xls")])
    return file_path

def optimize_schedule():
    # Ask user to upload files
    student_file = get_file_path("Select Student File")
    class_file = get_file_path("Select Class File")

    if not student_file or not class_file:
        print("File selection canceled.")
        return

    print(f"Student file: {student_file}")
    print(f"Class file: {class_file}")

    # Load Data
    student_df = pd.read_excel(student_file)
    class_df = pd.read_excel(class_file, names=["Class", "Capacity"])

    # Extract class information
    classes = class_df.set_index("Class")["Capacity"].to_dict()
    
    # Debug: Print class list and capacities
    print("\n📌 Class List and Capacities:")
    for cls, cap in classes.items():
        print(f"  - {cls}: {cap} spots")

    # Extract student preferences and availability
    students = student_df["First Name"] + " " + student_df["Last Name"]
    preferences = {}
    availabilities = {}

    for _, row in student_df.iterrows():
        student_name = row["First Name"] + " " + row["Last Name"]
        ranks = {}
        available_classes = []

        for col in student_df.columns[2:]:
            if "Rank" in col and pd.notna(row[col]):
                if "[" in col and "]" in col:
                    class_name = col.split("[")[1].strip("]")
                else:
                    class_name = col.replace("Rank ", "").strip()
                ranks[class_name] = int(row[col])
            elif "Available" in col and row[col] == "Available":
                if "[" in col and "]" in col:
                    class_name = col.split("[")[1].strip("]")
                else:
                    class_name = col.replace("Available ", "").strip()
                available_classes.append(class_name)

        preferences[student_name] = ranks
        availabilities[student_name] = available_classes

    # Debug: Print student preferences
    print("\n📌 Student Preferences:")
    for student, ranks in preferences.items():
        print(f"  - {student}: {ranks}")

    # Debug: Print student availabilities
    print("\n📌 Student Availabilities:")
    for student, available_classes in availabilities.items():
        print(f"  - {student}: {available_classes}")

    # Set high dissatisfaction value for unavailable classes
    # Set high dissatisfaction value for unavailable classes
    max_dissatisfaction = 10
    weight_fill = 50 # Penalty for unfilled classes
    rankings = {}

    # First, assign rankings for available classes
    for student, ranks in preferences.items():
        for class_name in classes:
            if class_name in ranks:  # Student has a rank for this class
                rankings[(student, class_name)] = ranks[class_name]
            elif class_name in availabilities.get(student, []):  # Student is available for this class
                rankings[(student, class_name)] = max_dissatisfaction  # Low rank for available class
            else:  # Student is neither available nor has a rank for this class
                rankings[(student, class_name)] = float('inf')  # No valid rank for this class

    # Debug: Print rankings before optimization
    print("\n📌 Student Rankings for Classes:")
    for (student, class_name), rank in rankings.items():
        if rank != float('inf'):
            print(f"  - {student} -> {class_name}: Rank {rank}")

    # Optimization problem setup
    problem = LpProblem("TAAssignment", LpMinimize)
    x = LpVariable.dicts("assign", [(s, c) for s in students for c in classes], cat="Binary")
    unfilled_penalty = LpVariable.dicts("unfilled", classes.keys(), lowBound=0, cat="Continuous")

    # Objective function: Minimize dissatisfaction + weight of unfilled classes
    problem += (
        lpSum(rankings[(s, c)] * x[(s, c)] for s in students for c in classes if rankings[(s, c)] != float('inf'))
        + weight_fill * lpSum(unfilled_penalty[c] for c in classes),
        "TotalDissatisfaction"
    )

    # Constraints: Each student gets one class
    for s in students:
        problem += lpSum(x[(s, c)] for c in classes if rankings[(s, c)] != float('inf')) == 1, f"OneClassPerStudent_{s}"

    # Constraints: Class capacities
    for c in classes:
        assigned_students = lpSum(x[(s, c)] for s in students if rankings[(s, c)] != float('inf'))
        problem += assigned_students <= classes[c], f"ClassCapacity_{c}"
        problem += unfilled_penalty[c] >= (classes[c] - assigned_students), f"UnfilledPenalty_{c}"

    # Solve the problem
    problem.solve(solver)

    # Extract total dissatisfaction
    total_dissatisfaction = problem.objective.value()
    print(f"\n✅ Total Dissatisfaction: {total_dissatisfaction}")

    # Extract unfilled classes and slots
    unfilled_classes = {c: unfilled_penalty[c].value() for c in classes if unfilled_penalty[c].value() > 0}
    print("\n📌 Unfilled Classes and Slots:", unfilled_classes)

    # Extract each student's assigned class and their rank
    assignments = {}
    print("\n📌 Student Assignments:")
    for s in students:
        for c in classes:
            if x[(s, c)].value() == 1:
                rank = rankings.get((s, c), max_dissatisfaction)
                assignments[s] = (c, rank)
                print(f"  - {s} assigned to {c} with rank {rank}")
    if not assignments:
        print("⚠️ No student assignments were made! Check constraints.")

# Run the function
optimize_schedule()

# Add this line to keep the window open
input("Press Enter to exit...")