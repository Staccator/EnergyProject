import time

import numpy as np
import pandas
from scipy.optimize import minimize

import accumulator
import combinations
from Units.UnitA import *
from Units.UnitB import *
from Units.UnitCD import *
from constraints import create_constraints
from data_to_file import write_to_csv
from history import *


def load_data():
    global energy_data
    energy_data = pandas.read_csv('data/dane1.csv', sep=';')

    global temperature
    temperature = list(energy_data['t'])

    global profit
    profit = list(energy_data['K'])[:-1]
    global avg_profit
    global group_hours
    group_hours = 24
    avg_profit = [sum(profit[i * group_hours: min((i + 1) * group_hours, len(profit))]) / group_hours
                  for i in range(math.ceil(8760 / group_hours))]

    # avg_profit = sum(profit) / len(profit)

    global Ptz
    Ptz = list(energy_data['Ptz'])

    global AvailabilityA
    global AvailabilityB
    global AvailabilityC
    global AvailabilityD
    AvailabilityA = list(energy_data['DA'])
    AvailabilityB = list(energy_data['DB'])
    AvailabilityC = list(energy_data['DC'])
    AvailabilityD = list(energy_data['DD'])


def custom_target_function(array):
    global profit
    global hour
    K = profit[hour]
    Pe = array[:4]
    Pt = array[4:]

    value = sum(Pe) * K + sum(Pt) * 130 + \
            (-32 * UnitA.Zg_per_Pt(Pt[0])) + \
            (-20.8 * (UnitB.Zw_per_Pe_Pt(Pe[1], Pt[1]) * 0.8 + UnitCD.Zw_per_Pt(Pt[2]) * 1.05 + UnitCD.Zw_per_Pt(
                Pt[3])))
    return -value


def find_optimization(combination, demand):
    global hour
    global temperature
    hour_temperature = temperature[hour]
    constraints, bounds = create_constraints(combination, demand, hour_temperature)

    res = minimize(custom_target_function, np.array([28.86, 73., 66., 66., 41., 1., 140., 140.]),
                   method='SLSQP',
                   bounds=bounds,
                   constraints=constraints,
                   options={
                       # 'disp': True,
                       'maxiter': 100}
                   )

    return res.x, -res.fun, res.success


