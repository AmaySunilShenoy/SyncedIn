from flask import g,current_app
import sqlite3


def create_table(db):
    db = sqlite3.connect(current_app.config['DATABASE'])
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            firstname TEXT,
            lastname TEXT,
            username TEXT,
            email TEXT,
            password TEXT,
            profile_picture TEXT,
            is_admin INTEGER DEFAULT 0
        );          
    ''')
    db.commit()
    cursor.close()
    db.close()

def auth(username, password):
    db = sqlite3.connect(current_app.config['DATABASE'])
    cursor = db.cursor()
    cursor.execute(f'''
        SELECT id, is_admin FROM users WHERE username = ? AND password = ?
    ''', (username, password))
    data = cursor.fetchone()
    db.commit()
    cursor.close()
    db.close()
    return data

def add_user(firstname, lastname, username,email,password,profile_picture, is_admin=0):
    db = sqlite3.connect(current_app.config['DATABASE'])
    cursor = db.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (firstname, lastname, username,email,password,profile_picture,is_admin) VALUES (?,?,?,?,?,?,?); 
    ''', (firstname, lastname, username,email,password,profile_picture,is_admin))
        db.commit()
        return auth(username, password)
    except:
        return False
    finally:
        cursor.close()
        db.close()
    
def get_by_id(id):
    db = sqlite3.connect(current_app.config['DATABASE'])
    cursor = db.cursor()
    cursor.execute('''
            SELECT * FROM users where id = ?
''', (id,))
    data = cursor.fetchone()
    db.commit()
    cursor.close()
    db.close()
    return data


def existing_data(column):
    db = sqlite3.connect(current_app.config['DATABASE'])
    cursor = db.cursor()
    cursor.execute(f'''
        SELECT {column} FROM users
''')
    data = cursor.fetchall()
    db.commit
    existing = [el[0] for el in data]
    cursor.close()
    db.close()
