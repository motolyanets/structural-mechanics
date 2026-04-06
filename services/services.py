def round_up(number: float, decimals: int = 2):
    multiplier = 10 ** decimals
    return int(number * multiplier + 0.5) / multiplier

print(round_up(2.24))
