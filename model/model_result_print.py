# This program serves to create a nice printed overview of the results, based on the variables spitted out by the model
# This allows the results to be viewed without running a full optimization
# The program does not require the information from the dataset, so it can be run independently of the dataset


def result_print(filename):
    # The file is opened as the variable f
    f = open(filename, "r")

    # A list of lines of the text file is created
    lines = f.readlines()

    # It creates dictionaries corresponding to the model variable dictionaries
    max_overtimes = {}
    room_overtimes = {}
    schedule = {}

    # It reads line per line
    for line in lines:
        # If the line is empty (it strips it of whitespace), skip it
        if not line.strip() == "":
            # It creates a list of the line separated by the '='
            equal_split = line.split('=')
            # It splits the part before the '=', separated by underscores
            underscore_split = equal_split[0].split('_')
            # It strips the part after the '=' of whitespace, converts it into a float as it can contain decimals
            # This is then converted to an int as only integer minutes are relevant in this problem
            value = int(float(equal_split[1].strip()))

            # The variable name is always before the underscore, so the 0th index of the underscore split
            if underscore_split[0] == "MaxOvertime":
                # If it is a MaxOvertime variable, it will put the value in the key corresponding to the day
                # This day is, in the output format, the numerical value after the underscore
                max_overtimes[int(underscore_split[1])] = value
            elif underscore_split[0] == "RoomOvertime":
                # If it is a RoomTime variable, the day is the value after the first underscore
                day = int(underscore_split[1])
                # The room is after the second underscore
                room = int(underscore_split[2])

                # Since shape is unknown beforehand, it must gradually create it
                # It checks if there is already a key for the day added
                try:
                    v = room_overtimes[day]
                # If there isn't, it will initialize this by setting an empty dictionary which will consist of the rooms
                # It will also initialize schedule dictionary for that day, also corresponding to the rooms
                except KeyError:
                    room_overtimes[day] = {}
                    schedule[day] = {}

                # The value is the room overtime, so it sets it at the correct place
                room_overtimes[day][room] = value

                # It checks now also if a room has been added to the schedule on a certain day
                try:
                    v = schedule[day][room]
                # If not, it creates an empty list where surgeries can be later added to
                except KeyError:
                    schedule[day][room] = []
            elif underscore_split[0] == "Schedule":
                # If the surgery is indeed scheduled in this room on this day, the value must be equal to 1
                if value == 1:
                    surgery = int(underscore_split[1])
                    day = int(underscore_split[2])
                    room = int(underscore_split[3])
                    # It adds the surgery number to a list corresponding to a room on a day
                    schedule[day][room].append(surgery)

    # Print section
    for day in room_overtimes.keys():
        # For each day it prints an overview. The room_overtimes consists of keys corresponding to days
        print("\nDAY " + str(day))
        # For each room it prints an overview
        for room in room_overtimes[day].keys():
            # The values for room_overtime corresponding to day keys are dictionaries consisting of rooms with overtimes
            room_overtime = room_overtimes[day][room]
            # If there is overtime, the value will be greater than 0
            if room_overtime > 0:
                overdue_string = str(room_overtime) + " minutes overtime"
            else:
                overdue_string = "not overdue"
            print("Room " + str(room) + ": " + overdue_string)

            # It prints a list of surgeries in a room
            room_surgeries = schedule[day][room]
            for i, surgery in enumerate(room_surgeries):
                # For the first surgery, it does not want to put a comma in front
                if i == 0:
                    sep = ""
                else:
                    sep = ", "
                # It prints them on one line, separating using sep
                print(sep + "Surgery " + str(surgery), end='')
            print()

    print("\n")

    # Here it prints which rooms are the overdue ones on a certain day
    for day in room_overtimes.keys():
        max_overtime = max_overtimes[day]
        # It makes a list of the rooms that have the maximum overtime associated with the day
        max_overtime_rooms = []
        for room in room_overtimes[day].keys():
            if room_overtimes[day][room] == max_overtime:
                max_overtime_rooms.append(room)
        # If it is greater than 1, use 'are' instead of 'is'  and such
        if len(max_overtime_rooms) > 1:
            room_overtime_string = "Rooms "
            for overtime_room in max_overtime_rooms:
                room_overtime_string += str(overtime_room) + " "
            room_overtime_string += "are "
        else:
            room_overtime_string = "Room " + str(max_overtime_rooms[0]) + " is "
        print("On day " + str(day) + ", " + room_overtime_string + "most overdue, at " + str(max_overtime) +
              " minutes")
