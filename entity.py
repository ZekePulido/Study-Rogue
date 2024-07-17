import random

class mob:
    def __init__(self, name, hp, damage, hit_rate):
        self.name = name
        self.hp = hp
        self.damage = damage
        self.hit_rate = hit_rate
    
    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
        result = f"{self.name} took {amount} damage."
        print(result)
        return result

    def deal_damage(self):
        if random.random() <= self.hit_rate:
            result = f"{self.name} deals {self.damage} damage!"
            print(result)
            return self.damage
        else:
            result = f"{self.name} misses the attack!"
            print(result)
            return 0
    
    def defend_damage(self, amount):
        blocked = amount - self.damage
        self.hp -= blocked
        if self.hp <= 0:
            self.hp = 0
        result = f"{self.name} blocked {blocked} damage!"
        print(result)
        return result

