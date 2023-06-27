def xp_needed_for_level() -> int:
    target_level = int(input("Please enter the target level: "))
    
    base_xp = 75
    total_xp = 0

    for i in range(1, target_level):
        total_xp += base_xp

        if i < 10:
            increase_percent = 1.20
        elif i < 20:
            increase_percent = 1.13
        elif i < 30:
            increase_percent = 1.15
        elif i < 40:
            increase_percent = 1.17
        elif i < 42:
            increase_percent = 1.20
        else:
            increase_percent += 0.01

        base_xp *= increase_percent

    level_xp = int(base_xp)
    total_xp += level_xp

    return total_xp, level_xp

# Testing
total_xp_needed, level_xp_needed = xp_needed_for_level()
print("Total XP needed:", total_xp_needed)
print("XP needed for the target level:", level_xp_needed)
