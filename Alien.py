import time
import math
import unicodedata
from typing import Callable, Dict, List, Tuple, Optional, Any
import random
import os

# Class
class Monster:
    def __init__(self, name: str, hp: int, damage: int, defense: int, gold_reward: int,xp_reward: int, crit_chance=0.03, crit_damage=1.25, dodge_chance=0.01):
        self.name = name
        self.hp = hp
        self.damage = damage
        self.defense = defense
        self.crit_chance = crit_chance
        self.crit_damage = crit_damage
        self.dodge_chance = dodge_chance
        self.gold_reward = gold_reward
        self.xp_reward = xp_reward
        self.initial_hp = hp  # Store the initial HP to reset later

    @property
    def variable_gold_reward(self):
        """Return a random gold reward between 70% and 130% of the monster's gold reward."""
        variation = self.gold_reward * 0.3
        return round(random.uniform(self.gold_reward - variation, self.gold_reward + variation))

    def attack(self, player: 'Player') -> None:
        """The monster attacks the player."""
        damage_variation = self.damage * 0.1  # Calculate 10% of the monster's damage
        modified_damage = self.damage + random.uniform(-damage_variation, damage_variation)  # Add the random damage variation to the monster's damage
        modified_damage = round(modified_damage)  # Round the modified damage
        
        if random.random() <= player.dodge_chance:  # Player dodges the attack
            print(f"{player.name} dodged the attack from {self.name}!")
        elif random.random() <= self.crit_chance:  # Monster lands a critical hit
            crit_dmg = round(modified_damage * self.crit_damage)  # Round the critical damage
            damage_reduction = player.calculate_damage_reduction(player.calculate_defense())
            effective_crit_damage = crit_dmg * (1 - damage_reduction / 100.0)  # Apply the damage reduction
            effective_crit_damage = round(effective_crit_damage)  # Round the effective crit damage
            player.hp -= effective_crit_damage
            print(f"{self.name} landed a critical hit on {player.name} for {effective_crit_damage} damage!")
        else:
            damage_reduction = player.calculate_damage_reduction(player.calculate_defense())
            effective_damage = modified_damage * (1 - damage_reduction / 100.0)  # Apply the damage reduction after the damage variation
            effective_damage = round(effective_damage)  # Round the effective damage
            player.hp -= effective_damage  # Player gets hit
            print(f"{self.name} attacked {player.name} for {effective_damage} damage!")

