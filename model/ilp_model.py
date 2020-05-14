from pulp import *
import pandas as pd

datasets = {
    'Small': "Data assignment operating room 2 Small.xlsx",
    'Large': "Data assignment operating room 2 Large.xlsx"
}

print("Datasets to optimize: ")

for data_key in datasets.keys():
    print("Key: <" + str(data_key) + ">, Dataset name: '" + datasets[data_key] + "'")

ask_dataset = True

while ask_dataset:
    dataset_choice = input("\nType the exact key (what is in between '<>') of the desired dataset to begin optimizing.")
    try:
        filename = datasets[dataset_choice]
        print("You have chosen the dataset: '" + filename + "'")
        break
    except KeyError:
        print("That is not a valid key Please try again.")

if not ask_dataset:
    filename = "Data assignment operating room 2 Large.xlsx"

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
surgeries = {} #mu
for i in range(surgery_amount):
    # The surgeries are identified by numbers, so get the row by index (iloc)
    # This gets a whole row, then get the value at the 'Duration' column (at)
    surgeries[i+1] = int(df_surg.iloc[i].at['Duration'])

I = range(1, surgery_amount+1)
T = range(1, days_amount+1)
R = range(1, rooms_amount+1)

#make variables
schedules = LpVariable.dicts("Schedule", (I, T, R), cat='Binary') #constraint 4
max_overtimes = LpVariable.dicts("MaxOvertime", T, cat='Continuous') #m_t
room_overtimes = LpVariable.dicts("RoomOvertime", (T, R), lowBound = 0, cat='Continuous') #m_r

#initialize problem
prob = LpProblem("OperatingRooms", LpMinimize)

#objective function
prob += lpSum([max_overtimes[t] for t in T])

#constraints
#constraint 1, 4
for i in I:
    prob += lpSum([schedules[i][t][r] for t in T for r in R]) == 1

#constraint 2
for t in T:
    for r in R:
            prob += room_overtimes[t][r] - lpSum([surgeries[i]*schedules[i][t][r] for i in I]) + c == 0
    
#constraint 3    
for t in T:
    for r in R:
        prob += max_overtimes[t] >= room_overtimes[t][r]

prob.solve()
print('Status', LpStatus[prob.status])

for v in prob.variables():
    print(v.name, '=', v.varValue)
    
print('Overtime sum =', value(prob.objective))



    
