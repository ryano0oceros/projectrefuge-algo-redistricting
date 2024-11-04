import pulp

# Full data for all 21 counties in New Jersey
county_data = {
    'County': [
        'Atlantic', 'Bergen', 'Burlington', 'Camden', 'Cape May', 'Cumberland', 'Essex', 
        'Gloucester', 'Hudson', 'Hunterdon', 'Mercer', 'Middlesex', 'Monmouth', 'Morris', 
        'Ocean', 'Passaic', 'Salem', 'Somerset', 'Sussex', 'Union', 'Warren'
    ],
    'Population': [
        275213, 975736, 469167, 527196, 94610, 152326, 851117, 308423, 705472, 130183, 
        381671, 863623, 642799, 514423, 659197, 513395, 65338, 348842, 146132, 572726, 111252
    ],
    'Adjacency': [
        ['Burlington', 'Camden', 'Cape May', 'Cumberland', 'Gloucester', 'Ocean'],  # Atlantic
        ['Essex', 'Hudson', 'Passaic', 'Rockland, NY'],  # Bergen
        ['Atlantic', 'Camden', 'Mercer', 'Monmouth', 'Ocean'],  # Burlington
        ['Atlantic', 'Burlington', 'Gloucester'],  # Camden
        ['Atlantic', 'Cumberland'],  # Cape May
        ['Atlantic', 'Cape May', 'Gloucester', 'Salem'],  # Cumberland
        ['Bergen', 'Hudson', 'Morris', 'Passaic', 'Union'],  # Essex
        ['Atlantic', 'Camden', 'Cumberland', 'Salem'],  # Gloucester
        ['Bergen', 'Essex', 'Union'],  # Hudson
        ['Mercer', 'Morris', 'Somerset', 'Warren'],  # Hunterdon
        ['Burlington', 'Hunterdon', 'Middlesex', 'Monmouth', 'Somerset'],  # Mercer
        ['Mercer', 'Monmouth', 'Somerset', 'Union'],  # Middlesex
        ['Burlington', 'Mercer', 'Middlesex', 'Ocean'],  # Monmouth
        ['Essex', 'Hunterdon', 'Passaic', 'Somerset', 'Sussex', 'Union', 'Warren'],  # Morris
        ['Atlantic', 'Burlington', 'Monmouth'],  # Ocean
        ['Bergen', 'Essex', 'Morris', 'Sussex'],  # Passaic
        ['Cumberland', 'Gloucester'],  # Salem
        ['Hunterdon', 'Mercer', 'Middlesex', 'Morris', 'Union'],  # Somerset
        ['Morris', 'Passaic', 'Warren'],  # Sussex
        ['Essex', 'Hudson', 'Middlesex', 'Morris', 'Somerset'],  # Union
        ['Hunterdon', 'Morris', 'Sussex']  # Warren
    ]
}

# Number of districts
num_districts = 6

# Create a linear programming problem
model = pulp.LpProblem("Redistricting", pulp.LpMaximize)

# Decision variables: X[i][j] is 1 if county i is assigned to district j, 0 otherwise
counties = county_data['County']
districts = range(num_districts)
x = pulp.LpVariable.dicts("x", [(i, j) for i in counties for j in districts], cat='Binary')

# Objective function: maximize compactness or other criteria (for example purposes, summing variables)
model += pulp.lpSum(x[i, j] for i in counties for j in districts)

# Constraints:
# 1. Each county should be assigned to exactly one district
for i in counties:
    model += pulp.lpSum(x[i, j] for j in districts) == 1, f"SingleAssignment_{i}"

# 2. Population balance constraint (adjust balance criteria as needed)
population_data = {county_data['County'][i]: county_data['Population'][i] for i in range(len(county_data['County']))}
total_population = sum(population_data.values())
population_per_district = total_population / num_districts

for j in districts:
    model += (
        pulp.lpSum(x[i, j] * population_data[i] for i in counties) <= population_per_district * 1.05  # Allow 5% deviation
    )
    model += (
        pulp.lpSum(x[i, j] * population_data[i] for i in counties) >= population_per_district * 0.95  # Allow 5% deviation
    )

# 3. Adjacency constraints for contiguity
# Ensure that if a county is assigned to a district, at least one of its adjacent counties must also be in the same district
adjacency_data = {county_data['County'][i]: county_data['Adjacency'][i] for i in range(len(county_data['County']))}

for i in counties:
    for j in districts:
        # If county i is in district j, then at least one adjacent county should also be in district j
        model += x[i, j] <= pulp.lpSum(x[adj, j] for adj in adjacency_data[i] if adj in counties), f"Adjacency_{i}_{j}"

# Solve the model
model.solve()

# Print results
for i in counties:
    for j in districts:
        if pulp.value(x[i, j]) == 1:
            print(f"{i} is assigned to district {j}")

# Print the status of the solution
print("Status:", pulp.LpStatus[model.status])
