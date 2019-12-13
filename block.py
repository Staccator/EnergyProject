import pandas


class Block:
    def __init__(self, max_power, heat_ratio, min_efficiency, max_efficiency):
        self.min_ratio = 0.4
        self.fuel_cost_per_MW = 15

        self.max_power = max_power
        self.heat_ratio = heat_ratio
        self.min_efficiency = min_efficiency
        self.max_efficiency = max_efficiency

    def current_power(self, power_ratio):
        return self.max_power * power_ratio

    def efficiency(self, power_ratio):
        efficiency_percent = (power_ratio - self.min_ratio) / (1 - self.min_ratio)
        efficiency = self.min_efficiency + (self.max_efficiency - self.min_efficiency) * efficiency_percent
        return efficiency

    def cost(self, power_ratio):
        return (self.current_power(power_ratio) / self.efficiency(power_ratio)) * self.fuel_cost_per_MW

    def created_energy(self, power_ratio):
        current_pow = self.current_power(power_ratio)
        created_heat = current_pow * self.heat_ratio
        created_electricity = current_pow - created_heat
        return created_heat, created_electricity
