
from flask import Flask, request, render_template, g
import sqlite3
from datetime import datetime

app = Flask(__name__)
DATABASE = 'urls.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS urls (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT NOT NULL,
                        author TEXT NOT NULL,
                        access_count INTEGER NOT NULL,
                        password TEXT,
                        created_at DATETIME NOT NULL
                    );''')
        db.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()
    if request.method == 'POST':
        url = request.form['url']
        author = request.form['author']
        access_count = request.form['access_count']
        password = request.form.get('password')
        created_at = datetime.now()

        db.execute('INSERT INTO urls (url, author, access_count, password, created_at) VALUES (?, ?, ?, ?, ?)',
                   (url, author, access_count, password, created_at))
        db.commit()

    urls = db.execute('SELECT * FROM urls').fetchall()
    return render_template('index.html', urls=urls)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
