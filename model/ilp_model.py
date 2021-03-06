from pulp import *
import pandas as pd
from model_result_print import result_print
import time

# List of importable datasets, each with a reference key so one can be chosen
datasets = {
    'Small': ("Data assignment operating room 2 Small.xlsx", "Basic"),
    'Large': ("Data assignment operating room 2 Large.xlsx", "Departments"),
    'VeryLarge': ("Data assignment operating room 2 VeryLarge.xlsx", "Basic")
}

print("Datasets to optimize: ")

# Prints out the importable datasets and indicates their reference keys by looping through the keys
for data_key in datasets.keys():
    print("Key: <" + str(data_key) + ">, Dataset name: '" + datasets[data_key][0] + "' (" + datasets[data_key][1] + ")")

# Set to false to skip the dataset request phase and set to defaults below
ask_dataset = True
# Default key and file name
filename = "Data assignment operating room 2 Large.xlsx"
data_key_choice = 'Large'

ask_departments = False
department_model = False

# A while loop so another key can be entered if a mistake is made
while ask_dataset:
    # The choice for the reference key listed above
    data_key_choice = input(
        "\nType the exact key (what is in between '<>') of the desired dataset to begin optimizing:\n")
    # It looks for the inputted key in the datasets dictionary. If it exists, it is a correct key
    # If the inputted key is incorrect, a KeyError will be thrown as none exists in the dictionary
    # In the latter case it will restart the while loop to give another chance
    try:
        filename = datasets[data_key_choice][0]
        print("You have chosen the dataset: '" + filename + "'")
        ask_dataset = False
        if datasets[data_key_choice][1] == "Departments":
            ask_departments = True
        while ask_departments:
            department_choice = input(
                "\nThis dataset has department data. Run the expanded model? [Y/n]:\n")
            if department_choice == 'Y':
                department_model = True
                ask_departments = False
            elif department_choice == 'n':
                ask_departments = False
            else:
                print("That is not a valid input. Type 'Y' for Yes and 'n' for No (without the '')")
    except KeyError:
        print("That is not a valid key Please try again.")

if department_model:
    print("The expanded department model will be run.")
else:
    print("The basic model will be run.")

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

if department_model:
    o = df_par.loc['Overtime per department'].iat[0]
else:
    o = None

# Get the amount of surgeries by counting the length of the index of the sheet (the 'Surgery' column)
surgery_amount = len(df_surg.index)
# List of different departments
set_D = []
# Binary variables indicating whether a surgery is in a department, y_id
department_surgeries = {}
# Dictionary of surgery times
surgeries_duration = {}  # mu

# I is the set of surgery numbers
# The surgeries are identified by numbers, which we want to get
# We had set the Surgery column to be the index column, so we can get these values by getting the df index values
set_I = list(df_surg.index.values)

for i in set_I:
    surgeries_duration[i] = int(df_surg.loc[i].at['Duration'])
    if department_model:
        department = df_surg.loc[i].at['Department']
        if department not in set_D:
            set_D.append(department)
            department_surgeries[department] = {surg_key: 0 for surg_key in set_I}
        department_surgeries[department][i] = 1

# Get the shape
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
# room_departments is a dictionary containing all the z_rd variables, so whether or not a room r has department d
# z_rd is binary, so setting the category to Binary satisfies C6
if department_model:
    room_departments = LpVariable.dicts("RoomDepartments", (set_T, set_R, set_D), cat='Binary')
else:
    room_departments = None

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
# In the case of departments, the amount of departments per room times the constant o also creates additional duration
# As a result, the difference must be equal to zero, satisfying C2
# We only want the surgeries actually scheduled, so we multiply the binary schedule variable with the surgery duration
# We want this for every room overtime variable m_r, so we loop through all r on all days t
for t in set_T:
    for r in set_R:
        if department_model:
            prob += room_overtimes[t][r] >= lpSum([surgeries_duration[i] * schedule_itr[i][t][r] for i in set_I]) + \
                    lpSum([room_departments[t][r][d]*o for d in set_D]) - c
        else:
            prob += room_overtimes[t][r] >= lpSum([surgeries_duration[i] * schedule_itr[i][t][r] for i in set_I]) - c
# To be the maximum room overtime, m_t must be larger than all other m_r for the r on that day t, satisfying C4
# As such, for all m_r, the corresponding m_t must be larger, requiring a constraint for all these
for t in set_T:
    for r in set_R:
        prob += max_overtimes[t] >= room_overtimes[t][r]

if department_model:
    for t in set_T:
        for r in set_R:
            for d in set_D:
                prob += room_departments[t][r][d] >= (1/surgery_amount) * \
                        lpSum([schedule_itr[i][t][r] * department_surgeries[d][i] for i in set_I])


# If the Gurobi solver is available, use it
if GUROBI_CMD().available():
    print("Solving with Gurobi...\n\n")
    # Sleep 1 second so the print statements above can be read
    time.sleep(1)
    prob.solve(GUROBI_CMD())

# Otherwise, solve it using the default solver
else:
    print("Solving with CBC...\n\n")
    prob.solve()

# Print whether the final status, indicating if it was indeed optimized
print('Status', LpStatus[prob.status])

# If it was indeed optimally solved, write the output to a text file for later viewing
if LpStatus[prob.status] == 'Optimal':
    # Define filename using the dataset key used in the choice at the start of this program
    output_filename = data_key_choice + ".txt"
    if department_model:
        output_filename = "output_department" + output_filename
    else:
        output_filename = "output_" + output_filename
    # Open file, write mode so it is created if it does not exist
    f = open(output_filename, 'w')
    # Create list of lines containing all variable names and their values
    lines = [str(v.name) + '=' + str(v.varValue) + "\n" for v in prob.variables()]
    # Append objective function result
    lines.append('Overtime sum=' + str(value(prob.objective)))
    # Write lines to file
    f.writelines(lines)
    f.close()

    # Print result using function in model_result_print.py
    result_print(output_filename)