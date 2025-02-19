import pandas as pd
import re
from tkinter import Tk, filedialog
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, PULP_CBC_CMD

def get_file_path(prompt):
    """Opens a file dialog and returns the selected file path."""
    Tk().withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(title=prompt, filetypes=[("Excel files", "*.xlsx;*.xls")])
    return file_path

def sanitize_name(name):
    """Sanitize class names by replacing spaces and special characters with underscores."""
    return re.sub(r'[^\w]', '_', str(name))

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

    # Sanitize class names
    class_df["Class"] = class_df["Class"].apply(sanitize_name)

    # Extract class information
    classes = class_df.set_index("Class")["Capacity"].to_dict()
    
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
                class_name = sanitize_name(col.split("[")[1].strip("]") if "[" in col and "]" in col else col.replace("Rank ", "").strip())
                ranks[class_name] = int(row[col])
            elif "Available" in col and row[col] == "Available":
                class_name = sanitize_name(col.split("[")[1].strip("]") if "[" in col and "]" in col else col.replace("Available ", "").strip())
                available_classes.append(class_name)

        preferences[student_name] = ranks
        availabilities[student_name] = available_classes

    print("\n📌 Student Preferences:")
    for student, ranks in preferences.items():
        print(f"  - {student}: {ranks}")

    print("\n📌 Student Availabilities:")
    for student, available_classes in availabilities.items():
        print(f"  - {student}: {available_classes}")

    max_dissatisfaction = 10
    weight_fill = 50  
    rankings = {}

    for student, ranks in preferences.items():
        for class_name in classes:
            if class_name in ranks:
                rankings[(student, class_name)] = ranks[class_name]
            elif class_name in availabilities.get(student, []):
                rankings[(student, class_name)] = max_dissatisfaction
            else:
                rankings[(student, class_name)] = float('inf')

    print("\n📌 Student Rankings for Classes:")
    for (student, class_name), rank in rankings.items():
        if rank != float('inf'):
            print(f"  - {student} -> {class_name}: Rank {rank}")

    # Optimization problem setup
    problem = LpProblem("TAAssignment", LpMinimize)
    x = LpVariable.dicts("assign", [(s, c) for s in students for c in classes], cat="Binary")
    unfilled_penalty = LpVariable.dicts("unfilled", classes.keys(), lowBound=0, cat="Continuous")

    problem += (
        lpSum(rankings[(s, c)] * x[(s, c)] for s in students for c in classes if rankings[(s, c)] != float('inf'))
        + weight_fill * lpSum(unfilled_penalty[c] for c in classes),
        "TotalDissatisfaction"
    )

    for s in students:
        problem += lpSum(x[(s, c)] for c in classes if rankings[(s, c)] != float('inf')) == 1, f"OneClassPerStudent_{s}"

    for c in classes:
        assigned_students = lpSum(x[(s, c)] for s in students if rankings[(s, c)] != float('inf'))
        problem += assigned_students <= classes[c], f"ClassCapacity_{c}"
        problem += unfilled_penalty[c] >= (classes[c] - assigned_students), f"UnfilledPenalty_{c}"

    # Solve the problem
    problem.solve()

    total_dissatisfaction = problem.objective.value()
    print(f"\n✅ Total Dissatisfaction: {total_dissatisfaction}")

    unfilled_classes = {c: unfilled_penalty[c].value() for c in classes if unfilled_penalty[c].value() > 0}
    print("\n📌 Unfilled Classes and Slots:", unfilled_classes)

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

    # Debugging: Why are classes going unfilled?
    print("\n🔍 Debugging Unfilled Classes:")
    for c in classes:
        capacity = classes[c]
        assigned = sum(1 for s in students if x.get((s, c), None) and x[(s, c)].value() == 1)
        if assigned < capacity:
            print(f"⚠️ {c} has {capacity - assigned} unfilled spots.")
            available_students = [s for s in students if rankings.get((s, c), float('inf')) != float('inf')]
            if not available_students:
                print(f"   🚨 No students available for {c}")
            else:
                print(f"   🔹 Available students but not assigned: {available_students}")

# Run the function
optimize_schedule()

input("Press Enter to exit...")
