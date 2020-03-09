epsilon = 0.001


class UnitB:
    @staticmethod
    def Zw_per_Pe_Pt(Pe, Pt):
        if abs(Pe) < epsilon:
            return 0
        if Pe < 105.:
            if abs(Pt) < epsilon:
                return 9.03 * Pe + 124.79
            else:
                return Pt * (1.98 * Pe + 61.34) / (1.72 * Pe + 2.43) + (8.66 * Pe + 129.68)
        else:
            if abs(Pt) < epsilon:
                return 9.03 * Pe + 124.79
            else:
                return Pt * (0.5 * Pe + 61.34) / (-5.28 * Pe + 686.83) + (8.66 * Pe + 129.68)
