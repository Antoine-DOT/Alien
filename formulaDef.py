import math

def calculate_damage(attk, defense):
    """Calculate the damage done with a given attack and defense value."""
    damage_reduction = 100 * (1 - math.exp(-defense / 200.0))
    effective_damage = attk * (1 - (damage_reduction / 100.0))  # Apply the damage reduction
    return effective_damage

def main():
    attk = float(input("Enter attack value: "))
    defense = float(input("Enter defense value: "))
    damage = calculate_damage(attk, defense)
    print(f"Effective damage done: {damage}")

if __name__ == "__main__":
    main()
