import random
from pulp import LpProblem, LpVariable, LpMinimize, lpSum

# Example Data
people = [
    'Alice', 'Bob', 'Charlie', 'Dana', 'Eve', 'Frank', 'Grace', 'Hannah', 'Ian', 'Jack',
    'Karen', 'Leo', 'Mona', 'Nina', 'Oscar', 'Paul', 'Quinn', 'Rachel', 'Steve', 'Tina'
]
fruits = ['Apple', 'Banana', 'Cherry', 'Date', 'Elderberry', 'Fig', 'Grape']

# Quantities of each fruit
fruit_quantities = {'Apple': 1, 'Banana': 3, 'Cherry': 2, 'Date': 3, 'Elderberry': 4, 'Fig': 4, 'Grape': 3}

# Popularity index for fruits (higher = more popular)
fruit_popularity = {'Apple': 0.9, 'Banana': 0.1, 'Cherry': 0.9, 'Date': 0.1, 'Elderberry': 0.1, 'Fig': 0.1, 'Grape': 0.3}

# Generate randomized rankings based on popularity
top_5_rankings = {}
for person in people:
    top_5 = random.choices(fruits, weights=fruit_popularity.values(), k=5)
    top_5_rankings[person] = list(dict.fromkeys(top_5))  # Remove duplicates while preserving order

# Randomize allergies for the remaining two fruits per person
allergies = {}
for person in people:
    ranked_fruits = set(top_5_rankings[person])
    unranked_fruits = [fruit for fruit in fruits if fruit not in ranked_fruits]
    allergies[person] = {fruit: random.choice([True, False]) for fruit in unranked_fruits}

# Create a dissatisfaction score for fruits not in top 5
max_dissatisfaction = 10
rankings = {}
for person in people:
    for fruit in fruits:
        if fruit in top_5_rankings[person]:
            rankings[(person, fruit)] = top_5_rankings[person].index(fruit) + 1
        elif allergies[person].get(fruit, False):
            rankings[(person, fruit)] = float('inf')  # Allergic fruits are not assignable
        else:
            rankings[(person, fruit)] = max_dissatisfaction

# Initialize the problem
problem = LpProblem("FruitAssignment", LpMinimize)

# Decision variables: x[p, f] = 1 if person p gets fruit f, 0 otherwise
x = LpVariable.dicts("assign", [(p, f) for p in people for f in fruits], cat="Binary")

# Objective function: Minimize total dissatisfaction
problem += lpSum(rankings[(p, f)] * x[(p, f)] for p in people for f in fruits if rankings[(p, f)] != float('inf')), "TotalDissatisfaction"

# Constraints
# Each person gets exactly one fruit
for p in people:
    problem += lpSum(x[(p, f)] for f in fruits if rankings[(p, f)] != float('inf')) == 1, f"OneFruitPerPerson_{p}"

# Each fruit is assigned according to its quantity
for f in fruits:
    problem += lpSum(x[(p, f)] for p in people if rankings[(p, f)] != float('inf')) == fruit_quantities[f], f"FruitQuantity_{f}"

# Solve the problem
problem.solve()

# Output the results
print("Status:", problem.status)

# Check for unassignable people
unassignable = []
assignments = {}
for p in people:
    assigned = False
    for f in fruits:
        if x[(p, f)].value() == 1:
            rank = rankings[(p, f)]
            if rank <= 5:
                rank_status = f"Rank {rank}"
            else:
                rank_status = "Available"
            assignments[p] = (f, rank_status)
            assigned = True
    if not assigned:
        unassignable.append(p)

print("\nAssignments:")
for p, (f, rank_status) in assignments.items():
    print(f"{p} is assigned {f} ({rank_status})")

if unassignable:
    print("\nUnassignable people due to allergies:", unassignable)
else:
    print("\nAll people successfully assigned fruits.")

# Print the total dissatisfaction
print("\nTotal Dissatisfaction:", problem.objective.value())
