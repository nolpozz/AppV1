import sqlite3

def create_tables():
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT,
                        level TEXT
                      )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS vocabulary (
                        id INTEGER PRIMARY KEY,
                        word TEXT,
                        level TEXT,
                        language TEXT
                      )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS sentences (
                        id INTEGER PRIMARY KEY,
                        sentence TEXT,
                        level TEXT,
                        language TEXT
                      )''')
    
    conn.commit()
    conn.close()

def get_sentence(level, language):
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    
    cursor.execute('''SELECT sentence FROM sentences WHERE level = ? AND language = ?''', (level, language))
    sentences = cursor.fetchall()
    
    conn.close()
    return random.choice(sentences)[0] if sentences else None

def check_translation(user_translation, correct_translation):
    return user_translation.strip().lower() == correct_translation.strip().lower()

if __name__ == '__main__':
    create_tables()
