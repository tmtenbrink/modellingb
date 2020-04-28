import pandas as pd
import numpy as np

filename = 'Data assignment operating room 2 Large.xlsx'

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
surgeries = np.zeros((surgery_amount, 2)).astype('int32')
for i in range(surgery_amount):
    # The surgeries are identified by numbers, so get the row by index (iloc)
    # This gets a whole row, then get the value at the 'Duration' column (at)
    surgeries[i] = [i, df_surg.iloc[i].at['Duration']]

# we negate the array and slice it to get the second column only
# we use argsort to get the indices in ascending order
# since it is negated these corresponds to indices in descending order
# we then get these indices to make a new array in descending order
surgeries = surgeries[(-surgeries[:, 1]).argsort()]

schedule = list()
slot_sums = list()
# R*T is the amount of different slots (days times operation rooms)
slot_amount = R * T

for i in range(slot_amount):
    schedule.append([])
    slot_sums.append(0)


def cycle_sequence_assignment():
    # k is next operation room to add surgery to
    k = 0
    ascending = True
    for i in range(surgery_amount):
        # surgery id
        surgery = surgeries[i, 0]
        schedule[k].append(surgery)

        if ascending:
            k += 1
            if k == slot_amount:
                ascending = False
                k -= 1
        else:
            k -= 1
            if k == -1:
                ascending = True
                k += 1

    for i, slot in enumerate(schedule):

        slot_sum = 0
        for surgery in slot:
            slot_sum += df_surg.iloc[surgery].at['Duration']
        slot_sums[i] = slot_sum

    return schedule, slot_sums


def min_slot_assignment():
    for i in range(surgery_amount):
        # make it into list to make it
        surgery = surgeries[i, :]
        surgery_id = surgery[0]

        # k is next operation room to add slot to, it is the one with the least current time
        small_slot_i = int(np.argmin(slot_sums))
        schedule[small_slot_i].append(surgery)

        slot_sums[small_slot_i] += df_surg.iloc[surgery_id].at['Duration']

    for i, slot in enumerate(schedule):
        schedule[i] = np.array(slot)

    skip_i = []

    no = 0
    while not all(slot > 480 for slot in slot_sums):
        print("round:")
        min_slot_i = int(np.argmin(slot_sums))
        print("min slot: " + str(min_slot_i))

        if not min_slot_i in skip_i:
            skip_i.append(min_slot_i)

        max_sum = 0
        max_slot_i = -1
        for i, slot_sum in enumerate(slot_sums):
            if not i in skip_i:
                if slot_sum > max_sum:
                    max_sum = slot_sum
                    max_slot_i = i
        if max_slot_i == -1:
            print("no max found")
            break
        print("max slot: " + str(max_slot_i))
        over_slot = slot_sums[max_slot_i] - c
        surgs_max_slot = schedule[max_slot_i]
        small_surgery_i = int(np.argmin(surgs_max_slot[:, 1]))
        small_surgery_id = surgs_max_slot[small_surgery_i, 0]
        small_surgery_duration = df_surg.iloc[small_surgery_id].at['Duration']
        if small_surgery_duration > over_slot:
            skip_i.append(max_slot_i)
            print("no small surgery, skipping: " + str(max_slot_i))
        else:
            skip_i = []
            surgs_max_slot_list = surgs_max_slot.tolist()
            surgs_max_slot_list.pop(small_surgery_i)
            surgs_max_slot = np.array(surgs_max_slot_list)
            schedule[max_slot_i] = surgs_max_slot
            surgs_min_slot_list = schedule[min_slot_i].tolist()
            surgs_min_slot_list.append([small_surgery_id, small_surgery_duration])
            schedule[min_slot_i] = np.array(surgs_min_slot_list)

            for i, slot in enumerate(schedule):
                slot_sum = 0
                for surgery in slot:
                    slot_sum += surgery[1]
                slot_sums[i] = slot_sum

        no += 1
        #if no > 1:
        #    print(slot_sums)

    return schedule, slot_sums


schedule, slot_sums = min_slot_assignment()

print(slot_sums)
print(schedule)
