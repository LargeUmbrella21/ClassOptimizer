import pandas as pd
from collections import defaultdict

class ScheduleOptimizer:
    def __init__(self, students_file, classes_file):
        # Read student preferences and availability
        self.students_df = pd.read_excel(students_file)
        # Read class capacities
        self.classes_df = pd.read_excel(classes_file, header=None, names=["Class", "Spots"])

        # Initialize data structures
        self.student_rankings = {}
        self.class_capacities = {}
        self.assigned_classes = defaultdict(list)

        # Load data from spreadsheets
        self._load_students()
        self._load_classes()

    def _load_students(self):
        # Extract student names and preferences
        for _, row in self.students_df.iterrows():
            student_name = row[0]
            preferences = row[1:].dropna().to_dict()
            rankings = {k: int(v) for k, v in preferences.items() if pd.notna(v)}
            self.student_rankings[student_name] = rankings

    def _load_classes(self):
        # Extract class capacities
        for _, row in self.classes_df.iterrows():
            class_name = row["Class"]
            capacity = int(row["Spots"])
            self.class_capacities[class_name] = capacity

    def optimize_schedule(self):
        # Simple greedy optimization: Assign students by preference order
        for student, rankings in self.student_rankings.items():
            # Sort preferences by rank (1 is highest preference)
            sorted_classes = sorted(rankings, key=rankings.get)
            
            for class_name in sorted_classes:
                # Assign student if capacity allows
                if self.class_capacities[class_name] > 0:
                    self.assigned_classes[class_name].append(student)
                    self.class_capacities[class_name] -= 1
                    break  # Move to the next student

    def get_results(self):
        # Return a DataFrame of class assignments
        result = []
        for class_name, students in self.assigned_classes.items():
            for student in students:
                result.append([class_name, student])
        return pd.DataFrame(result, columns=["Class", "Student"])

# Example usage:
# optimizer = ScheduleOptimizer("students.xlsx", "classes.xlsx")
# optimizer.optimize_schedule()
# results_df = optimizer.get_results()
# results_df.to_excel("schedule_results.xlsx", index=False)

print("Upload your student and class spreadsheets.")
