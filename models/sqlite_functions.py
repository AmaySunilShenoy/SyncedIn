from flask import g
import sqlite3


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('users.db')
        create_table(db)
    return db

def create_table(db):
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            email TEXT,
            password TEXT,
            profile_picture TEXT
        );          
    ''')
    db.commit()

def auth(username, password):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f'''
        SELECT id FROM users WHERE username = ? AND password = ?
    ''', (username, password))
    data = cursor.fetchone()
    db.commit()
    return data

def add_user(username,email,password,profile_picture):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (username,email,password,profile_picture) VALUES (?,?,?,?); 
    ''', (username,email,password,profile_picture))
        db.commit()
        return True
    except:
        return False
    
def get_by_id(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
            SELECT * FROM users where id = ?
''', (id,))
    data = cursor.fetchone()
    db.commit()
    return data


def existing_data(column):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f'''
        SELECT {column} FROM users
''')
    data = cursor.fetchall()
    db.commit
    existing = [el[0] for el in data]
    return existing
