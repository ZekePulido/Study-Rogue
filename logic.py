import entity

def setup():
    goblin = entity.mob("Goblin", 50, 10, 0.55)
    dragon = entity.mob("Dragon", 200, 50, 0.9)
    user = entity.mob("User", 100, 15, 0.75)
    return goblin, dragon, user

goblin, dragon, user = setup()

while True:
    choice = int(input("""
    You have three options:
      1: Attack
      2: Defend
      3: Heal
    Choose an option: """))
    
    if choice == 1:
        damage = user.deal_damage()
        goblin.take_damage(damage)
        if goblin.hp == 0:
            print("You defeated the Goblin!")
            break
        else:
            damage = goblin.deal_damage()
            user.take_damage(damage)
    elif choice == 2:
        damage = goblin.deal_damage()
        user.defend_damage(damage)
        
    elif choice == 3:
        user.heal_damage()
        damage = goblin.deal_damage()
        user.take_damage(damage)
    else:
        print("Invalid choice. Please choose 1, 2, or 3.")

    if user.hp == 0:
        print("You were defeated by the Goblin!")
        break
