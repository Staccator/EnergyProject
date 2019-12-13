from block import *
from scipy import *
from scipy.optimize import minimize

# heat = pandas.read_csv('Dane_cieplo.csv', sep=';')
# x = heat['Hour']
# y = pandas.to_numeric(heat['Heat_load'])

def target(x1,x2):
    return b1.cost(x1) + b2.cost(x2)


def optimize(b1, b2, heat_needs):
    # Create the 'prob' variable to contain the problem data
    res = minimize(target, x0, method='L-BFGS-B', options={'disp': True},
                   bounds=((0.0, 200.0), (0.0, 60.0), (0.0, 170.0), (0.0, 350.0)))


def main():
    b1 = Block(140, 0.4, 0.4, 0.6)
    b2 = Block(300, 0.7, 0.6, 0.7)
    power_ratio = 0.7
    cost = b1.cost(power_ratio)
    heat, electricity = b1.created_energy(power_ratio)
    print(cost, heat, electricity)
    heat_needs = 300
    optimize(b1, b2, heat_needs)


main()


