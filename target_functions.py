from Units.UnitA import UnitA
from Units.UnitB import UnitB
from Units.UnitCD import UnitCD


def real_target_function(array, hour, R, pts, profit):
    K = profit[hour]
    Pe = array[:4]
    Pt = array[4:]

    value = sum(Pe) * K + (sum(Pt) - pts) * 130. + \
            (-32. * UnitA.Zg_per_Pt(Pt[0])) + \
            (-20.8 * (UnitB.Zw_per_Pe_Pt(Pe[1], Pt[1]) + UnitCD.Zw_per_Pt(Pt[2]) + UnitCD.Zw_per_Pt(Pt[3]))) + \
            -R
    return value
