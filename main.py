from Units.UnitA import *
from Units.UnitB import *
from Units.UnitCD import *
from scipy.optimize import minimize
from history import *
import pandas
import numpy as np
import combinations
import time
import accumulator


def load_data():
    global energy_data
    energy_data = pandas.read_csv('data/dane1.csv', sep=';')

    global temperature
    temperature = list(energy_data['t'])

    global profit
    profit = list(energy_data['K'])[:-1]
    global avg_profit
    global group_hours
    group_hours = 24  # * 2
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


def target_function(array):
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


def good_target_function(array, hour, R, pts):
    global profit
    K = profit[hour]
    Pe = array[:4]
    Pt = array[4:]

    value = sum(Pe) * K + (sum(Pt) - pts) * 130. + \
            (-32. * UnitA.Zg_per_Pt(Pt[0])) + \
            (-20.8 * (UnitB.Zw_per_Pe_Pt(Pe[1], Pt[1]) + UnitCD.Zw_per_Pt(Pt[2]) + UnitCD.Zw_per_Pt(Pt[3]))) + \
            -R
    return value


def create_constraints(combination, demand):
    constraints = []
    constraints.append(
        {'type': 'eq', 'fun': lambda x: sum(x[-4:]) - demand},
    )

    if combination[0]:  # Unit A
        constraints.append({'type': 'eq', 'fun': lambda x: UnitA.Pe_per_Pt(x[4]) - x[0]})
    else:
        constraints.append({'type': 'eq', 'fun': lambda x: x[0]})
        constraints.append({'type': 'eq', 'fun': lambda x: x[4]})

    if combination[1]:  # Unit B
        constraints.extend([
            {'type': 'ineq', 'fun': lambda x: x[1] - 72.},
            {'type': 'ineq', 'fun': lambda x: x[5]},
            {'type': 'ineq', 'fun': lambda x: -0.0842 * x[5] + 120 - x[1]},
            {'type': 'ineq', 'fun': lambda x: -0.1892 * x[5] + 129.973 - x[1]},
            {'type': 'ineq', 'fun': lambda x: x[1] - 0.587 * x[5] + 1.956},
        ]
        )
    else:
        constraints.append({'type': 'eq', 'fun': lambda x: x[1]})
        constraints.append({'type': 'eq', 'fun': lambda x: x[5]})

    if combination[2]:  # Unit C
        constraints.append({'type': 'eq', 'fun': lambda x: UnitCD.Pe_per_Pt(x[6]) - x[2]})
    else:
        constraints.append({'type': 'eq', 'fun': lambda x: x[2]})
        constraints.append({'type': 'eq', 'fun': lambda x: x[6]})

    if combination[3]:  # Unit D
        constraints.append({'type': 'eq', 'fun': lambda x: UnitCD.Pe_per_Pt(x[7]) - x[3]})
    else:
        constraints.append({'type': 'eq', 'fun': lambda x: x[3]})
        constraints.append({'type': 'eq', 'fun': lambda x: x[7]})

    global temperature
    T = temperature[hour]
    maxPtA = UnitA.Pt_Max_per_temperature(T)

    boundsA = (40, maxPtA) if combination[0] else (None, None)
    boundsC = (139, 220) if combination[2] else (None, None)
    boundsD = (139, 220) if combination[3] else (None, None)

    bounds = (
        (None, None), (None, None), (None, None), (None, None),
        boundsA, (None, None), boundsC, boundsD
    )

    return tuple(constraints), bounds


