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
    query = "SELECT id, type, question, answer, term, definition, tag FROM Terms WHERE type = ?;"
    cursor.execute(query, (tag_type,))
    cards = cursor.fetchall()
    return render_template('insert.html', cards=cards)



@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, type, question, answer, term, definition, tag FROM Terms;")
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
            term = request.form.get('term')
            definition = request.form.get('definition')
            tag = request.form.get('tagTD')
            if term and definition and tag:
                cursor.execute("INSERT INTO Terms (type, term, definition, tag) VALUES (?, ?, ?, ?);", (entry_type, term, definition, tag))
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
            term = request.form.get('term')
            definition = request.form.get('definition')
            tag = request.form.get('tagTD')
            cursor.execute("UPDATE Terms SET term = ?, definition = ?, tag = ? WHERE id = ?;", (term, definition, tag, id))
        elif entry_type == 'Math':
            question = request.form.get('questionM')
            answer = request.form.get('answerM')
            tag = request.form.get('tagM')
            cursor.execute("UPDATE Terms SET question = ?, answer = ?, tag = ? WHERE id = ?;", (question, answer, tag, id))

        db.commit()
        return redirect(url_for('index'))

    cursor.execute("SELECT id, type, question, answer, term, definition, tag FROM Terms WHERE id = ?;", (id,))
    card = cursor.fetchone()
    return render_template('edit.html', card=card)


if __name__ == '__main__':
    app.run(debug=True)
