from pulp import *
import pandas as pd
from model_result_print import result_print

# List of importable datasets, each with a reference key so one can be chosen
datasets = {
    'Small': "Data assignment operating room 2 Small.xlsx",
    'Large': "Data assignment operating room 2 Large.xlsx",
    'VeryLarge': "Data assignment operating room 2 VeryLarge.xlsx"
}

print("Datasets to optimize: ")

# Prints out the importable datasets and indicates their reference keys by looping through the keys
for data_key in datasets.keys():
    print("Key: <" + str(data_key) + ">, Dataset name: '" + datasets[data_key] + "'")

# Set to false to skip the dataset request phase and set to defaults below
ask_dataset = True
# Default key and file name
filename = "Data assignment operating room 2 Large.xlsx"
data_key_choice = 'Large'

# A while loop so another key can be entered if a mistake is made
while ask_dataset:
    # The choice for the reference key listed above
    data_key_choice = input(
        "\nType the exact key (what is in between '<>') of the desired dataset to begin optimizing.\n")
    # It looks for the inputted key in the datasets dictionary. If it exists, it is a correct key
    # If the inputted key is incorrect, a KeyError will be thrown as none exists in the dictionary
    # In the latter case it will restart the while loop to give another chance
    try:
        filename = datasets[data_key_choice]
        print("You have chosen the dataset: '" + filename + "'")
        ask_dataset = False
    except KeyError:
        print("That is not a valid key Please try again.")

# Get pandas dataframe of the first sheet called 'General Information'
# Index the dataframe by the names in the 0th column
# Indicate columns have no header name, so it doesn't see the 0th row as header names
df_par = pd.read_excel(filename, sheet_name='General Information', index_col=0, header=None)
# Get pandas dataframe of the first sheet called 'General Information'
# Index the dataframe by the names in the column called 'Surgery'
df_surg = pd.read_excel(filename, sheet_name='Duration surgeries', index_col='Surgery')

# Number of operations rooms
rooms_amount = df_par.loc['Number operating rooms'].iat[0]

# Number of days
days_amount = df_par.loc['Number days'].iat[0]

# Capacity per day per operating room
c = df_par.loc['Capacity'].iat[0]

# Get the amount of surgeries by counting the length of the index of the sheet (the 'Surgery' column)
surgery_amount = len(df_surg.index)
# Dictionary of surgery times
surgeries_duration = {}  # mu
for i in range(surgery_amount):
    # The surgeries are identified by numbers, so get the row by index (iloc)
    # This gets a whole row, then get the value at the 'Duration' column (at)
    surgeries_duration[i + 1] = int(df_surg.iloc[i].at['Duration'])

# Get the shape
# I is the set of surgery numbers
set_I = range(1, surgery_amount + 1)
# T is the set of days
set_T = range(1, days_amount + 1)
# R is the set of rooms
set_R = range(1, rooms_amount + 1)

# Make 3 dictionaries for the problem variables
# schedule_itr is the dictionary containing all the model x_ir variables, for r on a particular day t
# This gives a 3-dimensional dictionary, where every individual value is either 1 or 0, satisfying C5
# This indicates whether a surgery i is indeed scheduled in room r on day t (1 is scheduled, 0 not scheduled)
schedule_itr = LpVariable.dicts("Schedule", (set_I, set_T, set_R), cat='Binary')
# The overtimes are measured in minutes (integer)
# max_overtimes is a dictionary containing all the model m_t variables, so the maximum overtime on a day t
max_overtimes = LpVariable.dicts("MaxOvertime", set_T, cat='Integer')
# room_overtimes is a dictionary containing all the m_r variables, so the overtime of a room r on a day t
# As the overtime is zero if it is at less than capacity, we want a lower bound of 0, satisfying C3
room_overtimes = LpVariable.dicts("RoomOvertime", (set_T, set_R), lowBound=0, cat='Integer')

# Initialize the problem
# We seek to minimize the overtime
prob = LpProblem("OperatingRooms", LpMinimize)

# Objective function is the sum of all maximum overtimes of the days, which we seek to minimize
prob += lpSum([max_overtimes[t] for t in set_T])

# Each surgery has to be scheduled exactly once, satisfying C1
# So for a surgery i, all variables over all rooms r on all days t, must sum to exactly 1
# This has to be the case for all surgeries, so we add this constraint for all surgeries
for i in set_I:
    prob += lpSum([schedule_itr[i][t][r] for t in set_T for r in set_R]) == 1

# The overtime of a room r on a day t must be equal to the sum of the surgery times in that room minus the capacity
# As a result, the difference must be equal to zero, satisfying C2
# We only want the surgeries actually scheduled, so we multiply the binary schedule variable with the surgery duration
# We want this for every room overtime variable m_r, so we loop through all r on all days t
for t in set_T:
    for r in set_R:
        prob += room_overtimes[t][r] - lpSum([surgeries_duration[i] * schedule_itr[i][t][r] for i in set_I]) + c == 0

# To be the maximum room overtime, m_t must be larger than all other m_r for the r on that day t, satisfying C4
# As such, for all m_r, the corresponding m_t must be larger, requiring a constraint for all these
for t in set_T:
    for r in set_R:
        prob += max_overtimes[t] >= room_overtimes[t][r]

# If the Gurobi solver is available, use it
if GUROBI_CMD().available():
    prob.solve(GUROBI_CMD())
# Otherwise, solve it using the default solver
else:
    prob.solve()

# Print whether the final status, indicating if it was indeed optimized
print('Status', LpStatus[prob.status])

# If it was indeed optimally solved, write the output to a text file for later viewing
if LpStatus[prob.status] == 'Optimal':
    # Define filename using the dataset key used in the choice at the start of this program
    output_filename = "output_" + data_key_choice + ".txt"
    # Open file, write mode so it is created if it does not exist
    f = open(output_filename, 'w')
    # Create list of lines containing all variable names and their values
    lines = [str(v.name) + '=' + str(v.varValue) + "\n" for v in prob.variables()]
    # Append objective function result
    lines.append('Overtime sum =' + str(value(prob.objective)))
    # Write lines to file
    f.writelines(lines)
    f.close()

    # Print result using function in model_result_print.py
    result_print(output_filename)
