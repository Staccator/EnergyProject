max_energy = 840.
min_energy_safe_level = 320.
max_energy_safe_level = 600.

error_solvers = [0, 30, -30, 60, -60, 90, -90, 120, -120]
#error_solvers = [30, 60, 90, 120, -30, -60, -90, -120]


def accumulator_function(energy_level, energy_price, avg_profit, error_counter, demand):
    if error_counter == 0:
        if energy_level > min_energy_safe_level:
            if energy_price < avg_profit:
                return - min((1 - energy_price / avg_profit) * 40, energy_level, demand)
                #return - min(40, energy_level, demand)
        if energy_level < max_energy_safe_level:
            if energy_price > avg_profit:
                return min((energy_price / avg_profit - 1) * 40, max_energy - energy_level, 120)
        if energy_level < min_energy_safe_level:
            return 60
        return 0
    else:
        energy_change = error_solvers[error_counter]
        if energy_change < 0:
            return - min(-energy_change, energy_level, demand)
        else:
            return min(energy_change, max_energy - energy_level)
