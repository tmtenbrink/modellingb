# -*- coding: utf-8 -*-
"""
@author: margo, tip
"""
import numpy as np
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
R = df_par.loc['Number operating rooms'].iat[0]

# Number of days
T = df_par.loc['Number days'].iat[0]

# Capacity per day per operating room
c = df_par.loc['Capacity'].iat[0]

# Get the amount of surgeries by counting the length of the index of the sheet (the 'Surgery' column)
surgery_amount = len(df_surg.index)
# Dictionary of surgery times
surgeries = {}
for i in range(surgery_amount):
    # The surgeries are identified by numbers, so get the row by index (iloc)
    # This gets a whole row, then get the value at the 'Duration' column (at)
    surgeries[i] = int(df_surg.iloc[i].at['Duration'])

sorted_surgeries = sorted(surgeries.items(), key=lambda x: -x[1])

# create array to count minutes
rooms_time = np.zeros((T, R), dtype=int)

# create array with empty lists to check which operation which day and room
# first list = first day, first room, second list = first day, second room ect
rooms_op = np.empty((T, R), dtype=list)
for i in range(T):
    for j in range(R):
        rooms_op[i][j] = []

# loop over each operation (sorted high to low)
for surgery in sorted_surgeries:
    # find the operation room with fewest time spend
    choose = np.unravel_index(np.argmin(rooms_time, axis=None), rooms_time.shape)
    # add time of the 'current' operation to this room
    rooms_time[choose] += surgery[1]
    # append operation to the this room
    rooms_op[choose].append(surgery[0])

# find maximum time in rooms
max_room_times = np.amax(rooms_time, 1)
max_overdue_rooms = np.argmax(rooms_time, 1)

total_max_overdue = 0
# loop over all the maximum overdue times and add the overdue to the total
for max_room_time in max_room_times:
    total_max_overdue += max_room_time - c

for day in range(T):
    print("\nDAY " + str(day))
    for room in range(R):
        room_time = rooms_time[day, room]
        room_overdue = room_time - c
        if room_overdue > 0:
            overdue_string = ", " + str(room_overdue) + " overdue"
        else:
            overdue_string = ", not overdue"
        print("Room " + str(room) + ": " + str(room_time) + overdue_string)
        room_surgeries = rooms_op[day, room]
        for surgery in room_surgeries:
            surgery_time = surgeries[surgery]
            print("Surgery " + str(surgery) + " (" + str(surgery_time) + " minutes)", end=', ')

print("\n")

for day in range(T):
    max_overdue_room = max_overdue_rooms[day]
    max_room_time = rooms_time[day, max_overdue_room]
    max_room_overdue = max_room_time - c
    print("On day " + str(day) + ", Room " + str(max_overdue_room) + " is most overdue, at " + str(max_room_overdue) +
          " minutes")

print("\nSummed max overdues: " + str(total_max_overdue))
