import numpy as np

f = open("output_large.txt", "r")

lines = f.readlines()

max_overtimes = {}
room_overtimes = {}
schedule = {}

for line in lines:
    if not line.strip() == "":
        equal_split = line.split('=')
        underscore_split = equal_split[0].split('_')
        value = int(float(equal_split[1].strip()))

        if underscore_split[0] == "MaxOvertime":
            max_overtimes[int(underscore_split[1])] = value
        elif underscore_split[0] == "RoomOvertime":
            day = int(underscore_split[1])
            room = int(underscore_split[2])
            try:
                v = room_overtimes[day]
            except KeyError:
                room_overtimes[day] = {}
                schedule[day] = {}
            room_overtimes[day][room] = value
            try:
                v = schedule[day][room]
            except KeyError:
                schedule[day][room] = []
        elif underscore_split[0] == "Schedule":
            if value == 1:
                surgery = int(underscore_split[1])
                day = int(underscore_split[2])
                room = int(underscore_split[3])
                schedule[day][room].append(surgery)

for day in room_overtimes.keys():
    print("\nDAY " + str(day))
    for room in room_overtimes[day].keys():
        room_overtime = room_overtimes[day][room]
        if room_overtime > 0:
            overdue_string = str(room_overtime) + " minutes overtime"
        else:
            overdue_string = "not overdue"
        print("Room " + str(room) + ": " + overdue_string)
        room_surgeries = schedule[day][room]
        for i, surgery in enumerate(room_surgeries):
            # surgery_time = surgeries[surgery]
            if i != 0:
                sep = ", "
            else:
                sep = ""
            print(sep + "Surgery " + str(surgery), end='') # + " (" + str(surgery_time) + " minutes)", end='')
        print()

print("\n")

for day in room_overtimes.keys():
    max_overtime = max_overtimes[day]
    max_overtime_rooms = []
    for room in room_overtimes[day].keys():
        if room_overtimes[day][room] == max_overtime:
            max_overtime_rooms.append(room)
    if len(max_overtime_rooms) > 1:
        room_overtime_string = "Rooms "
        for overtime_room in max_overtime_rooms:
            room_overtime_string += str(overtime_room) + " "
        room_overtime_string += "are "
    else:
        room_overtime_string = "Room " + str(max_overtime_rooms[0]) + " is "
    print("On day " + str(day) + ", " + room_overtime_string + "most overdue, at " + str(max_overtime) +
          " minutes")