def update_historyA(history):
    for ind, value in enumerate(history[:-1]):
        if value == 0 and history[ind + 1] == 1:
            history[ind] = 2

def update_historyBCD(history):
    zero_count = 0
    for ind, value in enumerate(history[:-1]):
        if value == 0:
            zero_count += 1
        if value == 1:
            if zero_count == 0:
                continue

            if zero_count < 12:
                for i in range(-3,0):
                    history[ind + i] = 3
            else:
                for i in range(-6,0):
                    history[ind + i] = 4
            zero_count = 0