class Player:
    """Player class for the RPG game."""

    def __init__(self, name: str):
        """Initialize the player with default attributes."""
        self.name = name
        self.max_hp = 100
        self.xp = 0
        self.level = 1
        self.level_bonuses = [False]*51  # Initialize a list of 51 False, one for each level until 50
        self.achievements = []
        self.total_xp = 0  # Initialize total XP
        self.reset()

    def reset(self) -> None:
        """Reset the player attributes to the default state."""
        self.hp = self.max_hp
        self.base_atk = 15
        self.gold = 0
        self.defense = 0
        self.crit_chance = 0.03
        self.crit_damage = 1.25
        self.dodge_chance = 0.01
        self.in_battle = False
        self.inventory = []
        self.equipped_weapon = Weapon("baton de bwa", 0, 5)
        self.equipped_ring = None
        self.equipped_necklace = None
        self.equipped_armor = {
            'Hat': None,
            'Chestplate': None,
            'Pant': None,
            'Boots': None,
        }
        self.monster_kills = {}
    
    def record_kill(self, monster_name: Monster) -> None:
        if monster_name in self.monster_kills:
            self.monster_kills[monster_name] += 1
        else:
            self.monster_kills[monster_name] = 1
    
    def get_total_kills(self) -> int:
        return sum(self.monster_kills.values())

    def get_kills(self, monster_name: str) -> int:
        return self.monster_kills.get(monster_name, 0)  # Returns 0 if the monster name is not found
    
    def print_monster_kills(self):
        """Print the number of times the player has killed each type of monster."""
        for monster_name, kill_count in self.monster_kills.items():
            print(f"You have killed {kill_count} {monster_name}(s).")

    def add_achievement(self, achievement: 'Achievement'):
        if not isinstance(achievement, Achievement):
            raise TypeError(f"Expected Achievement, got {type(achievement)} instead.")
        self.achievements.append(achievement)

    def check_achievements(self):
        # print(self.achievements)  # Debug print
        for achievement in self.achievements:
            if not achievement.is_achieved and achievement.check_condition(self):  
                gold_reward, xp_reward = achievement.reward
                if achievement.effect:
                    print(f"You have achieved {achievement.name} | {achievement.description} | Tu as obtenu {gold_reward} gold et {xp_reward} XP, ainsi qu'une amélioration de {achievement.effect_params[0]} {effect_to_stat[achievement.effect.__name__]}.")
                else:
                    print(f"You have achieved {achievement.name} | {achievement.description} | Tu as obtenu {gold_reward} gold et {xp_reward} XP.")
                achievement.give_reward(self)
                achievement.is_achieved = True
    def has_achievement(self, achievement_name: str) -> bool:
        for achievement in self.achievements:
            if achievement.name == achievement_name and achievement.is_achieved:
                return True
        return False
    
    def display_achievements(self):
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')

        print("\n*** Achievements ***")
        while True:
            choice = input("\nDo you want to display:\n1) Incomplete Achievements\n2) Completed Achievements\nYour choice (1/2): ")
            if choice in ['1', '2']:
                # Clear screen before displaying achievements
                os.system('cls' if os.name == 'nt' else 'clear')
                break
            else:
                print("Invalid choice. Please enter either 1 or 2.")
                
        if choice == '1':
            print("\n--- Incomplete Achievements ---")
        else:
            print("\n--- Completed Achievements ---")
            
        for achievement in self.achievements:
            if (choice == '2' and achievement.is_achieved) or (choice == '1' and not achievement.is_achieved):
                if achievement.display_condition is None or achievement.display_condition(self):
                    status = "Completed" if achievement.is_achieved else "Incomplete"
                    print(f"\n{achievement.name} - {status}")
                    if achievement.description:
                        print(f"  {achievement.description}")

        print("\n******************************")  # End line for clarity



    def level_up(self) -> None:
        while self.level < len(Player.xp_requirements) - 1 and self.xp >= Player.xp_requirements[self.level]:
            self.xp -= Player.xp_requirements[self.level]  # Subtract the xp needed to reach this level
            self.level += 1

            # Adjust stats increase based on the level reached
            if self.level <= 10:
                self.max_hp += 5
                self.base_atk += 2
                self.defense += 0
            elif self.level <= 20:
                self.max_hp += 10
                self.base_atk += 4
                self.defense += 1
            elif self.level <= 30:
                self.max_hp += 20
                self.base_atk += 5
                self.defense += 2
            elif self.level <= 40:
                self.max_hp += 50
                self.base_atk += 10
                self.defense += 3
            else:  # Level 41 to 50
                self.max_hp += 100
                self.base_atk += 20
                self.defense += 4

            print(f"You have reached level {self.level}! Your stats have been increased.")
            self.give_bonus()  # Add this line
        if self.level >= len(Player.xp_requirements) - 1:
            print("You are level max.")
            self.xp = Player.xp_requirements[-1]  # Set xp to the maximum possible


    level_bonuses_data = {
        10: {'crit_chance': 0.01, 'crit_damage': 0.05},
        20: {'crit_chance': 0.02, 'crit_damage': 0.10, 'dodge_chance': 0.01},
        30: {'crit_chance': 0.03, 'crit_damage': 0.15, 'dodge_chance': 0.01},
        40: {'crit_chance': 0.07, 'crit_damage': 0.30, 'dodge_chance': 0.02},
        50: {'crit_chance': 0.10, 'crit_damage': 0.50, 'dodge_chance': 0.03},
    }

    def give_bonus(self) -> None:
        if self.level in Player.level_bonuses_data and not self.level_bonuses[self.level]:
            bonuses = Player.level_bonuses_data[self.level]
            for bonus_type, bonus_value in bonuses.items():
                setattr(self, bonus_type, getattr(self, bonus_type) + bonus_value)
                print(f"Your {bonus_type} has increased by {bonus_value}!")
            self.level_bonuses[self.level] = True

    def add_xp(self, amount: int) -> None:
        self.xp += amount
        self.total_xp += amount  # Update total XP
        self.level_up()  # Appel de la méthode level_up() après l'ajout d'XP

    def print_commands(self) -> None:
        """Print the available commands."""
        print("Available commands:")
        print("- zone: Explore a zone to fight some alien")
        print("- shop: Visit the shop")
        print("- buy: Buy an item from the shop")
        print("- sell: Sell an item from your inventory")
        print("- equip: Equip an item from your inventory")
        print("- stuff: Show equipped items and inventory")
        print("- stats: Show player statistics")
        print("- monster: Show your kill count")
        print("- succès: Display achievements")
        print("- quit: Quit the game")
        print("- help: Show this help message")

    def calculate_atk(self) -> int: 
        """Calculate the total attack value."""
        return self.base_atk + (self.equipped_weapon.damage if self.equipped_weapon else 0)
    def calculate_defense(self) -> int:
        """Calculate the total defense value."""
        return self.defense + sum(armor.defense for armor in self.equipped_armor.values() if armor)
    def calculate_max_hp(self) -> int:
        """Calculate the total max HP value."""
        base_max_hp = self.max_hp
        armor_hp_bonus = sum(armor.hp_bonus for armor in self.equipped_armor.values() if armor)
        return base_max_hp + armor_hp_bonus
    def calculate_crit_chance(self) -> float:
        """Calculate the total crit chance."""
        if self.equipped_ring:  # if there's a ring equipped
            return self.crit_chance + self.equipped_ring.crit_chance
        else:
            return self.crit_chance   
    def calculate_crit_damage(self) -> float:
        """Calculate the total crit damage"""
        crit_damage = self.crit_damage
        if self.equipped_necklace:
            crit_damage += self.equipped_necklace.crit_damage
        return crit_damage
    def attack(self, monster: 'Monster') -> None:
        """Attack a monster."""
        atk = self.calculate_atk()
        if atk > 0:
            crit_chance = self.calculate_crit_chance()
            damage_variation = atk * 0.1
            atk += random.uniform(-damage_variation, damage_variation)
            atk = round(atk)  # Round the attack value after applying the damage variation
            damage_reduction = self.calculate_damage_reduction(monster.defense)
            effective_atk = atk * (1 - damage_reduction / 100.0)  # Apply the damage reduction after the damage variation
            effective_atk = round(effective_atk)  # Round the effective attack
            if random.random() < crit_chance:
                crit_dmg = round(effective_atk * self.calculate_crit_damage())  # Use calculate_crit_damage() here
                monster.hp -= crit_dmg
                print(f"OwO You landed a cringical.. Ahem. Critical hit for {crit_dmg} on {monster.name}!")

            else:
                monster.hp -= effective_atk
                print(f"You attacked {monster.name} for {effective_atk} damage!")
        else:
            print("You have no weapon equipped!")

    @staticmethod
    def calculate_damage_reduction(defense: int) -> float:
        """Calculate the damage reduction based on defense."""
        return 100 * (1 - math.exp(-defense / 200.0))
    @staticmethod
    def generate_xp_requirements():
        base_xp = 75
        xp_requirements = [0]  # Start at 0 XP for level 1
        for i in range(1, 51):  # We loop from level 1 to 50
            xp_requirements.append(int(base_xp))

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
        
        return xp_requirements

    xp_requirements = generate_xp_requirements.__func__()

    def print_stats(self) -> None:
        """Print the current player's statistics."""
        print("Player Stats:")
        print(f"Name: {self.name}")
        print(f"Level: {self.level}")
        print(f"XP: {self.xp} sur {Player.xp_requirements[self.level]}, xp total: {self.total_xp}")
        print(f"HP: {self.calculate_max_hp()}")
        print(f"Attack: {self.calculate_atk()}")
        print(f"Defense: {self.calculate_defense()}")
        print(f"Crit Chance: {self.calculate_crit_chance() * 100:.2f}%")
        print(f"Crit Damage: {self.calculate_crit_damage() * 100}%")
        print(f"Dodge Chance: {self.dodge_chance * 100}%")

    def print_inventory(self) -> None:
        """Print the current inventory with a formatted UI."""
        print("Inventory:")
        print("-" * 30)
        for item in self.inventory:
            print(f"{item.name}")
            if isinstance(item, (Weapon, Armor, Ring, Necklace)):
                item.print_stats()
            print("-" * 30)

    def print_equipped_items_stats(self) -> None:
        """Print the statistics of equipped items with a compact UI."""
        print("\n*** Equipped Items ***")
        if self.equipped_weapon or self.equipped_ring or self.equipped_necklace or any(self.equipped_armor.values()):
            if self.equipped_weapon:
                print(f"Weapon: {self.equipped_weapon.name}")
                self.equipped_weapon.print_stats()
                print("------------")
            
            if self.equipped_ring:
                print(f"Ring: {self.equipped_ring.name}")
                self.equipped_ring.print_stats()
                print("------------")
            
            if self.equipped_necklace:
                print(f"Necklace: {self.equipped_necklace.name}")
                self.equipped_necklace.print_stats()
                print("------------")
            
            for slot, armor in self.equipped_armor.items():
                if armor:
                    print(f"{slot}: {armor.name}")
                    armor.print_stats()
                    print("------------")
        else:
            print("You have no items equipped.")


    def equip_item(self, item_name: str) -> None:
        """Equip an item from the inventory."""
        for item in self.inventory:
            if unicodedata.normalize('NFKD', item.name.lower()) == unicodedata.normalize('NFKD', item_name.lower()):
                if isinstance(item, Weapon):
                    if self.equipped_weapon:
                        self.inventory.append(self.equipped_weapon)  # Add the old weapon to the inventory
                    self.equipped_weapon = item  # Replace the old weapon with the new one
                elif isinstance(item, Armor):
                    # Check if there's an armor piece already equipped in the slot
                    if self.equipped_armor[item.slot]:
                        # Reduce max_hp by the old armor's hp_bonus
                        self.max_hp -= self.equipped_armor[item.slot].hp_bonus
                        self.inventory.append(self.equipped_armor[item.slot])  # Add the old armor piece to the inventory

                    # Replace the old armor piece with the new one
                    self.equipped_armor[item.slot] = item  
                    # Increase max_hp by the new armor's hp_bonus
                    self.max_hp += item.hp_bonus

                elif isinstance(item, Ring):  # Add this elif block
                    if self.equipped_ring:
                        self.inventory.append(self.equipped_ring)  # Add the old ring to the inventory
                    self.equipped_ring = item  # Replace the old ring with the new one

                elif isinstance(item, Necklace):  # Add this elif block
                    if self.equipped_necklace:
                        self.inventory.append(self.equipped_necklace)  # Add the old ring to the inventory
                    self.equipped_necklace = item  # Replace the old ring with the new one                    

                # Remove the newly equipped item from the inventory
                self.inventory.remove(item)
                print(f"You equipped {item.name}!")
                return

        print("You don't have this item in your inventory. Baka.")
    
    def sell(self, item_name):
        # Trouver l'item dans l'inventaire
        for item in self.inventory:
            if item.name.lower() == item_name:  # convertir item.name en minuscules
                # Calculer le prix de revente
                sell_price = int(item.value / 4)
                # Ajouter le prix de revente à l'or du joueur
                self.gold += sell_price
                # Supprimer l'item de l'inventaire
                self.inventory.remove(item)
                print(f"You sold {item_name} for {sell_price} gold!")
                return  # Si vous trouvez l'item, vous pouvez sortir de la fonction
        # Si vous arrivez ici, l'item n'était pas dans l'inventaire
        print(f"You don't have {item_name} in your inventory!")

    def admin_command(self):
        """Execute an admin command."""
        while True:
            command = input("Enter command (addxp, addgold, exit): ")
            if command.lower() == "exit":
                break
            elif command.lower() in ["addxp", "addgold"]:
                amount = int(input("Enter amount: "))
                if command == "addxp":
                    self.xp += amount
                    print(f"Added {amount} XP.")
                    self.level_up()  # Check if player levels up after adding XP
                elif command == "addgold":
                    self.gold += amount
                    print(f"Added {amount} gold.")
            else:
                print("Unknown command.")

