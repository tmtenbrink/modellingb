surgery_amount = 30
days_amount = 2
rooms_amount = 3

I = range(1, surgery_amount + 1)
T = range(1, days_amount + 1)
R = range(1, rooms_amount + 1)

thing = {}

for i in I:
    thing[i] = {}
    for t in T:
        thing[i][t] = {}
        for r in R:
            thing[i][t][r] = str(i) + " " + str(t) + " " + str(r)

for i in I:
    print([thing[i][t][r] for t in T for r in R])
