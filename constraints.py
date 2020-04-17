from Units.UnitA import UnitA
from Units.UnitCD import UnitCD


def create_constraints(combination, demand, hour_temperature):
    constraints = [{'type': 'eq', 'fun': lambda x: sum(x[-4:]) - demand}]

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

    maxPtA = UnitA.Pt_Max_per_temperature(hour_temperature)

    boundsA = (40, maxPtA) if combination[0] else (None, None)
    boundsC = (139, 220) if combination[2] else (None, None)
    boundsD = (139, 220) if combination[3] else (None, None)

    bounds = (
        (None, None), (None, None), (None, None), (None, None),
        boundsA, (None, None), boundsC, boundsD
    )

    return tuple(constraints), bounds

