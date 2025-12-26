EXP_THRESHOLDS = [
    0, 100, 250, 400, 600, 900, 1250, 1600, 2200, 3000,
    4200, 5500, 7000, 9000, 12000, 15000, 18000, 22000,
    27000, 32000, 38000, 48000, 60000, 78000, 100000
]

def calculate_level(exp: int) -> int:
    current_level = 0
    for threshold in EXP_THRESHOLDS:
        if exp >= threshold:
            current_level += 1
        else:
            break
    return current_level