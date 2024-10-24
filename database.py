import sqlite3
import random
from datetime import datetime

def create_tables():
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()

    # Drop the existing vocabulary table (if necessary)
    cursor.execute('''DROP TABLE IF EXISTS vocabulary''')
    # Drop the existing vocabulary table (if necessary)
    cursor.execute('''DROP TABLE IF EXISTS users''')
    # Drop the existing vocabulary table (if necessary)
    cursor.execute('''DROP TABLE IF EXISTS sentences''')

    
    # Create the users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT,
                        level TEXT
                      )''')
    
    # Create the vocabulary table
    cursor.execute('''CREATE TABLE IF NOT EXISTS vocabulary (
                        id INTEGER PRIMARY KEY,
                        word TEXT,
                        level TEXT,
                        language TEXT,
                        seen INTEGER DEFAULT 0,
                        last_seen TIMESTAMP
                      )''')
    
    # Create the sentences table with an additional column for seen status
    cursor.execute('''CREATE TABLE IF NOT EXISTS sentences (
                        id INTEGER PRIMARY KEY,
                        sentence TEXT,
                        level TEXT,
                        language TEXT,
                        seen INTEGER DEFAULT 0,  -- 0 means not seen, 1 means seen
                        last_seen TIMESTAMP      -- Timestamp for when the sentence was last seen
                      )''')
    
    conn.commit()
    conn.close()

def add_sentences(language, level, sentences):
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()

    if isinstance(sentences, str):
        sentences = [sentences]  # Convert to a list if it's a single string

    # Insert each sentence into the database
    for sentence in sentences:
        cursor.execute('''INSERT INTO sentences (sentence, level, language, seen)
                          VALUES (?, ?, ?, 0)''', (sentence, level, language))
    
    conn.commit()
    conn.close()

def store_words(language, level, words):
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()

    for word in words:
        cursor.execute('''INSERT INTO vocabulary (word, level, language, seen)
                          VALUES (?, ?, ?, 0)''', (word, level, language))
    
    conn.commit()
    conn.close()

def get_vocab(language, level):
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    
    # Select sentences that haven't been seen yet
    cursor.execute('''SELECT id, word FROM vocabulary
                      WHERE level = ? AND language = ? AND seen = 0
                      ORDER BY RANDOM() LIMIT 1''', (level, language))
    result = []
    for _ in range(10):
        res = cursor.fetchone()
        
        if res:
            sentence_id, sentence = res
            result.append(sentence)
            
            # Mark the sentence as seen and update the timestamp
            cursor.execute('''UPDATE vocabulary
                            SET seen = 1, last_seen = ?
                            WHERE id = ?''', (datetime.now(), sentence_id))
            
        else:
            break
    
    conn.commit()
    conn.close()

    return result if result else None

def get_sentence(language, level):
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    
    # Select sentences that haven't been seen yet
    cursor.execute('''SELECT id, sentence FROM sentences
                      WHERE level = ? AND language = ? AND seen = 0
                      ORDER BY RANDOM() LIMIT 1''', (level, language))
    
    result = cursor.fetchone()
    
    if result:
        sentence_id, sentence = result
        
        # Mark the sentence as seen and update the timestamp
        cursor.execute('''UPDATE sentences
                          SET seen = 1, last_seen = ?
                          WHERE id = ?''', (datetime.now(), sentence_id))
        
        conn.commit()
        conn.close()
        return sentence
    else:
        conn.close()
        return None

def check_translation(user_translation, correct_translation):
    return user_translation.strip().lower() == correct_translation.strip().lower()

if __name__ == '__main__':
    create_tables()