class Item:
    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value

class Weapon(Item):
    def __init__(self, name: str, value: int, damage: int):
        super().__init__(name, value)
        self.damage = damage
    def print_stats(self):
        print(f"Damage: {self.damage}")

class Armor(Item):
    def __init__(self, name: str, value: int, defense: int, hp_bonus: int, slot: str):
        super().__init__(name, value)
        self.defense = defense
        self.hp_bonus = hp_bonus
        self.slot = slot

    def print_stats(self):
        print(f"Defense: {self.defense}")
        print(f"HP Bonus: {self.hp_bonus}")

class Ring(Item):
    def __init__(self, name: str, value: int, crit_chance: float):
        super().__init__(name, value)
        self.crit_chance = crit_chance
    def print_stats(self):
        print(f"Crit Chance: {self.crit_chance}")

class Necklace(Item):
    def __init__(self, name: str, value: int, crit_damage: float):
        super().__init__(name, value)
        self.crit_damage = crit_damage
    def print_stats(self):
        print(f"Crit Damage: {self.crit_damage}")

class Achievement:
    def __init__(self, name: str, condition: Callable[[Player], bool], reward: Tuple[int, int], description: str = "",
                 effect: Optional[Callable[[Player, Any], None]] = None, effect_params: Optional[Tuple[Any, ...]] = None,
                 display_condition: Optional[Callable[[Player], bool]] = None):
        self.name = name
        self.condition = condition
        self.reward = reward
        self.description = description
        self.is_achieved = False
        self.effect = effect
        self.effect_params = effect_params
        self.display_condition = display_condition

    def check_condition(self, player: Player) -> bool:
        return self.condition(player)

    def give_reward(self, player: Player) -> None:
        gold_reward, xp_reward = self.reward
        player.gold += gold_reward
        player.add_xp(xp_reward)
        if self.effect:
            self.effect(player, *self.effect_params)

#Achievements

def has_required_achievement(self, achievement: Achievement) -> bool:
    if not achievement.required_achievement:
        return True
    for ach in self.achievements:
        if ach.name == achievement.required_achievement:
            return ach.is_achieved
    return False

