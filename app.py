from flask import Flask, render_template, request, g, redirect, url_for, session
import sqlite3
import random
import entity
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

DATABASE = 'StudyRogue.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Terms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            question TEXT,
            answer TEXT,
            tag TEXT NOT NULL
        );
    ''')
    db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/start_game', methods= ['POST'])
def start_game():
    session.clear()

    # Initialize session variables
    session['monsters'] = [
        {"name": "Goblin", "hp": 50, "damage": 10, "hit_rate": 0.6},
        {"name": "Orc", "hp": 80, "damage": 15, "hit_rate": 0.7},
        {"name": "Dragon", "hp": 150, "damage": 25, "hit_rate": 0.8}
    ]
    session['current_monster'] = 0
    session['user'] = {"name": "User", "hp": 100, "damage": 15, "hit_rate": 0.75}

    # Initialize game mechanics related variables
    session['correct_answers'] = 0
    session['remaining_actions'] = 0
    session['questions_answered'] = 0
    session['combat_log'] = []

    # Initialize terms for questions
    session['terms'] = get_terms('s')
    session['current_term_index'] = 0

    return redirect(url_for('gameView'))


@app.route('/gameView/', methods=['GET', 'POST'])
def gameView():
    if 'monsters' not in session or 'current_monster' not in session:
        return redirect(url_for('start_game'))

    monsters = session['monsters']
    current_monster_index = session['current_monster']

    if current_monster_index >= len(monsters):
        return redirect(url_for('game_end'))

    monster = monsters[current_monster_index]

    monster_sprites = {
        "Goblin": "goblin.png",
        "Dragon": "dragon.png",
        "Orc": "orc.png",
        # Add more mappings as needed
    }

     # Determine the sprite filename based on monster name
    monster_name = monster.get('name', 'Unknown')  # Access name from dictionary
    sprite_filename = monster_sprites.get(monster_name, "default_monster.png")

    if 'user' not in session:
        session['user'] = {"name": "User", "hp": 100, "damage": 15, "hit_rate": 0.75}
        session['correct_answers'] = 0
        session['remaining_actions'] = 0
        session['questions_answered'] = 0

    if 'terms' not in session or 'current_term_index' not in session:
        session['terms'] = get_terms('s')  # Load initial terms
        session['current_term_index'] = 0

    terms = session['terms']
    current_term_index = session['current_term_index']


    # Ensure current_term_index is valid
    if current_term_index >= len(terms):
        session['terms'] = get_terms('s')  # Reload terms if index is out of range
        session['current_term_index'] = 0
        current_term_index = 0
    else:
        session['current_term_index'] = current_term_index

    # Fetch the current term for display
    current_term = terms[current_term_index] if terms else None

    combat_log = session.get('combat_log', [])

    feedback_message = ""
    feedback_class = ""

    if request.method == 'POST':
        user_answer = request.form.get('user_answer', '').strip().lower()
        correct_answer = current_term['answer'].strip().lower()

        if user_answer == correct_answer:
            feedback_message = "Correct!"
            feedback_class = "correct"
            session['correct_answers'] += 1
        else:
            feedback_message = f"Incorrect, the correct answer is {correct_answer}"
            feedback_class = "incorrect"

        session['questions_answered'] += 1

        # Move to the next question
        current_term_index += 1

        if current_term_index >= len(terms):
            # Reload terms and reset index if out of range
            session['terms'] = get_terms('s')
            current_term_index = 0

        session['current_term_index'] = current_term_index

        # Check if 5 questions have been answered
        if session['questions_answered'] >= 5:
            session['remaining_actions'] = session['correct_answers']
            session['questions_answered'] = 0
            session['correct_answers'] = 0

    # Debug output to trace issue
    print(f"Current Term Index: {current_term_index}")
    print(f"Current Term: {current_term}")

    # Fetch the current term for rendering
    current_term = terms[session['current_term_index']] if terms else None

    return render_template('gameView.html',
                           monster=monster,
                           monster_sprite = sprite_filename,
                           user=session['user'],
                           combat_log=combat_log,
                           current_term=current_term,
                           feedback_message=feedback_message,
                           feedback_class=feedback_class,
                           correct_answers=session['correct_answers'],
                           remaining_actions=session['remaining_actions'])




@app.route('/attack')
def attack():
    if 'user' not in session or 'monsters' not in session or 'current_monster' not in session:
        return redirect(url_for('gameView'))

    if session['remaining_actions'] <= 0:
        return redirect(url_for('gameView'))

    user_data = session['user']
    monsters = session['monsters']
    current_monster_index = session['current_monster']
    monster_data = monsters[current_monster_index]

    user = entity.mob(user_data['name'], user_data['hp'], user_data['damage'], user_data['hit_rate'])
    monster = entity.mob(monster_data['name'], monster_data['hp'], monster_data['damage'], monster_data['hit_rate'])

    damage_dealt = user.deal_damage()
    result = monster.take_damage(damage_dealt)
    session['remaining_actions'] -= 1

    combat_log = session.get('combat_log', [])
    combat_log.append(f"{user.name} attacked! {result}")

    if session['remaining_actions'] == 0:
        # Monster attacks automatically
        damage_from_monster = monster.deal_damage()
        reduced_damage = int(damage_from_monster * (1 - (user.defense_stack / 100)))
        result = user.take_damage(reduced_damage)
        combat_log.append(f"{monster.name} attacks! {result}")
        user.defense_stack = 0

    session['user'] = user.__dict__
    monsters[current_monster_index] = monster.__dict__
    session['monsters'] = monsters
    session['combat_log'] = combat_log

    if monster.hp <= 0:
        combat_log.append(f"{monster.name} has been defeated!")
        session['current_monster'] += 1

        if session['current_monster'] >= len(monsters):
            return redirect(url_for('game_end'))

        session['remaining_actions'] = 5  # Reset actions for the next monster

    return redirect(url_for('gameView'))

@app.route('/defend')
def defend():
    if 'user' not in session or 'monsters' not in session or 'current_monster' not in session:
        return redirect(url_for('gameView'))

    if session['remaining_actions'] <= 0:
        return redirect(url_for('gameView'))

    user_data = session['user']
    monsters = session['monsters']
    current_monster_index = session['current_monster']
    monster_data = monsters[current_monster_index]

    user = entity.mob(user_data['name'], user_data['hp'], user_data['damage'], user_data['hit_rate'])
    monster = entity.mob(monster_data['name'], monster_data['hp'], monster_data['damage'], monster_data['hit_rate'])

    user.stack_defense()
    session['remaining_actions'] -= 1

    combat_log = session.get('combat_log', [])
    combat_log.append(f"{user.name} used defend. {user.defense_stack} defense stacked!")

    if session['remaining_actions'] == 0:
        # Monster attacks automatically
        damage_from_monster = monster.deal_damage()
        reduced_damage = int(damage_from_monster * (1 - (user.defense_stack / 100)))
        result = user.take_damage(reduced_damage)
        combat_log.append(f"{monster.name} attacks! {result}")
        user.defense_stack = 0

    session['user'] = user.__dict__
    monsters[current_monster_index] = monster.__dict__
    session['monsters'] = monsters
    session['combat_log'] = combat_log

    if user.hp <= 0:
        combat_log.append("You have been defeated!")
        session.clear()

    return redirect(url_for('gameView'))


def get_terms(tag):
    db = get_db()
    cursor = db.cursor()

    query = '''
    SELECT * FROM Terms WHERE tag = ? ORDER BY RANDOM() LIMIT 5;
    '''
    cursor.execute(query, (tag,))

    terms = cursor.fetchall()

    terms_dict = [dict(term) for term in terms]

    db.close()

    return terms_dict

@app.route('/game_end')
def game_end():
    return render_template('gameEnd.html')

if __name__ == '__main__':
    create_table()
    app.run(debug=True)
