import math
from pprint import pprint as pp


def generate_combination(n):
    return [int_to_binary_string(i, n) for i in range(int(math.pow(2, n)))]


def int_to_binary_string(number, count):
    return [bool(number >> i & 1) for i in range(count)]


def test():
    pp(generate_combination(3)[1:])
