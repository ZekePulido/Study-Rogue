from flask import Flask, render_template, request, g, redirect, url_for
import sqlite3
import random

app = Flask(__name__)

DATABASE = 'StudyRogue.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

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

@app.route('/type-selected', methods=['GET'])
def tag_selected():
    tag_type = request.args.get('type', default='TrueFalse', type=str)
    db = get_db()
    cursor = db.cursor()
    query = "SELECT id, type, question, answer, tag FROM Terms WHERE type = ?;"
    cursor.execute(query, (tag_type,))
    cards = cursor.fetchall()
    return render_template('insert.html', cards=cards)

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, type, question, answer, tag FROM Terms;")
    cards = cursor.fetchall()
    return render_template('insert.html', cards=cards)

@app.route('/insert_data', methods=['POST'])
def insert_data():
    try:
        db = get_db()
        cursor = db.cursor()

        entry_type = request.form['type']
        
        if entry_type == 'TrueFalse':
            question = request.form.get('questionTF')
            answer = request.form.get('answerTF')
            tag = request.form.get('tagTF')
            if question and answer and tag:
                cursor.execute("INSERT INTO Terms (type, question, answer, tag) VALUES (?, ?, ?, ?);", (entry_type, question, answer, tag))
        elif entry_type == 'TermDefinition':
            question = request.form.get('questionTD')
            answer = request.form.get('answerTD')
            tag = request.form.get('tagTD')
            if question and answer and tag:
                cursor.execute("INSERT INTO Terms (type, question, answer, tag) VALUES (?, ?, ?, ?);", (entry_type, question, answer, tag))
        elif entry_type == 'Math':
            question = request.form.get('questionM')
            answer = request.form.get('answerM')
            tag = request.form.get('tagM')
            if question and answer and tag:
                cursor.execute("INSERT INTO Terms (type, question, answer, tag) VALUES (?, ?, ?, ?);", (entry_type, question, answer, tag))

        db.commit()
        return redirect(url_for('index'))
    except sqlite3.Error as e:
        db.rollback()
        return "Database error: " + str(e), 500
    finally:
        cursor.close()

@app.route('/edit_card/<int:id>', methods=['GET', 'POST'])
def edit_card(id):
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        print(request.form)  # Debugging line
        entry_type = request.form['type']

        if entry_type == 'TrueFalse':
            question = request.form.get('questionTF')
            answer = request.form.get('answerTF')
            tag = request.form.get('tagTF')
            cursor.execute("UPDATE Terms SET question = ?, answer = ?, tag = ? WHERE id = ?;", (question, answer, tag, id))
        elif entry_type == 'TermDefinition':
            question = request.form.get('questionTD')
            answer = request.form.get('answerTD')
            tag = request.form.get('tagTD')
            cursor.execute("UPDATE Terms SET question = ?, answer = ?, tag = ? WHERE id = ?;", (question, answer, tag, id))
        elif entry_type == 'Math':
            question = request.form.get('questionM')
            answer = request.form.get('answerM')
            tag = request.form.get('tagM')
            cursor.execute("UPDATE Terms SET question = ?, answer = ?, tag = ? WHERE id = ?;", (question, answer, tag, id))

        db.commit()
        return redirect(url_for('index'))

    cursor.execute("SELECT id, type, question, answer, tag FROM Terms WHERE id = ?;", (id,))
    card = cursor.fetchone()
    return render_template('edit.html', card=card)


@app.route('/confirm_delete/<int:id>', methods=['GET'])
def confirm_delete(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Terms WHERE id = ?", (id,))
    card = cursor.fetchone()
    db.close()
    return render_template('delete.html', card=card)

@app.route('/delete_card/<int:id>', methods=['POST'])
def delete_card(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Terms WHERE id = ?", (id,))
    db.commit()
    db.close()
    return redirect(url_for('index'))

@app.route('/gameView/')
def gameView():
    return render_template('gameView.html')


@app.route('/cancel')
def cancel():
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        create_table()
    app.run(debug=True)