def meteor_guy(player: Player) -> bool:
    meteor_monsters = ["Eclair", "Crocus", "Lunaris", "Voltaic"]
    return all(player.get_kills(monster) > 0 for monster in meteor_monsters)
def killed_10_crocus(player: Player) -> bool:
    return player.get_kills("Crocus") >= 10
def killed_10_lunaris(player: Player) -> bool:
    return player.get_kills("Lunaris") >= 10
def killed_10_eclair(player: Player) -> bool:
    return player.get_kills("Eclair") >= 10
def killed_10_voltaic(player: Player) -> bool:
    return player.get_kills("Voltaic") >= 10
def killed_5_of_each_meteor_monster(player: Player) -> bool:
    meteor_monsters = ["Eclair", "Crocus", "Lunaris", "Voltaic"]
    return all(player.get_kills(monster) >= 5 for monster in meteor_monsters)
def killed_10_of_each_meteor_monster(player: Player) -> bool:
    meteor_monsters = ["Eclair", "Crocus", "Lunaris", "Voltaic"]
    return all(player.get_kills(monster) >= 10 for monster in meteor_monsters)
def killed_100_meteor_monsters(player: Player) -> bool:
    meteor_monsters = ["Eclair", "Crocus", "Lunaris", "Voltaic"]
    return sum(player.get_kills(monster) for monster in meteor_monsters) >= 100

def spatiofarm_guy(player: Player) -> bool:
    spatiofarm_monsters = ["Petalo", "Gloo", "Vaporis", "Foudro"]
    return all(player.get_kills(monster) > 0 for monster in spatiofarm_monsters)
def killed_10_petalo(player: Player) -> bool:
    return player.get_kills("Petalo") >= 10
def killed_10_gloo(player: Player) -> bool:
    return player.get_kills("Gloo") >= 10
def killed_10_vaporis(player: Player) -> bool:
    return player.get_kills("Vaporis") >= 10
def killed_10_foudro(player: Player) -> bool:
    return player.get_kills("Foudro") >= 10
def killed_5_of_each_spatiofarm_monster(player: Player) -> bool:
    spatiofarm_monsters = ["Petalo", "Gloo", "Vaporis", "Foudro"]
    return all(player.get_kills(monster) >= 5 for monster in spatiofarm_monsters)
def killed_10_of_each_spatiofarm_monster(player: Player) -> bool:
    spatiofarm_monsters = ["Petalo", "Gloo", "Vaporis", "Foudro"]
    return all(player.get_kills(monster) >= 10 for monster in spatiofarm_monsters)
def killed_100_spatiofarm_monsters(player: Player) -> bool:
    spatiofarm_monsters = ["Petalo", "Gloo", "Vaporis", "Foudro"]
    return sum(player.get_kills(monster) for monster in spatiofarm_monsters) >= 100

def astropolis_guy(player: Player) -> bool:
    astropolis_monsters = ["Wakashoko", "Hans", "Glimmer"]
    return all(player.get_kills(monster) > 0 for monster in astropolis_monsters)
def killed_10_wakashoko(player: Player) -> bool:
    return player.get_kills("Wakashoko") >= 10
def killed_10_hans(player: Player) -> bool:
    return player.get_kills("Hans") >= 10
def killed_10_glimmer(player: Player) -> bool:
    return player.get_kills("Glimmer") >= 10
def killed_5_of_each_astropolis_monster(player: Player) -> bool:
    astropolis_monsters = ["Wakashoko", "Hans", "Glimmer"]
    return all(player.get_kills(monster) >= 5 for monster in astropolis_monsters)
def killed_10_of_each_astropolis_monster(player: Player) -> bool:
    astropolis_monsters = ["Wakashoko", "Hans", "Glimmer"]
    return all(player.get_kills(monster) >= 10 for monster in astropolis_monsters)
def killed_100_astropolis_monsters(player: Player) -> bool:
    astropolis_monsters = ["Wakashoko", "Hans", "Glimmer"]
    return sum(player.get_kills(monster) for monster in astropolis_monsters) >= 100

def kill_xalith(player: Player) -> bool:
    return player.get_kills("Xa'lith, Roi du Vide") >= 1
def kill_andariel(player: Player) -> bool:
    return player.get_kills("Andariel, l'Éradicateur des Mondes") >= 1
def kill_mephis(player: Player) -> bool:
    return player.get_kills("Mephistofedes, le Fléau Cosmique") >= 1
def poche(player: Player) -> bool:
    return player.gold >= 100
def gobelin(player: Player) -> bool:
    return player.gold >= 1000
def enutrof(player: Player) -> bool:
    return player.gold >= 10000

# affichage des succès
def can_display_gobelin(player: Player) -> bool:
    return player.has_achievement('Poche')
def can_display_enutrof(player: Player) -> bool:
    return player.has_achievement('Gobelin')
def can_display_killed_10_crocus(player: Player) -> bool:
    return player.has_achievement('Meteor Guy')
def can_display_killed_10_lunaris(player: Player) -> bool:
    return player.has_achievement('Meteor Guy')
def can_display_killed_10_eclair(player: Player) -> bool:
    return player.has_achievement('Meteor Guy')
def can_display_killed_10_voltaic(player: Player) -> bool:
    return player.has_achievement('Meteor Guy')
def can_display_killed_5_of_each_meteor_monster(player: Player) -> bool:
    return player.has_achievement('Meteor Guy')
def can_display_killed_10_of_each_meteor_monster(player: Player) -> bool:
    return player.has_achievement('Meteor Amateur')
def can_display_killed_100_meteor_monsters(player: Player) -> bool:
    return player.has_achievement('Meteor Walker')
def can_display_killed_10_petalo(player: Player) -> bool:
    return player.has_achievement('Spatiofarm Guy')
def can_display_killed_10_gloo(player: Player) -> bool:
    return player.has_achievement('Spatiofarm Guy')
def can_display_killed_10_vaporis(player: Player) -> bool:
    return player.has_achievement('Spatiofarm Guy')
def can_display_killed_10_foudro(player: Player) -> bool:
    return player.has_achievement('Spatiofarm Guy')
