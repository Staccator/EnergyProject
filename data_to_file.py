from Units.UnitA import UnitA
from Units.UnitB import UnitB
from Units.UnitCD import UnitCD
from target_functions import real_target_function


def write_to_csv(year_results, energy_data, historyA, historyB, historyC, historyD, acc_energy_change, acc_energy_level, profit):
    PtS = acc_energy_change[1:]
    E = acc_energy_level[1:]
    Y = []

    PeA, PeB, PeC, PeD, RA, RB, RC, RD = [], [], [], [], [], [], [], []
    PtA, PtB, PtC, PtD, Pe, Pt = [], [], [], [], [], []
    ZgA, Zw, ZwB, ZwC, ZwD = [], [], [], [], []

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
        Y.append(real_target_function(
            [result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7]],
            ind, R, PtS[ind], profit)
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
