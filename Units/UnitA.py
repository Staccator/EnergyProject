import math


class UnitA:

    @staticmethod
    def Pt_Max_per_temperature(temperature):
        return 50.85 if temperature < 5 else -0.23 * temperature + 52

    @staticmethod
    def Pe_per_Pt(Pt):
        return 0.00024 * math.pow(Pt, 3) - 0.004 * math.pow(Pt, 2) + 0.4 * Pt + 3.9

    @staticmethod
    def Zg_per_Pt(Pt):
        return 0 if abs(Pt) < 0.001 else 6.33 * Pt - 15.94