def can_display_killed_5_of_each_spatiofarm_monster(player: Player) -> bool:
    return player.has_achievement('Spatiofarm Guy')
def can_display_killed_10_of_each_spatiofarm_monster(player: Player) -> bool:
    return player.has_achievement('Spatiofarm Amateur')
def can_display_killed_100_spatiofarm_monsters(player: Player) -> bool:
    return player.has_achievement('Spatiofarm Walker')
def can_display_killed_10_wakashoko(player: Player) -> bool:
    return player.has_achievement('Astropolis Guy')
def can_display_killed_10_hans(player: Player) -> bool:
    return player.has_achievement('Astropolis Guy')
def can_display_killed_10_glimmer(player: Player) -> bool:
    return player.has_achievement('Astropolis Guy')
def can_display_killed_5_of_each_astropolis_monster(player: Player) -> bool:
    return player.has_achievement('Astropolis Guy')
def can_display_killed_10_of_each_astropolis_monster(player: Player) -> bool:
    return player.has_achievement('Astropolis Amateur')
def can_display_killed_100_astropolis_monsters(player: Player) -> bool:
    return player.has_achievement('Astropolis Walker')

def can_display_kill_xalith(player: Player) -> bool:
    return player.has_achievement('Enutrof')
def can_display_kill_andariel(player: Player) -> bool:
    return player.has_achievement('Enutrof')
def can_display_kill_mephis(player: Player) -> bool:
    return player.has_achievement('Enutrof')

# Increase stats pour gerer certains ach
def increase_atk(player: Player, amount: int) -> None:
    player.base_atk += amount
def increase_def(player: Player, amount: int) -> None:
    player.defense += amount
def increase_HP(player: Player, amount: int) -> None:
    player.max_hp += amount

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii.decode()

def print_status(player: Player) -> None:
    print(f"{player.name} HP: {player.calculate_max_hp()}  ATK: {player.calculate_atk()}  Gold: {player.gold}  Level: {player.level}")

def init_shop() -> List[Item]:
    shop_items = [
        # Weapons
        Weapon("Epee meteor", 100, 20),
        Weapon("Lance anti-crocus", 500, 65),
        Weapon("DAWN", 1999, 150),
        Weapon("DUSK", 5000, 300),
        Weapon("Lilith", 15000, 666),
        Weapon("Baby", 1, 6666 ),

        # Armors
        Armor("Capuche du voleur", 300, 10, 50, 'Hat'),
        Armor("Caskapointe", 700, 20, 150, 'Hat'),
        Armor("Solomonk", 1500, 30, 450, 'Hat'),

        Armor("Sandales", 450, 12, 60, 'Boots'),
        Armor("Chaussons Lapins", 1050, 24, 180, 'Boots'),
        Armor("Nova", 2250, 36, 540, 'Boots'),

        Armor("Jambiere en cuivre", 600, 15, 75, 'Pant'),
        Armor("Pantalon ", 1400, 30, 225, 'Pant'),
        Armor("Eternal", 3000, 45, 675, 'Pant'),

        Armor("Cotte de maille", 900, 20, 110, 'Chestplate'),
        Armor("Garde Lune", 2000, 40, 330, 'Chestplate'),
        Armor("Genesis", 3200, 60, 1000, 'Chestplate'),

        # Rings
        Ring("Gelano", 3000, 0.05),
        Ring("Anonano", 10000, 0.08),
        Ring("Dracanneau", 30000, 0.1),

        # Necklace
        Necklace("Gelamu", 1000, 0.1),
        Necklace("Umbra", 7500, 0.25),
        Necklace("Collier Divin", 40000, 0.6),
    ]
    return shop_items

def init_monsters() -> Dict[str, List[Monster]]:

    """Initialize the monsters."""
    # Alien Noob
    alien_noob_1 = Monster("Eclair", 110, 13, 0, 5,xp_reward=25)
    alien_noob_2 = Monster("Crocus", 110, 15, 0, 5,xp_reward=24)
    alien_noob_3 = Monster("Lunaris", 110, 18, 0, 5,xp_reward=26)
    alien_noob_4 = Monster("Voltaic", 90, 25, 0, 5, crit_chance=0.1, crit_damage=1.4,xp_reward=30)

    # Alien ça va
    alien_cava_1 = Monster("Petalo", 450, 30, 10, 25,xp_reward=91)
    alien_cava_2 = Monster("Gloo", 500, 33, 10, 25,xp_reward=89)
    alien_cava_3 = Monster("Vaporis", 600, 40, 10, 25,xp_reward=92)
    alien_cava_4 = Monster("Foudro", 300, 60, 10, 25, crit_chance=0.1, crit_damage=1.4,xp_reward=90)

    # Alien Easy & Normal
    alien_normal_1 = Monster("Wakashoko", 1400, 50, 25, 80,xp_reward=752)
    alien_normal_2 = Monster("Hans", 1600, 60, 25, 80,xp_reward=751)
    alien_normal_3 = Monster("Glimmer", 1300, 70, 25, 80, crit_chance=0.05, crit_damage=1.2,xp_reward=749)

    # Alien Medium & Hard
    alien_medium_1 = Monster("Wis", 2150, 105, 50, 140, crit_chance=0.07, crit_damage=1.4, xp_reward=2301)
    alien_medium_2 = Monster("Gorgalon", 2300, 114, 50, 140, crit_chance=0.07, crit_damage=1.4, xp_reward=2302)
    alien_medium_3 = Monster("Nebulus", 2100, 105, 50, 140, crit_chance=0.07, crit_damage=1.4, xp_reward=2300)

    alien_hard_1 = Monster("Xant'ia", 4000, 150, 75, 200, crit_chance=0.09, crit_damage=1.5, xp_reward=6661)
    alien_hard_2 = Monster("Zephyrus", 4150, 159, 75, 220, crit_chance=0.09, crit_damage=1.5, xp_reward=6666)
    alien_hard_3 = Monster("Aurora", 3900, 150, 75, 200, crit_chance=0.09, crit_damage=1.5, xp_reward=6666)

    # Boss Alien
    alien_boss1 = Monster("Xa'lith, Roi du Vide", 10000, 300, 139, 500, crit_chance=0.15, crit_damage=2.0, xp_reward=15555)
    alien_boss2 = Monster("Mephistofedes, le Fléau Cosmique", 12000, 250, 139, 500, crit_chance=0.15, crit_damage=2.0, xp_reward=15555)
    alien_boss3 = Monster("Andariel, l'Éradicateur des Mondes", 8000, 400, 100, 500, crit_chance=0.25, crit_damage=2.0, xp_reward=15555)
    # Endboss
    alien_master = Monster("??..|§§§|..?!", 35000, 300, 200, 1, crit_chance=0.25, crit_damage=4.0, xp_reward=1)

    return {
        'meteor': [alien_noob_1, alien_noob_2, alien_noob_3, alien_noob_4],  
        'spatiofarm': [alien_cava_1, alien_cava_2, alien_cava_3, alien_cava_4],  
        'astropolis': [alien_normal_1, alien_normal_2, alien_normal_3],
        'stellaris': [alien_medium_1, alien_medium_2, alien_medium_3],
        'xenodrome': [alien_hard_1, alien_hard_2, alien_hard_3],
        'nebulae': [alien_boss2, alien_boss3, alien_boss1],
        'elysium':[alien_master]
    }

