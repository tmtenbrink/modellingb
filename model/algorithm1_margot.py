# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 19:12:59 2020

@author: margo
"""
import numpy as np

#SMALL PROBLEM 
information = {
        'number OR': 3,
        'days': 1,
        'capacity': 480,
        }

operation = {
        '1': 46,
        '2': 60, 
        '3': 40,
        '4': 291,
        '5': 21, 
        '6': 21,
        '7': 83,
        '8': 254,
        '9': 21,
        '10': 171,
        '11': 230,
        '12': 40,
        '13': 21,
        '14': 40,
        '15': 51,
        '16': 152
        }

#sorted list with tuples low to high
o_sort = sorted(operation.items(), key = lambda x:x[1])

#sorted list with tuples high to low
op_sort = o_sort[::-1]

#create array to count minutes
rooms_time = np.zeros((information['days'], information['number OR']))

#create array with empty lists to check which operation which day and room
#first list = first day, first room, second list = first day, second room ect
rooms_op = np.empty((information['days'], information['number OR']), dtype = object)
for a in range(information['days']):
    for b in range(information['number OR']):
        rooms_op[a][b] = []

#loop over each operation (sorted high to low)
for x in op_sort:
    #find the operation room with fewest time spend
    choose = np.unravel_index(np.argmin(rooms_time, axis = None), rooms_time.shape)
    #add time of the 'current' operation to this room
    rooms_time[choose] += x[1]
    #append operation to the this room
    rooms_op[choose].append(x[0])

print(rooms_time)
print(rooms_op)

#find maximum time in rooms
overdue = np.amax(rooms_time)-information['capacity']
print(overdue)
print()



#LARGE PROBLEM
information = {
        'number OR': 3,
        'days': 2,
        'capacity': 480,
        }

operation = {
        '1': 109,
        '2': 51, 
        '3': 44,
        '4': 51,
        '5': 113, 
        '6': 60,
        '7': 171,
        '8': 125,
        '9': 51,
        '10': 127,
        '11': 65,
        '12': 60,
        '13': 60,
        '14': 73,
        '15': 121,
        '16': 51,
        '17': 61,
        '18': 262,
        '19': 40,
        '20': 102,
        '21': 82,
        '22': 45,
        '23': 50,
        '24': 74,
        '25': 40,
        '26': 60, 
        '27': 324,
        '28': 324,
        '29': 46,
        '30': 125,
        }

#sorted list with tuples low to high
o_sort = sorted(operation.items(), key = lambda x:x[1])

#sorted list with tuples high to low
op_sort = o_sort[::-1]

#create array to count minutes
rooms_time = np.zeros((information['days'], information['number OR']))

#create array with empty lists to check which operation which day and room
#first list = first day, first room, second list = first day, second room ect
rooms_op = np.empty((information['days'], information['number OR']), dtype = object)
for a in range(information['days']):
    for b in range(information['number OR']):
        rooms_op[a][b] = []

#loop over each operation (sorted high to low)
for x in op_sort:
    #find the operation room with fewest time spend
    choose = np.unravel_index(np.argmin(rooms_time, axis = None), rooms_time.shape)
    #add time of the 'current' operation to this room
    rooms_time[choose] += x[1]
    #append operation to the this room
    rooms_op[choose].append(x[0])

print(rooms_time)
print(rooms_op)

#find maximum time in rooms
overdue = np.amax(rooms_time)-information['capacity']
print(overdue)