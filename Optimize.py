from pulp import LpProblem, LpVariable, LpMinimize, lpSum
from collections import Counter
import random

# Example Data
people = [
    'Alice', 'Bob', 'Charlie', 'Dana', 'Eve', 'Frank', 'Grace', 'Hannah', 'Ian', 'Jack',
    'Karen', 'Leo', 'Mona', 'Nina', 'Oscar', 'Paul', 'Quinn', 'Rachel', 'Steve', 'Tina'
]
fruits = ['Apple', 'Banana', 'Cherry', 'Date', 'Elderberry', 'Fig', 'Grape']

# Generate Random Top 5 Rankings for Each Person
random.seed(42)
top_5_rankings = {}
for person in people:
    top_5_rankings[person] = random.sample(fruits, 5)

# Generate Random Allergies for Each Person
allergies = {}
for person in people:
    allergies[person] = {fruit: random.choice([True, False]) for fruit in fruits}

# Add "unassigned" dummy fruit
fruits.append("unassigned")
for person in people:
    allergies[person]["unassigned"] = False  # Cannot be allergic to "unassigned"

# Dissatisfaction Scores
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

# Adjust Fruit Quantities
total_fruit_supply = len(people)  # Total supply matches the number of users
popularity_weights = {fruit: random.randint(1, 10) for fruit in fruits if fruit != "unassigned"}
fruit_quantities = Counter(
    random.choices(
        list(popularity_weights.keys()),
        weights=popularity_weights.values(),
        k=total_fruit_supply
    )
)

# Initialize the Problem
problem = LpProblem("FruitAssignment", LpMinimize)

# Decision Variables
x = LpVariable.dicts("assign", [(p, f) for p in people for f in fruits], cat="Binary")
leftover = LpVariable.dicts("leftover", fruits, lowBound=0, cat="Integer")

# Objective Function with Penalties
alpha = 20  # Stronger penalty for leftover fruits
beta = 100  # Stronger penalty for unassigned people

problem += (
    lpSum(
        rankings[(p, f)] * x[(p, f)]
        for p in people for f in fruits
        if rankings[(p, f)] != float('inf')
    ) +
    beta * lpSum(x[(p, "unassigned")] for p in people) +
    alpha * lpSum(leftover[f] for f in fruits if f != "unassigned")
), "TotalDissatisfactionWithPenalties"

# Constraints
# Each person gets exactly one fruit
for p in people:
    problem += (
        lpSum(x[(p, f)] for f in fruits if rankings[(p, f)] != float('inf')) == 1,
        f"OneFruitPerPerson_{p}"
    )

# Each fruit is assigned according to its quantity
for f in fruits:
    if f != "unassigned":  # Exclude "unassigned" from leftover constraints
        problem += (
            lpSum(x[(p, f)] for p in people if rankings[(p, f)] != float('inf')) + leftover[f] == fruit_quantities[f],
            f"FruitQuantity_{f}"
        )

# Solve the Problem
problem.solve()

# Output the Results
print("Status:", problem.status)

assignments = {}
unassigned = []
for p in people:
    for f in fruits:
        if x[(p, f)].value() == 1:
            if f == "unassigned":
                unassigned.append(p)
                assignments[p] = f
            else:
                rank = rankings[(p, f)]
                rank_status = f"Rank {rank}" if rank <= 5 else "Available"
                assignments[p] = (f, rank_status)

print("\nAssignments:")
for p, value in assignments.items():
    if value == "unassigned":
        print(f"{p} is unassigned")
    else:
        fruit, rank_status = value
        print(f"{p} is assigned {fruit} ({rank_status})")

print("\nLeftover Fruits:")
for f in fruits:
    if f != "unassigned":
        print(f"{f}: {int(leftover[f].value())} left over")

print("\nTotal Dissatisfaction:", problem.objective.value())
