from pulp import *

chips = ['PLAIN', 'MEXICAN']

profits = {'PLAIN': 2, 'MEXICAN': 1.5}

slicing_time = {'PLAIN': 2, 'MEXICAN': 4}
frying_time = {'PLAIN': 4, 'MEXICAN': 5}
packing_time = {'PLAIN': 4, 'MEXICAN': 2}

prob = LpProblem("PatatoChips", LpMaximize)

chip_vars = LpVariable.dicts('Chip', chips, 0, cat='Integer')

prob += lpSum([profits[i] * chip_vars[i] for i in chips]), "Profit"

prob += lpSum([slicing_time[i] * chip_vars[i] for i in chips]) <= 345, "Slice Time Available"
prob += lpSum([frying_time[i] * chip_vars[i] for i in chips]) <= 480, "Frying Time Available"
prob += lpSum([packing_time[i] * chip_vars[i] for i in chips]) <= 330, "Packing Time Available"

prob.writeLP("test")
prob.solve()

print("Status:", LpStatus[prob.status])

for v in prob.variables():
    print(v.name, "=", v.varValue)

print("Profit = ", value(prob.objective))