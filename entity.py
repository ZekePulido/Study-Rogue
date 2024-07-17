import random

class Mob:
    def __init__(self, name, hp, damage, hit_rate):
        self.name = name
        self.hp = hp
        self.damage = damage
        self.hit_rate = hit_rate
    
    def take_damage(self, amount):
        if self.hp > 0:
            self.hp -= amount
            if self.hp < 0:
                self.hp = 0
            result = f"{self.name} took {amount} damage. Current HP: {self.hp}."
            print(result)
            return result
        else:
            return f"{self.name} is already defeated."

    def deal_damage(self):
        if self.hp > 0:
            if random.random() <= self.hit_rate:
                result = f"{self.name} strikes and deals {self.damage} damage!"
                print(result)
                return self.damage
            else:
                result = f"{self.name} swings and misses the attack!"
                print(result)
                return 0
        else:
            return f"{self.name} is unable to attack because it is defeated."
    
    def defend_damage(self, amount):
        if self.hp > 0:
            blocked = min(amount, self.damage)
            actual_damage = amount - blocked
            self.hp -= actual_damage
            
            if self.hp < 0:
                self.hp = 0
            
            result = f"{self.name} blocks {blocked} damage and takes {actual_damage} damage. Current HP: {self.hp}."
            print(result)
            return result
        else:
            return f"{self.name} is already defeated."
