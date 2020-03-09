class UnitCD:
    @staticmethod
    def Pe_per_Pt(Pt):
        return (44. / 81.) * Pt + 66 - (6116. / 81.)

    @staticmethod
    def Zw_per_Pt(Pt):
        return 0 if abs(Pt) < 0.001 else 5.75 * Pt + 57.82