def calculate_target_yearly():
    global AvailabilityA
    global AvailabilityB
    global AvailabilityC
    global AvailabilityD
    global historyA
    global historyB
    global historyC
    global historyD
    historyA = [1] * 15
    historyB = [1] * 15
    historyC = [1] * 15
    historyD = [1] * 15
    year_results = []
    bad_numbers = {1, 2, 3, 12, 13, 14}
    global acc_energy_change
    global acc_energy_level
    acc_energy_change = [0]
    acc_energy_level = [0]
    all_combs = combinations.generate_combination(4)  # [1:]

    start = time.time()

    global Ptz
    global profit
    for index, h in enumerate(range(0, 8760)):
        if divmod(h, 20)[1] == 0:
            print(h)
        global hour
        hour = h
        start_demand = Ptz[hour]
        energy_price = profit[hour]
        avA = AvailabilityA[h]
        avB = AvailabilityB[h]
        avC = AvailabilityC[h]
        avD = AvailabilityD[h]

        # Changing demand depending on accumulator

        avg_for_hour = avg_profit[h // group_hours]
        error_counter = 0
        while True:
            energy_change = accumulator.accumulator_function(acc_energy_level[index], energy_price, avg_for_hour,
                                                             error_counter, start_demand)
            temp_demand = start_demand + energy_change
            if temp_demand == 0:
                acc_energy_change.append(energy_change)
                acc_energy_level.append(acc_energy_level[index] + energy_change)
                best_comb = (False, False, False, False)
                historyA.append(int(best_comb[0]))
                historyB.append(int(best_comb[1]))
                historyC.append(int(best_comb[2]))
                historyD.append(int(best_comb[3]))
                year_results.append((-1, best_comb, (0, 0, 0, 0, 0, 0, 0, 0)))
                break

            hour_results = {}
            for comb in all_combs:
                if (avA == 0 and comb[0] == 1) or (avB == 0 and comb[1] == 1) or (avC == 0 and comb[2] == 1) or (
                        avD == 0 and comb[3] == 1):
                    continue

                min_available_power = 40 * comb[0] + 139 * comb[2] + 139 * comb[3]
                if min_available_power > temp_demand:
                    continue

                max_available_power = 50.85 * comb[0] + 171 * comb[1] + 220 * comb[2] + 220 * comb[3]
                if max_available_power < temp_demand:
                    continue

                max_boundary = max_available_power + 120
                if historyA[-1] and not comb[0]:
                    exits = False
                    for i in range(1, min(2, 8760 - h)):
                        if max_boundary < Ptz[h + i]:
                            exits = True
                    if exits:
                        continue

                # don't disable if needed
                if any(a and not b for a, b in zip([historyB[-1], historyC[-1], historyD[-1]], comb[1:])):
                    exits = False
                    for i in range(1, min(5, 8760 - h)):
                        if max_boundary < Ptz[h + i]:
                            exits = True
                    if exits:
                        continue

                # don't switch between unitC and unitD
                if historyC[-1] and not historyD[-1] and not comb[2] and comb[3] and avC == 1 and avD == 1:
                    continue
                if not historyC[-1] and historyD[-1] and comb[2] and not comb[3] and avC == 1 and avD == 1:
                    continue

                # History check
                if comb[0] and historyA[-2] == 1 and historyA[-1] == 0:
                    continue
                if comb[1]:
                    ind = len(historyB) - 1
                    count = 0
                    while historyB[ind] == 0:
                        count += 1
                        ind -= 1
                    if count in bad_numbers:
                        continue
                if comb[2]:
                    ind = len(historyC) - 1
                    count = 0
                    while historyC[ind] == 0:
                        count += 1
                        ind -= 1
                    if count in bad_numbers:
                        continue
                if comb[3]:
                    ind = len(historyD) - 1
                    count = 0
                    while historyD[ind] == 0:
                        count += 1
                        ind -= 1
                    if count in bad_numbers:
                        continue

                result, value, success = find_optimization(comb, temp_demand)
                penalty = 0
                penalty += 5000 if historyA[-1] and not comb[0] else 0
                penalty += 36000 if historyB[-1] and not comb[1] else 0
                penalty += 36000 if historyC[-1] and not comb[2] else 0
                penalty += 36000 if historyD[-1] and not comb[3] else 0
                value -= penalty

                if success:
                    hour_results[value] = comb, result

            if len(hour_results) >= 1:
                # FOUNT GOOD RESULT
                acc_energy_change.append(energy_change)
                acc_energy_level.append(acc_energy_level[index] + energy_change)

                best_result_value = max(hour_results)
                best_comb, best_result = hour_results[best_result_value]
                historyA.append(int(best_comb[0]))
                historyB.append(int(best_comb[1]))
                historyC.append(int(best_comb[2]))
                historyD.append(int(best_comb[3]))
                year_results.append((best_result_value, best_comb, best_result))
                break
            else:
                error_counter += 1

    historyA = historyA[15:]
    historyB = historyB[15:]
    historyC = historyC[15:]
    historyD = historyD[15:]
    update_history(historyA, historyB, historyC, historyD)

    elapsed = time.time() - start
    print('ELAPSED TIME = ', elapsed)
    return year_results


def main():
    load_data()
    try:
        year_results = calculate_target_yearly()
    except:
        print('')

    global energy_data
    global historyA
    global historyB
    global historyC
    global historyD
    global acc_energy_change
    global acc_energy_level
    global profit

    print('Finished, Annual profit amounts to : ', energy_data['Y'][-1:])
    write_to_csv(year_results, energy_data, historyA, historyB, historyC, historyD, acc_energy_change, acc_energy_level,
                 profit)


main()