def explore_zone(player: Player, monsters: Dict[str, List[Monster]], shop_items: List[Item], zone_requirements: Dict[str, str]) -> None:
    print("zones disponibles : Meteor, Spatiofarm, Astropolis, Stellaris, Xenodrome, Nebulae, Elysium")
    zone_command = input("Enter the name of the zone: ").strip().lower()
    if zone_command in monsters:
        required_achievement = zone_requirements.get(zone_command, None)
        if required_achievement and not player.has_achievement(required_achievement):
            print(f"You need the {required_achievement} achievement to enter {zone_command.capitalize()}!")
            return

        selected_monsters = monsters[zone_command]
        monster = random.choice(selected_monsters)
        original_max_hp = player.max_hp  # Store the original max HP
        player.max_hp = player.calculate_max_hp()  # Update max HP based on equipment
        player.hp = player.max_hp  # Reset current HP to the new max HP
        player.in_battle = True
        while player.hp > 0 and monster.hp > 0:
            player.max_hp = player.calculate_max_hp() # On calcule le max HP du joueur
            # Update battle info
            battle_info = f"\n{'*' * 50}\n"
            battle_info += f"Yikes! A super-scary {monster.name} just popped up out of nowhere in the {zone_command.capitalize()}! （ΟΔΟ；）\n"
            battle_info += f"Check out these stats:\n \n HP: \033[1m{monster.initial_hp}\033[0m *gulp*\nATK: \033[1m{monster.damage}\033[0m *sweats*\n"
            battle_info += f"{'*' * 50}\n"
            # Clear the console
            os.system('cls' if os.name == 'nt' else 'clear')
            # Now print the battle info and the current status
            print(battle_info)
            print(f"Player HP: {player.hp} Monster HP: {monster.hp}")
            player.attack(monster)
            if monster.hp <= 0:
                os.system('cls' if os.name == 'nt' else 'clear')
                player.hp = original_max_hp
                player.max_hp = original_max_hp
                reward = monster.variable_gold_reward
                xp_reward = monster.xp_reward
                player.add_xp(xp_reward)
                print(f"You defeated {monster.name}! You earned {reward} gold. and {xp_reward} xp")
                player.gold += reward
                # Dire au joueur combien d'xp il lui reste pour passer au niveau suivant
                print(f"XP required to up : {Player.xp_requirements[player.level] - player.xp} XP")
                monster.hp = monster.initial_hp
                player.in_battle = False
                # Record the monster kill and check achievements
                player.monster_kills[monster.name] = player.monster_kills.get(monster.name, 0) + 1
                player.check_achievements()
                break
            time.sleep(0.7)  # Delay for one second before the monster attacks
            if player.hp > 0:  # Check if the player is still alive
                monster.attack(player)
            if player.hp <= 0:
                # I want that if the player dies, it clear the console and print the following message:
                print(f"You have been defeated! {monster.name} had {monster.hp} left.")
                player.hp = original_max_hp  # Reset the player's HP to the original max HP
                player.max_hp = original_max_hp  # Reset the player's max HP to the original max HP
                player.in_battle = False
                monster.hp = monster.initial_hp
                break
            time.sleep(0.7)  # Delay for one second before the player attacks again
    else:
        print(f"Zone {zone_command.capitalize()} doesn't exist.")
    if player.hp <= 0:
        return
  
def show_monster_kills(player: Player, monsters: Dict[str, List[Monster]], shop_items: List[Item]) -> None:
    """Display the number of monsters the player has killed."""
    player.print_monster_kills()

def visit_shop(player: Player, monsters: Dict[str, List[Monster]], shop_items: List[Item]) -> None:
    print(f"You have {player.gold} gold.\n")
    print("Shop Items:\n")

    weapon_items = [item for item in shop_items if isinstance(item, Weapon)]
    armor_items = [item for item in shop_items if isinstance(item, Armor)]
    ring_items = [item for item in shop_items if isinstance(item, Ring)]
    necklace_items = [item for item in shop_items if isinstance(item, Necklace)]

    print("="*60)
    print("[Weapons]")
    print("-"*60)
    for item in weapon_items:
        stats = f"Damage: {item.damage}"
        print(f"{item.name:<30} {stats:<20} Value: {item.value} gold")

    armor_types = ["Hat", "Chestplate", "Boots", "Pant"]
    print("\n"+"="*60)
    print("[Armors]")
    for armor_type in armor_types:
        print(f"\n{armor_type}s")
        print("-"*60)
        for item in armor_items:
            if item.slot == armor_type:
                defense_stat = f"Defense: {item.defense}".ljust(20)
                hp_bonus_stat = f"HP: {item.hp_bonus}".ljust(20)
                stats = f"{defense_stat} {hp_bonus_stat}"
                print(f"{item.name:<30} {stats:<40} Value: {item.value} gold")

    print("\n"+"="*60)
    print("[Rings]")
    print("-"*60)
    for item in ring_items:
        stats = f"Crit Chance: {item.crit_chance}"
        print(f"{item.name:<30} {stats:<20} Value: {item.value} gold")

    print("\n"+"="*60)
    print("[Necklaces]")
    print("-"*60)
    for item in necklace_items:
        stats = f"Crit Damage: {item.crit_damage}"
        print(f"{item.name:<30} {stats:<20} Value: {item.value} gold")

