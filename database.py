import sqlite3
import random
from datetime import datetime
import hashlib
import os
from werkzeug.security import generate_password_hash, check_password_hash

class DatabaseManager:
    def __init__(self, db_path='language_learning.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize the database with all required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )''')
        
        # Create languages table if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS languages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            code TEXT UNIQUE NOT NULL,
            flag_emoji TEXT
        )''')
        
        # Create user_languages table if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_languages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            language_id INTEGER NOT NULL,
            is_learning BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (language_id) REFERENCES languages (id),
            UNIQUE(user_id, language_id)
        )''')
        
        # Create vocabulary table if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS vocabulary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            language_id INTEGER NOT NULL,
            word TEXT NOT NULL,
            translation TEXT,
            difficulty_level TEXT DEFAULT 'beginner',
            category TEXT,
            part_of_speech TEXT,
            example_sentence TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_reviewed TIMESTAMP,
            review_count INTEGER DEFAULT 0,
            mastery_level INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (language_id) REFERENCES languages (id)
        )''')
        
        # Create sentences table if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS sentences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            language_id INTEGER NOT NULL,
            sentence TEXT NOT NULL,
            translation TEXT,
            difficulty_level TEXT DEFAULT 'beginner',
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used TIMESTAMP,
            use_count INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (language_id) REFERENCES languages (id)
        )''')
        
        # Create learning_sessions table if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS learning_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            language_id INTEGER NOT NULL,
            session_type TEXT NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP,
            words_practiced INTEGER DEFAULT 0,
            sentences_practiced INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0,
            total_questions INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (language_id) REFERENCES languages (id)
        )''')
        
        # Create practice_records table if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS practice_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            vocabulary_id INTEGER,
            sentence_id INTEGER,
            session_id INTEGER NOT NULL,
            user_answer TEXT,
            correct_answer TEXT,
            is_correct BOOLEAN,
            response_time_ms INTEGER,
            practiced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (vocabulary_id) REFERENCES vocabulary (id),
            FOREIGN KEY (sentence_id) REFERENCES sentences (id),
            FOREIGN KEY (session_id) REFERENCES learning_sessions (id)
        )''')
        
        # Insert default languages only if they don't exist
        cursor.execute('SELECT COUNT(*) FROM languages')
        if cursor.fetchone()[0] == 0:
            default_languages = [
                ('Spanish', 'es', '🇪🇸'),
                ('French', 'fr', '🇫🇷'),
                ('German', 'de', '🇩🇪'),
                ('Italian', 'it', '🇮🇹'),
                ('Portuguese', 'pt', '🇵🇹'),
                ('Russian', 'ru', '🇷🇺'),
                ('Japanese', 'ja', '🇯🇵'),
                ('Korean', 'ko', '🇰🇷'),
                ('Chinese (Mandarin)', 'zh', '🇨🇳'),
                ('Arabic', 'ar', '🇸🇦'),
                ('Hindi', 'hi', '🇮🇳'),
                ('Dutch', 'nl', '🇳🇱'),
                ('Swedish', 'sv', '🇸🇪'),
                ('Norwegian', 'no', '🇳🇴'),
                ('Danish', 'da', '🇩🇰')
            ]
            
            for lang_name, lang_code, flag in default_languages:
                cursor.execute('''INSERT INTO languages (name, code, flag_emoji) 
                                 VALUES (?, ?, ?)''', (lang_name, lang_code, flag))
        
        conn.commit()
        conn.close()
    
    def create_user(self, username, email, password):
        """Create a new user account"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = generate_password_hash(password)
            
            # Check if this is an existing user without email
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                # Update existing user with email and password
                cursor.execute('''UPDATE users 
                                 SET email = ?, password_hash = ?, is_active = 1
                                 WHERE username = ?''', (email, password_hash, username))
                user_id = existing_user[0]
            else:
                # Create new user
                cursor.execute('''INSERT INTO users (username, email, password_hash) 
                                 VALUES (?, ?, ?)''', (username, email, password_hash))
                user_id = cursor.lastrowid
            
            conn.commit()
            return user_id
        except sqlite3.IntegrityError as e:
            print(f"Database error: {e}")
            return None
        finally:
            conn.close()
    
    def authenticate_user(self, username, password):
        """Authenticate a user and return user data if successful"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''SELECT id, username, email, password_hash FROM users 
                         WHERE username = ? AND is_active = 1''', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[3], password):
            # Update last login
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''UPDATE users SET last_login = CURRENT_TIMESTAMP 
                             WHERE id = ?''', (user[0],))
            conn.commit()
            conn.close()
            
            return {
                'id': user[0],
                'username': user[1],
                'email': user[2]
            }
        return None
    
    def get_user_by_id(self, user_id):
        """Get user data by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''SELECT id, username, email, created_at, last_login 
                         FROM users WHERE id = ? AND is_active = 1''', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'created_at': user[3],
                'last_login': user[4]
            }
        return None
    
    def get_languages(self):
        """Get all available languages"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''SELECT id, name, code, flag_emoji FROM languages ORDER BY name''')
        languages = cursor.fetchall()
        conn.close()
        
        return [{'id': lang[0], 'name': lang[1], 'code': lang[2], 'flag_emoji': lang[3]} 
                for lang in languages]
    
    def add_user_language(self, user_id, language_id):
        """Add a language to user's learning list"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''INSERT INTO user_languages (user_id, language_id) 
                             VALUES (?, ?)''', (user_id, language_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Language already exists for this user
            return False
        finally:
            conn.close()
    
    def get_user_languages(self, user_id):
        """Get all languages that a user is learning"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''SELECT ul.language_id, l.name, l.code, l.flag_emoji
                         FROM user_languages ul
                         JOIN languages l ON ul.language_id = l.id
                         WHERE ul.user_id = ? AND ul.is_learning = 1''', (user_id,))
        
        languages = []
        for row in cursor.fetchall():
            languages.append({
                'language_id': row[0],
                'name': row[1],
                'code': row[2],
                'flag_emoji': row[3]
            })
        
        conn.close()
        return languages
    
    def add_vocabulary(self, user_id, language_id, word, translation=None, 
                      difficulty_level='beginner', category=None, part_of_speech=None, 
                      example_sentence=None):
        """Add vocabulary for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''INSERT INTO vocabulary 
                         (user_id, language_id, word, translation, difficulty_level, 
                          category, part_of_speech, example_sentence)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (user_id, language_id, word, translation, difficulty_level,
                       category, part_of_speech, example_sentence))
        vocab_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return vocab_id
    
    def get_user_vocabulary(self, user_id, language_id=None, difficulty_level=None, limit=50):
        """Get vocabulary for a user with optional filters"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''SELECT id, word, translation, difficulty_level, category, 
                          part_of_speech, example_sentence, mastery_level, review_count
                   FROM vocabulary 
                   WHERE user_id = ? AND is_active = 1'''
        params = [user_id]
        
        if language_id:
            query += ' AND language_id = ?'
            params.append(language_id)
        
        if difficulty_level:
            query += ' AND difficulty_level = ?'
            params.append(difficulty_level)
        
        query += ' ORDER BY mastery_level ASC, review_count ASC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        vocabulary = cursor.fetchall()
        conn.close()
        
        return [{'id': vocab[0], 'word': vocab[1], 'translation': vocab[2],
                'difficulty_level': vocab[3], 'category': vocab[4],
                'part_of_speech': vocab[5], 'example_sentence': vocab[6],
                'mastery_level': vocab[7], 'review_count': vocab[8]}
                for vocab in vocabulary]
    
    def add_sentence(self, user_id, language_id, sentence, translation=None,
                    difficulty_level='beginner', category=None):
        """Add a sentence for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''INSERT INTO sentences 
                         (user_id, language_id, sentence, translation, difficulty_level, category)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (user_id, language_id, sentence, translation, difficulty_level, category))
        sentence_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return sentence_id
    
    def get_user_sentences(self, user_id, language_id=None, difficulty_level=None, limit=50):
        """Get sentences for a user with optional filters"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''SELECT id, sentence, translation, difficulty_level, category, use_count
                   FROM sentences 
                   WHERE user_id = ? AND is_active = 1'''
        params = [user_id]
        
        if language_id:
            query += ' AND language_id = ?'
            params.append(language_id)
        
        if difficulty_level:
            query += ' AND difficulty_level = ?'
            params.append(difficulty_level)
        
        query += ' ORDER BY use_count ASC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        sentences = cursor.fetchall()
        conn.close()
        
        return [{'id': sent[0], 'sentence': sent[1], 'translation': sent[2],
                'difficulty_level': sent[3], 'category': sent[4], 'use_count': sent[5]}
                for sent in sentences]
    
    def get_random_sentence(self, user_id, language_id, difficulty_level=None):
        """Get a random sentence for practice"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''SELECT id, sentence, translation, difficulty_level, category
                   FROM sentences 
                   WHERE user_id = ? AND language_id = ? AND is_active = 1'''
        params = [user_id, language_id]
        
        if difficulty_level:
            query += ' AND difficulty_level = ?'
            params.append(difficulty_level)
        
        query += ' ORDER BY RANDOM() LIMIT 1'
        
        cursor.execute(query, params)
        sentence = cursor.fetchone()
        conn.close()
        
        if sentence:
            return {'id': sentence[0], 'sentence': sentence[1], 'translation': sentence[2],
                    'difficulty_level': sentence[3], 'category': sentence[4]}
        return None
    
    def get_random_vocabulary(self, user_id, language_id, difficulty_level=None, limit=10):
        """Get random vocabulary for practice"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''SELECT id, word, translation, difficulty_level, category, mastery_level
                   FROM vocabulary 
                   WHERE user_id = ? AND language_id = ? AND is_active = 1'''
        params = [user_id, language_id]
        
        if difficulty_level:
            query += ' AND difficulty_level = ?'
            params.append(difficulty_level)
        
        query += ' ORDER BY mastery_level ASC, RANDOM() LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        vocabulary = cursor.fetchall()
        conn.close()
        
        return [{'id': vocab[0], 'word': vocab[1], 'translation': vocab[2],
                'difficulty_level': vocab[3], 'category': vocab[4], 'mastery_level': vocab[5]}
                for vocab in vocabulary]
    
    def start_learning_session(self, user_id, language_id, session_type):
        """Start a new learning session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''INSERT INTO learning_sessions 
                         (user_id, language_id, session_type)
                         VALUES (?, ?, ?)''', (user_id, language_id, session_type))
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return session_id
    
    def end_learning_session(self, session_id, words_practiced=0, sentences_practiced=0,
                           correct_answers=0, total_questions=0):
        """End a learning session with statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''UPDATE learning_sessions 
                         SET ended_at = CURRENT_TIMESTAMP,
                             words_practiced = ?, sentences_practiced = ?,
                             correct_answers = ?, total_questions = ?
                         WHERE id = ?''', 
                      (words_practiced, sentences_practiced, correct_answers, 
                       total_questions, session_id))
        conn.commit()
        conn.close()
    
    def record_practice(self, user_id, session_id, vocabulary_id=None, sentence_id=None,
                       user_answer=None, correct_answer=None, is_correct=None, response_time_ms=None):
        """Record a practice attempt"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''INSERT INTO practice_records 
                         (user_id, session_id, vocabulary_id, sentence_id, user_answer,
                          correct_answer, is_correct, response_time_ms)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (user_id, session_id, vocabulary_id, sentence_id, user_answer,
                       correct_answer, is_correct, response_time_ms))
        
        # Update vocabulary mastery if applicable
        if vocabulary_id and is_correct is not None:
            if is_correct:
                cursor.execute('''UPDATE vocabulary 
                                 SET mastery_level = mastery_level + 1,
                                     review_count = review_count + 1,
                                     last_reviewed = CURRENT_TIMESTAMP
                                 WHERE id = ?''', (vocabulary_id,))
            else:
                cursor.execute('''UPDATE vocabulary 
                                 SET mastery_level = MAX(0, mastery_level - 1),
                                     review_count = review_count + 1,
                                     last_reviewed = CURRENT_TIMESTAMP
                                 WHERE id = ?''', (vocabulary_id,))
        
        # Update sentence use count if applicable
        if sentence_id:
            cursor.execute('''UPDATE sentences 
                             SET use_count = use_count + 1,
                                 last_used = CURRENT_TIMESTAMP
                             WHERE id = ?''', (sentence_id,))
        
        conn.commit()
        conn.close()
    
    def get_user_stats(self, user_id, language_id=None):
        """Get learning statistics for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get vocabulary stats
        vocab_query = '''SELECT COUNT(*) as total, 
                               SUM(CASE WHEN mastery_level >= 5 THEN 1 ELSE 0 END) as mastered,
                               AVG(mastery_level) as avg_mastery
                        FROM vocabulary 
                        WHERE user_id = ? AND is_active = 1'''
        vocab_params = [user_id]
        
        if language_id:
            vocab_query += ' AND language_id = ?'
            vocab_params.append(language_id)
        
        cursor.execute(vocab_query, vocab_params)
        vocab_stats = cursor.fetchone()
        
        # Get session stats
        session_query = '''SELECT COUNT(*) as total_sessions,
                                 SUM(correct_answers) as total_correct,
                                 SUM(total_questions) as total_questions,
                                 AVG(correct_answers * 100.0 / total_questions) as avg_accuracy
                          FROM learning_sessions 
                          WHERE user_id = ? AND ended_at IS NOT NULL'''
        session_params = [user_id]
        
        if language_id:
            session_query += ' AND language_id = ?'
            session_params.append(language_id)
        
        cursor.execute(session_query, session_params)
        session_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            'vocabulary': {
                'total': vocab_stats[0] or 0,
                'mastered': vocab_stats[1] or 0,
                'avg_mastery': round(vocab_stats[2] or 0, 2)
            },
            'sessions': {
                'total': session_stats[0] or 0,
                'total_correct': session_stats[1] or 0,
                'total_questions': session_stats[2] or 0,
                'avg_accuracy': round(session_stats[3] or 0, 2)
            }
        }

    def migrate_existing_data(self):
        """Migrate existing data to new schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get default language ID (Spanish)
            cursor.execute('SELECT id FROM languages WHERE name = ?', ('Spanish',))
            default_lang = cursor.fetchone()
            default_lang_id = default_lang[0] if default_lang else 1
            
            # Update existing vocabulary to have user_id and language_id
            cursor.execute('''UPDATE vocabulary 
                             SET user_id = 1, language_id = ?
                             WHERE user_id IS NULL OR language_id IS NULL''', (default_lang_id,))
            
            # Update existing sentences to have user_id and language_id
            cursor.execute('''UPDATE sentences 
                             SET user_id = 1, language_id = ?
                             WHERE user_id IS NULL OR language_id IS NULL''', (default_lang_id,))
            
            # Create default user if it doesn't exist
            cursor.execute('SELECT id FROM users WHERE username = ?', ('default_user',))
            default_user = cursor.fetchone()
            
            if not default_user:
                cursor.execute('''INSERT INTO users (username, email, password_hash, is_active)
                                 VALUES (?, ?, ?, ?)''', 
                              ('default_user', 'default@example.com', 
                               generate_password_hash('password'), 1))
            
            conn.commit()
            print("Data migration completed successfully")
            
        except Exception as e:
            print(f"Migration error: {e}")
            conn.rollback()
        finally:
            conn.close()

# Global database instance
db = DatabaseManager()