def find_optimization(combination, demand):
    global hour
    constraints, bounds = create_constraints(combination, demand)

    res = minimize(target_function, np.array([28.86, 73., 66., 66., 41., 1., 140., 140.]),
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
            energy_change = accumulator.accumulator_function_basic(acc_energy_level[index], energy_price, avg_for_hour,
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
    update_historyA(historyA)
    update_historyBCD(historyB)
    update_historyBCD(historyC)
    update_historyBCD(historyD)
    elapsed = time.time() - start
    print('ELAPSED TIME')
    print(elapsed)

    return year_results


def upload_to_csv(year_results):
    global energy_data
    global historyA
    global historyB
    global historyC
    global historyD
    global acc_energy_change
    global acc_energy_level
    PtS = acc_energy_change[1:]
    E = acc_energy_level[1:]

    Y = []

    PeA = []
    PeB = []
    PeC = []
    PeD = []
    RA = []
    RB = []
    RC = []
    RD = []

    PtA = []
    PtB = []
    PtC = []
    PtD = []
    Pe = []
    Pt = []
    ZgA = []
    Zw = []
    ZwB = []
    ZwC = []
    ZwD = []

    for ind, resulttuple in enumerate(year_results):
        result = resulttuple[2]
        # ZUZYCIE GAZU I WEGLA
        ZgA.append(UnitA.Zg_per_Pt(result[4]))
        zwb = UnitB.Zw_per_Pe_Pt(result[1], result[5])
        zwc = UnitCD.Zw_per_Pt(result[6])
        zwd = UnitCD.Zw_per_Pt(result[7])
        ZwB.append(zwb)
        ZwC.append(zwc)
        ZwD.append(zwd)
        Zw.append(zwb + zwc + zwd)

        # Moc energii cieplnej i elektrycznej
        PeA.append(result[0])
        PeB.append(result[1])
        PeC.append(result[2])
        PeD.append(result[3])
        PtA.append(result[4])
        PtB.append(result[5])
        PtC.append(result[6])
        PtD.append(result[7])
        # Sumaryczna moc energii cieplnej i elektrycznej
        Pe.append(result[0] + result[1] + result[2] + result[3])
        Pt.append(result[4] + result[5] + result[6] + result[7] - PtS[ind])
        # Rozruch A
        if historyA[ind] == 2:
            RA.append(5000)
        else:
            RA.append(0)
        # Rozruch B
        if historyB[ind] == 3:
            RB.append(12000)
        elif historyB[ind] == 4:
            RB.append(10000)
        else:
            RB.append(0)
        # Rozruch C
        if historyC[ind] == 3:
            RC.append(12000)
        elif historyC[ind] == 4:
            RC.append(10000)
        else:
            RC.append(0)
        # Rozruch D
        if historyD[ind] == 3:
            RD.append(12000)
        elif historyD[ind] == 4:
            RD.append(10000)
        else:
            RD.append(0)
        # Funkcja celu
        R = RA[ind] + RB[ind] + RC[ind] + RD[ind]
        Y.append(good_target_function(
            [result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7]],
            ind, R, PtS[ind])
        )

    Y.append(sum(Y))
    Y = [round(x, 3) for x in Y]
    energy_data['Y'] = Y
    Pt.append(sum(Pt))
    Pt = [round(x, 3) for x in Pt]
    energy_data['Pt'] = Pt
    Pe.append(sum(Pe))
    Pe = [round(x, 3) for x in Pe]
    energy_data['Pe'] = Pe
    ZgA.append(sum(ZgA))
    ZgA = [round(x, 3) for x in ZgA]
    energy_data['ZgA'] = ZgA
    energy_data['Zg'] = ZgA

    Zw.append(sum(Zw))
    Zw = [round(x, 3) for x in Zw]
    energy_data['Zw'] = Zw

    PtA.append(sum(PtA))
    PtA = [round(x, 3) for x in PtA]
    energy_data['PtA'] = PtA
    PtB.append(sum(PtB))
    PtB = [round(x, 3) for x in PtB]
    energy_data['PtB'] = PtB
    PtC.append(sum(PtC))
    PtC = [round(x, 3) for x in PtC]
    energy_data['PtC'] = PtC
    PtD.append(sum(PtD))
    PtD = [round(x, 3) for x in PtD]
    energy_data['PtD'] = PtD

    PtS = [round(x, 3) for x in PtS]
    PtS.append(str(min(PtS)) + '/' + str(max(PtS)))
    energy_data['PtS'] = PtS
    E = [round(x, 3) for x in E]
    E.append(str(min(E)) + '/' + str(max(E)))
    energy_data['E'] = E

    PeA.append(sum(PeA))
    PeA = [round(x, 3) for x in PeA]
    energy_data['PeA'] = PeA
    PeB.append(sum(PeB))
    PeB = [round(x, 3) for x in PeB]
    energy_data['PeB'] = PeB
    PeC.append(sum(PeC))
    PeC = [round(x, 3) for x in PeC]
    energy_data['PeC'] = PeC
    PeD.append(sum(PeD))
    PeD = [round(x, 3) for x in PeD]
    energy_data['PeD'] = PeD

    ZwB.append(sum(ZwB))
    ZwB = [round(x, 3) for x in ZwB]
    energy_data['ZwB'] = ZwB
    ZwC.append(sum(ZwC))
    ZwC = [round(x, 3) for x in ZwC]
    energy_data['ZwC'] = ZwC
    ZwD.append(sum(ZwD))
    ZwD = [round(x, 3) for x in ZwD]
    energy_data['ZwD'] = ZwD

    RA.append(sum(RA))
    energy_data['RA'] = RA
    RB.append(sum(RB))
    energy_data['RB'] = RB
    RC.append(sum(RC))
    energy_data['RC'] = RC
    RD.append(sum(RD))
    energy_data['RD'] = RD

    energy_data.to_csv('data/wyniki1.csv', sep=';', index=False)


def main():
    load_data()
    try:
        year_results = calculate_target_yearly()
    except:
        print('')
    print('CALCULATED')
    upload_to_csv(year_results)


main()