def buy_item(player: Player, monsters: Dict[str, List[Monster]], shop_items: List[Item]) -> None:
    item_name = input("Enter the name of the item you want to buy: ").strip().lower()
    item_name = remove_accents(item_name)  # Normalize user input
    if item_name == "":
        print("Please specify the name of the item you want to buy.")
        return
    available_items = [item for item in shop_items if remove_accents(item.name.lower()) == item_name]
    if available_items:
        item = available_items[0]
        if player.gold >= item.value:
            player.gold -= item.value
            if isinstance(item, Weapon):
                new_item = Weapon(item.name, item.value, item.damage)
            elif isinstance(item, Armor):
                new_item = Armor(item.name, item.value, item.defense, item.hp_bonus, item.slot)
            elif isinstance(item, Ring):
                new_item = Ring(item.name, item.value, item.crit_chance)
            elif isinstance(item, Necklace):
                new_item = Necklace(item.name, item.value, item.crit_damage)
            player.inventory.append(new_item)
            print(f"You bought {new_item.name}!")
        else:
            print("You don't have enough gold!")
    else:
        print("The item is not available in the shop.")

def sell_item(player: Player, monsters: Dict[str, List[Monster]], shop_items: List[Item]) -> None:
    item_name = input("Enter the name of the item you want to sell: ").strip().lower()
    item_name = remove_accents(item_name)  # Normalize user input
    player.sell(item_name)

def equip_item(player: Player, monsters: Dict[str, List[Monster]], shop_items: List[Item]) -> None:
    print("You have the following items in your inventory:")
    player.print_inventory()
    item_name = input("Enter the name of the item you want to equip: ")
    item_name = remove_accents(item_name)  # Normalize user input
    player.equip_item(item_name)

def command_stats(player: Player, monsters: Dict[str, List[Monster]], shop_items: List[Item]) -> None:
    player.print_stats()

def command_show_stuff(player: Player, monsters: Dict[str, List[Monster]], shop_items: List[Item]) -> None:
    player.print_equipped_items_stats()
    player.print_inventory()

def error_typing(player: Player, monsters: Dict[str, List[Monster]], shop_items: List[Item]) -> None:
    print("This command doesn't exist. Type 'help' to see the list of available commands.")

# Dictionnaires
zone_requirements = {
        'meteor': None,  # Pas d'exigence pour cette zone
        'spatiofarm': 'Meteor Amateur',  # Nom de l'achievement nécessaire pour accéder à la zone
        'astropolis': 'Spatiofarm Amateur',
        'stellaris': 'Astropolis Amateur',
        'xenodrome': 'Stellaris Amateur',
        'nebulae': 'Xenodrome Amateur', 
}
effect_to_stat = {
    "increase_atk": "Attaque",
    "increase_def": "Défense",
    "increase_HP": "Point de vie"
}
command_functions = {
    "zone": lambda player, monsters, shop_items: explore_zone(player, monsters, shop_items, zone_requirements),
    "shop": visit_shop,
    "monster" : show_monster_kills,
    "succès" : Player.display_achievements,
    "buy": buy_item,
    "sell": sell_item,
    "equip": equip_item,
    "stuff": command_show_stuff,
    "stats": command_stats,
}

