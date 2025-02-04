from pulp import LpProblem, LpVariable, LpMinimize, lpSum

# Example Data
people = [
    'Alice', 'Bob', 'Charlie', 'Dana', 'Eve', 'Frank', 'Grace', 'Hannah', 'Ian', 'Jack', 'Karen', 'Leo', 'Mona', 'Nina', 'Oscar', 'Paul', 'Quinn', 'Rachel', 'Steve', 'Tina'
]
fruits = ['Apple', 'Banana', 'Cherry', 'Date', 'Elderberry', 'Fig', 'Grape']

# Quantities of each fruit
fruit_quantities = {
    'Apple': 1, 'Banana': 3, 'Cherry': 2, 'Date': 3, 'Elderberry': 4, 'Fig': 4, 'Grape': 3
}

# Rankings (1 = most preferred, 5 = least preferred, inf = not ranked)
top_5_rankings = {
    'Alice': ['Apple', 'Banana', 'Cherry', 'Date', 'Fig'],
    'Bob': ['Apple', 'Banana', 'Cherry', 'Grape', 'Fig'],
    'Charlie': ['Apple', 'Cherry', 'Grape', 'Fig', 'Elderberry'],
    'Dana': ['Banana', 'Apple', 'Cherry', 'Fig', 'Date'],
    'Eve': ['Fig', 'Banana', 'Apple', 'Elderberry', 'Grape'],
    'Frank': ['Apple', 'Cherry', 'Fig', 'Grape', 'Banana'],
    'Grace': ['Banana', 'Elderberry', 'Apple', 'Cherry', 'Fig'],
    'Hannah': ['Apple', 'Fig', 'Banana', 'Grape', 'Date'],
    'Ian': ['Grape', 'Apple', 'Banana', 'Elderberry', 'Fig'],
    'Jack': ['Date', 'Apple', 'Grape', 'Banana', 'Cherry'],
    'Karen': ['Elderberry', 'Apple', 'Fig', 'Grape', 'Banana'],
    'Leo': ['Apple', 'Banana', 'Grape', 'Fig', 'Cherry'],
    'Mona': ['Fig', 'Grape', 'Banana', 'Apple', 'Cherry'],
    'Nina': ['Banana', 'Apple', 'Elderberry', 'Cherry', 'Fig'],
    'Oscar': ['Cherry', 'Apple', 'Grape', 'Fig', 'Banana'],
    'Paul': ['Grape', 'Fig', 'Apple', 'Cherry', 'Elderberry'],
    'Quinn': ['Elderberry', 'Cherry', 'Apple', 'Grape', 'Fig'],
    'Rachel': ['Fig', 'Apple', 'Banana', 'Grape', 'Elderberry'],
    'Steve': ['Apple', 'Grape', 'Fig', 'Elderberry', 'Banana'],
    'Tina': ['Banana', 'Apple', 'Cherry', 'Grape', 'Fig']
}

# Allergies (True if allergic, False otherwise)
allergies = {
    'Alice': {'Elderberry': True, 'Grape': False},
    'Bob': {'Date': True, 'Grape': False},
    'Charlie': {'Elderberry': False, 'Banana': True},
    'Dana': {'Cherry': True, 'Elderberry': False},
    'Eve': {'Date': True, 'Cherry': False},
    'Frank': {'Banana': True, 'Date': False},
    'Grace': {'Fig': True, 'Date': False},
    'Hannah': {'Elderberry': False, 'Grape': True},
    'Ian': {'Date': True, 'Fig': False},
    'Jack': {'Elderberry': True, 'Apple': False},
    'Karen': {'Banana': True, 'Cherry': False},
    'Leo': {'Date': True, 'Elderberry': False},
    'Mona': {'Cherry': True, 'Banana': False},
    'Nina': {'Fig': False, 'Apple': True},
    'Oscar': {'Grape': True, 'Date': False},
    'Paul': {'Apple': False, 'Elderberry': True},
    'Quinn': {'Cherry': False, 'Fig': True},
    'Rachel': {'Grape': True, 'Banana': False},
    'Steve': {'Date': True, 'Cherry': False},
    'Tina': {'Fig': True, 'Elderberry': False}
}

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