def main():
    # Monsters
    monsters = init_monsters()

    # Shop Items
    shop_items = init_shop()

    while True:
        # Player
        player = Player("Roi_Mouuw")
        print(f"Bienvenue! Tu peux écrire Help pour voir les différentes commandes ou directement écrire Zone pour rentrer en combat.")
        player.reset()  # Reset player stats for each new session

        # Achievements
        meteor_ach = Achievement('Meteor Guy', meteor_guy, (20, 150), "Tuer tous les monstres de la zone Meteor au moins une fois.")
        player.add_achievement(meteor_ach)

        crocus_ach = Achievement('Destructeur de Crocus', killed_10_crocus, (50, 250), 'Tuez 10 monstres Crocus.', display_condition=can_display_killed_10_crocus)
        player.add_achievement(crocus_ach)

        lunaris_ach = Achievement('Destructeur de Lunaris', killed_10_lunaris, (50, 250), 'Tuez 10 monstres Lunaris.', display_condition=can_display_killed_10_lunaris)
        player.add_achievement(lunaris_ach)

        eclair_ach = Achievement('Destructeur d\'Eclair', killed_10_eclair, (50, 250), 'Tuez 10 monstres Eclair.', display_condition=can_display_killed_10_eclair)
        player.add_achievement(eclair_ach)

        voltaic_ach = Achievement('Destructeur de Voltaic', killed_10_voltaic, (50, 250), 'Tuez 10 monstres Voltaic.', display_condition=can_display_killed_10_voltaic)
        player.add_achievement(voltaic_ach)

        all_meteor_ach_5 = Achievement('Meteor Amateur', killed_5_of_each_meteor_monster, (100, 600), 'Tuer tous les monstres de la zone Meteor au moins 5 fois.', display_condition=can_display_killed_5_of_each_meteor_monster)
        player.add_achievement(all_meteor_ach_5)

        all_meteor_ach_10 = Achievement('Meteor Walker', killed_10_of_each_meteor_monster, (400, 1500), 'Tuer tous les monstres de la zone Meteor au moins 10 fois.', display_condition=can_display_killed_10_of_each_meteor_monster)
        player.add_achievement(all_meteor_ach_10)

        meteor_100_ach = Achievement('Meteor Slayer', killed_100_meteor_monsters, (500, 2500), 'Tuez 100 monstres de la Zone Meteor.', display_condition=can_display_killed_100_meteor_monsters)
        player.add_achievement(meteor_100_ach)

        spatiofarm_ach = Achievement('Spatiofarm Guy', spatiofarm_guy, (150, 500), "Tuer tous les monstres de la zone Spatiofarm au moins une fois.")
        player.add_achievement(spatiofarm_ach)

        petalo_ach = Achievement('Destructeur de Petalo', killed_10_petalo, (250, 700), 'Tuez 10 monstres Petalo.', display_condition=can_display_killed_10_petalo)
        player.add_achievement(petalo_ach)

        gloo_ach = Achievement('Destructeur de Gloo', killed_10_gloo, (250, 700), 'Tuez 10 monstres Gloo.', display_condition=can_display_killed_10_gloo)
        player.add_achievement(gloo_ach)

        vaporis_ach = Achievement('Destructeur de Vaporis', killed_10_vaporis, (250, 700), 'Tuez 10 monstres Vaporis.', display_condition=can_display_killed_10_vaporis)
        player.add_achievement(vaporis_ach)

        foudro_ach = Achievement('Destructeur de Foudro', killed_10_foudro, (250, 700), 'Tuez 10 monstres Foudro.', display_condition=can_display_killed_10_foudro)
        player.add_achievement(foudro_ach)

        all_spatiofarm_ach_5 = Achievement('Spatiofarm Amateur', killed_5_of_each_spatiofarm_monster, (400, 1800), 'Tuer tous les monstres de la zone Spatiofarm au moins 5 fois.', display_condition=can_display_killed_5_of_each_spatiofarm_monster)
        player.add_achievement(all_spatiofarm_ach_5)

        all_spatiofarm_ach_10 = Achievement('Spatiofarm Walker', killed_10_of_each_spatiofarm_monster, (800, 4500), 'Tuer tous les monstres de la zone Spatiofarm au moins 10 fois.', display_condition=can_display_killed_10_of_each_spatiofarm_monster)
        player.add_achievement(all_spatiofarm_ach_10)

        spatiofarm_100_ach = Achievement('Spatiofarm Slayer', killed_100_spatiofarm_monsters, (1500, 8000), 'Tuez 100 monstres de la Zone Spatiofarm.', display_condition=can_display_killed_100_spatiofarm_monsters)
        player.add_achievement(spatiofarm_100_ach)

        astropolis_ach = Achievement('Astropolis guy', astropolis_guy, (300, 1000), "Tuer tous les monstres de la zone Astropolis au moins une fois.")
        player.add_achievement(astropolis_ach)

        hans_ach = Achievement('Destructeur de Hans', killed_10_hans, (500, 1200), 'Tuez 10 monstres Hans.', display_condition=can_display_killed_10_hans)
        player.add_achievement(hans_ach)

        wakashoko_ach = Achievement('Destructeur de Wakashoko', killed_10_wakashoko, (500, 1200), 'Tuez 10 monstres Wakashoko.', display_condition=can_display_killed_10_wakashoko)
        player.add_achievement(wakashoko_ach)

        glimmer_ach = Achievement('Destructeur de Glimmer', killed_10_glimmer, (500, 1200), 'Tuez 10 monstres Glimmer.', display_condition=can_display_killed_10_glimmer)
        player.add_achievement(glimmer_ach)

        all_astropolis_ach_5 = Achievement('Astropolis Amateur', killed_5_of_each_astropolis_monster, (800, 3000), 'Tuer tous les monstres de la zone Astropolis au moins 5 fois.', display_condition=can_display_killed_5_of_each_astropolis_monster)
        player.add_achievement(all_astropolis_ach_5)

        all_astropolis_ach_10 = Achievement('Astropolis Walker', killed_10_of_each_astropolis_monster, (1600, 6000), 'Tuer tous les monstres de la zone Astropolis au moins 10 fois.', display_condition=can_display_killed_10_of_each_astropolis_monster)
        player.add_achievement(all_astropolis_ach_10)

        astropolis_100_ach = Achievement('Astropolis Slayer', killed_100_astropolis_monsters, (3000, 12000), 'Tuez 100 monstres de la Zone Astropolis.', display_condition=can_display_killed_100_astropolis_monsters)
        player.add_achievement(astropolis_100_ach)

        xalith_ach = Achievement('Xa\'lith Swagger', kill_xalith, (1000, 5000), "Tuez Xa'lith, Roi du Vide.", effect=increase_atk, effect_params=(50,), display_condition=can_display_kill_xalith)
        player.add_achievement(xalith_ach)

        andariel_ach = Achievement('Andariel Swagger', kill_andariel, (1000, 5000), "Tuez, Andariel, l'Éradicateur des Mondes", effect=increase_def, effect_params=(20,), display_condition=can_display_kill_andariel)
        player.add_achievement(andariel_ach)

        mephis_ach = Achievement('Mephistofedes Swagger', kill_mephis, (1000, 5000), "Tuez Mephistofedes, le Fléau Cosmique.", effect=increase_HP, effect_params=(500,), display_condition=can_display_kill_mephis)
        player.add_achievement(mephis_ach)

        gold_achievement1 = Achievement('Poche', poche, (1, 200), 'Possédez au moins 100 pièces d\'or.')
        player.add_achievement(gold_achievement1)

        gold_achievement2 = Achievement('Gobelin', gobelin, (1, 2500), 'Possédez au moins 1000 pièces d\'or.', display_condition=can_display_gobelin)
        player.add_achievement(gold_achievement2)

        gold_achievement3 = Achievement('Enutrof', enutrof, (1, 30000), 'Possédez au moins 10000 pièces d\'or.', display_condition=can_display_enutrof)
        player.add_achievement(gold_achievement3)


        # Game loop 
        while True:
            if not player.in_battle:
                print_status(player)
                command = input("> ").strip().lower()  # strip et lower pour normaliser la commande
                if command == "quit":
                    break
                elif command == "help":
                    player.print_commands()
                elif command == "":
                    print("Can you fucking write something instead of nothing?")
                elif command == "admin" and player.name == "Roi_Mouuw":
                   player.admin_command()
                elif command == "admin":
                    print("Qu'essaies-tu de faire?")
                else:
                    # Exécute la fonction correspondante à la commande, ou la fonction d'erreur si la commande n'est pas reconnue
                    command_function = command_functions.get(command, error_typing)
                    if command == "succès":
                        command_function(player)
                    else:
                        command_function(player, monsters, shop_items)

        # Break the outer loop when the player quits
        if command == "quit":
            break

if __name__ == "__main__":
    main()
