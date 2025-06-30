import os
import re
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, DatabaseManager
from openai import OpenAI
from dotenv import load_dotenv
import json
from datetime import datetime
import time

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Development cache for faster iteration
class DevCache:
    def __init__(self):
        self.cache = {}
    
    def get(self, key, default=None):
        return self.cache.get(key, default)
    
    def set(self, key, value):
        self.cache[key] = value
    
    def clear(self):
        self.cache.clear()

# Global development cache instance
dev_cache = DevCache()

# Check if we're in development mode
DEV_MODE = os.getenv('FLASK_ENV') == 'development' or os.getenv('DEV_MODE') == 'true'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.username = user_data['username']
        self.email = user_data['email']

@login_manager.user_loader
def load_user(user_id):
    user_data = db.get_user_by_id(int(user_id))
    if user_data:
        return User(user_data)
    return None

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle JSON data from frontend
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            # Fallback for form data
            username = request.form.get('username')
            password = request.form.get('password')
        
        user_data = db.authenticate_user(username, password)
        if user_data:
            user = User(user_data)
            login_user(user)
            return jsonify({'success': True, 'redirect': url_for('dashboard')})
        else:
            return jsonify({'success': False, 'error': 'Invalid username or password'})
    
    return render_template('login.html')

# Development helper - create a test user if none exists
def ensure_dev_user():
    """Create a development user if none exists"""
    if not DEV_MODE:
        return
    
    # Check if any users exist
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    conn.close()
    
    if user_count == 0:
        # Create a default development user
        try:
            db.create_user('dev', 'dev@example.com', 'password123')
            print("✅ Created development user: dev/password123")
        except Exception as e:
            print(f"⚠️ Could not create development user: {e}")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return jsonify({'success': False, 'error': 'All fields are required'})
        
        user_id = db.create_user(username, email, password)
        if user_id:
            return jsonify({'success': True, 'message': 'Account created successfully! Please log in.'})
        else:
            return jsonify({'success': False, 'error': 'Username or email already exists'})
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_languages = db.get_user_languages(current_user.id)
    stats = db.get_user_stats(current_user.id)
    return render_template('dashboard.html', 
                         user=current_user, 
                         languages=user_languages, 
                         stats=stats)

@app.route('/profile')
@login_required
def profile():
    user_languages = db.get_user_languages(current_user.id)
    stats = db.get_user_stats(current_user.id)
    return render_template('profile.html', user=current_user, languages=user_languages, stats=stats)

@app.route('/practice/vocabulary')
@login_required
def practice_vocabulary():
    language_id = request.args.get('language_id', type=int)
    session_id = request.args.get('session_id', type=int)
    
    if not language_id or not session_id:
        return redirect(url_for('dashboard'))
    
    # Get language info
    languages = db.get_languages()
    language = next((lang for lang in languages if lang['id'] == language_id), None)
    
    if not language:
        return redirect(url_for('dashboard'))
    
    return render_template('practice_vocabulary.html', 
                         language=language, 
                         session_id=session_id)

@app.route('/practice/sentences')
@login_required
def practice_sentences():
    language_id = request.args.get('language_id', type=int)
    session_id = request.args.get('session_id', type=int)
    
    if not language_id or not session_id:
        return redirect(url_for('dashboard'))
    
    # Get language info
    languages = db.get_languages()
    language = next((lang for lang in languages if lang['id'] == language_id), None)
    
    if not language:
        return redirect(url_for('dashboard'))
    
    return render_template('practice_sentences.html', 
                         language=language, 
                         session_id=session_id)

@app.route('/api/languages', methods=['GET'])
def get_languages():
    languages = db.get_languages()
    return jsonify(languages)

@app.route('/api/user-languages', methods=['GET'])
@login_required
def get_user_languages_api():
    user_languages = db.get_user_languages(current_user.id)
    return jsonify(user_languages)

@app.route('/api/add-language', methods=['POST'])
@login_required
def add_language():
    data = request.get_json()
    language_id = data.get('language_id')
    
    if not language_id:
        return jsonify({'success': False, 'error': 'Language ID is required'}), 400
    
    # Convert language_id to integer
    try:
        language_id = int(language_id)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid language ID'}), 400
    
    try:
        db.add_user_language(current_user.id, language_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/vocabulary', methods=['GET'])
@login_required
def get_vocabulary():
    language_id = request.args.get('language_id', type=int)
    difficulty_level = request.args.get('difficulty_level')
    limit = request.args.get('limit', 50, type=int)
    
    vocabulary = db.get_user_vocabulary(current_user.id, language_id, difficulty_level, limit)
    return jsonify(vocabulary)

@app.route('/api/add-vocabulary', methods=['POST'])
@login_required
def add_vocabulary():
    data = request.get_json()
    language_id = data.get('language_id')
    word = data.get('word')
    translation = data.get('translation')
    difficulty_level = 'beginner'  # Default difficulty level
    category = data.get('category')
    part_of_speech = data.get('part_of_speech')
    example_sentence = data.get('example_sentence')
    
    if not language_id or not word:
        return jsonify({'success': False, 'error': 'Language and word are required'}), 400
    
    # Convert language_id to integer
    try:
        language_id = int(language_id)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid language ID'}), 400
    
    # Check if user has added this language
    user_languages = db.get_user_languages(current_user.id)
    user_language_ids = [lang['language_id'] for lang in user_languages]
    
    if language_id not in user_language_ids:
        return jsonify({'success': False, 'error': 'You can only add vocabulary for languages you have added to your profile'}), 400
    
    try:
        vocabulary_id = db.add_vocabulary(
            current_user.id, language_id, word, translation, 
            difficulty_level, category, part_of_speech, example_sentence
        )
        return jsonify({'success': True, 'vocabulary_id': vocabulary_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bulk-add-vocabulary', methods=['POST'])
@login_required
def bulk_add_vocabulary():
    data = request.get_json()
    language_id = data.get('language_id')
    vocabulary_list = data.get('vocabulary_list', [])
    
    if not language_id or not vocabulary_list:
        return jsonify({'success': False, 'error': 'Language and vocabulary list are required'}), 400
    
    # Convert language_id to integer
    try:
        language_id = int(language_id)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid language ID'}), 400
    
    # Check if user has added this language
    user_languages = db.get_user_languages(current_user.id)
    user_language_ids = [lang['language_id'] for lang in user_languages]
    
    if language_id not in user_language_ids:
        return jsonify({'success': False, 'error': 'You can only add vocabulary for languages you have added to your profile'}), 400
    
    try:
        added_count = 0
        for vocab in vocabulary_list:
            word = vocab.get('word')
            translation = vocab.get('translation')
            difficulty_level = 'beginner'  # Default difficulty level
            category = vocab.get('category')
            
            if word:
                db.add_vocabulary(
                    current_user.id, language_id, word, translation, 
                    difficulty_level, category
                )
                added_count += 1
        
        return jsonify({'success': True, 'added_count': added_count})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sentences', methods=['GET'])
@login_required
def get_sentences():
    language_id = request.args.get('language_id', type=int)
    difficulty_level = request.args.get('difficulty_level')
    limit = request.args.get('limit', 50, type=int)
    
    sentences = db.get_user_sentences(current_user.id, language_id, difficulty_level, limit)
    return jsonify(sentences)

@app.route('/api/add-sentence', methods=['POST'])
@login_required
def add_sentence():
    data = request.get_json()
    language_id = data.get('language_id')
    sentence = data.get('sentence')
    translation = data.get('translation')
    difficulty_level = data.get('difficulty_level', 'beginner')
    category = data.get('category')
    
    if not sentence or not language_id:
        return jsonify({'success': False, 'error': 'Sentence and language are required'})
    
    sentence_id = db.add_sentence(
        current_user.id, language_id, sentence, translation, 
        difficulty_level, category
    )
    
    return jsonify({'success': True, 'sentence_id': sentence_id})

@app.route('/api/practice/vocabulary', methods=['GET'])
@login_required
def get_vocabulary_practice():
    language_id = request.args.get('language_id', type=int)
    difficulty_level = request.args.get('difficulty_level')
    limit = request.args.get('limit', 10, type=int)
    
    vocabulary = db.get_random_vocabulary(current_user.id, language_id, difficulty_level, limit)
    return jsonify(vocabulary)

@app.route('/api/practice/sentence', methods=['GET'])
@login_required
def get_sentence_practice():
    language_id = request.args.get('language_id', type=int)
    difficulty_level = request.args.get('difficulty_level')
    
    sentence = db.get_random_sentence(current_user.id, language_id, difficulty_level)
    return jsonify(sentence)

@app.route('/api/practice/start-session', methods=['POST'])
@login_required
def start_practice_session():
    data = request.get_json()
    language_id = data.get('language_id')
    session_type = data.get('session_type', 'vocabulary')
    
    # Convert language_id to integer
    try:
        language_id = int(language_id)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid language ID'}), 400
    
    session_id = db.start_learning_session(current_user.id, language_id, session_type)
    return jsonify({'success': True, 'session_id': session_id})

@app.route('/api/practice/end-session', methods=['POST'])
@login_required
def end_practice_session():
    data = request.get_json()
    session_id = data.get('session_id')
    words_practiced = data.get('words_practiced', 0)
    sentences_practiced = data.get('sentences_practiced', 0)
    correct_answers = data.get('correct_answers', 0)
    total_questions = data.get('total_questions', 0)
    
    db.end_learning_session(session_id, words_practiced, sentences_practiced, correct_answers, total_questions)
    return jsonify({'success': True})

@app.route('/api/practice/record', methods=['POST'])
@login_required
def record_practice():
    data = request.get_json()
    session_id = data.get('session_id')
    vocabulary_id = data.get('vocabulary_id')
    sentence_id = data.get('sentence_id')
    user_answer = data.get('user_answer')
    correct_answer = data.get('correct_answer')
    is_correct = data.get('is_correct')
    response_time_ms = data.get('response_time_ms')
    
    db.record_practice(
        current_user.id, session_id, vocabulary_id, sentence_id,
        user_answer, correct_answer, is_correct, response_time_ms
    )
    
    return jsonify({'success': True})

@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    language_id = request.args.get('language_id', type=int)
    stats = db.get_user_stats(current_user.id, language_id)
    return jsonify(stats)

@app.route('/api/generate-sentences', methods=['POST'])
@login_required
def generate_sentences():
    data = request.get_json()
    language_id = data.get('language_id')
    difficulty_level = data.get('difficulty_level', 'beginner')
    
    print(f"🔍 Debug: Generating sentences for language_id={language_id}, difficulty={difficulty_level}")
    
    if not language_id:
        return jsonify({'success': False, 'error': 'Language ID is required'}), 400
    
    # Convert language_id to integer
    try:
        language_id = int(language_id)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid language ID'}), 400
    
    # Check if user has added this language
    user_languages = db.get_user_languages(current_user.id)
    user_language_ids = [lang['language_id'] for lang in user_languages]
    print(f"🔍 Debug: User languages: {user_language_ids}")
    
    if language_id not in user_language_ids:
        return jsonify({'success': False, 'error': 'You can only generate sentences for languages you have added to your profile'}), 400
    
    # Get vocabulary for the language
    vocabulary = db.get_user_vocabulary(current_user.id, language_id, difficulty_level, 20)
    print(f"🔍 Debug: Found {len(vocabulary)} vocabulary items")
    
    if not vocabulary:
        return jsonify({'success': False, 'error': 'No vocabulary found for this language and level'})
    
    # Get language name
    languages = db.get_languages()
    language_name = next((lang['name'] for lang in languages if lang['id'] == language_id), 'Unknown')
    print(f"🔍 Debug: Language name: {language_name}")
    
    # Generate sentences using OpenAI
    try:
        load_dotenv()
        api_key = os.getenv("APIKEY")
        print(f"🔍 Debug: API key loaded: {'Yes' if api_key and api_key != 'your_openai_api_key_here' else 'No'}")
        
        if not api_key or api_key == 'your_openai_api_key_here':
            return jsonify({'success': False, 'error': 'OpenAI API key not configured. Please set your API key in the .env file.'})
        
        vocab_words = [vocab['word'] for vocab in vocabulary[:10]]  # Use first 10 words
        vocab_str = ", ".join(vocab_words)
        print(f"🔍 Debug: Using vocabulary words: {vocab_str}")
        
        prompt = f"Generate 5 simple sentences in {language_name} using some of these words: {vocab_str}. Make sure each sentence uses 2-3 words from the list. Return only the sentences, one per line."
        
        print(f"🔍 Debug: Sending request to OpenAI...")
        try:
            response_data = call_openai_api([
                {"role": "system", "content": "You are a helpful language learning assistant."},
                {"role": "user", "content": prompt}
            ], max_tokens=200)
            
            content = response_data['choices'][0]['message']['content']
        except Exception as e:
            print(f"❌ Error calling OpenAI API: {str(e)}")
            return jsonify({'success': False, 'error': f'Failed to call OpenAI API: {str(e)}'})
        
        if content:
            generated_sentences = content.strip().split('\n')
            generated_sentences = [s.strip() for s in generated_sentences if s and s.strip()]
        else:
            generated_sentences = []
        
        print(f"🔍 Debug: Generated {len(generated_sentences)} sentences")
        
        # Add sentences to database
        for sentence in generated_sentences:
            db.add_sentence(current_user.id, language_id, sentence, difficulty_level=difficulty_level)
        
        return jsonify({'success': True, 'sentences': generated_sentences, 'count': len(generated_sentences)})
        
    except Exception as e:
        print(f"❌ Error in sentence generation: {str(e)}")
        return jsonify({'success': False, 'error': f'Failed to generate sentences: {str(e)}'})

@app.route('/api/practice/generate-sentence', methods=['POST'])
@login_required
def generate_practice_sentence():
    data = request.get_json()
    language_id = data.get('language_id')
    difficulty_level = data.get('difficulty_level', 'beginner')
    
    print(f"🔍 Debug: Generating practice sentence for language_id={language_id}, difficulty={difficulty_level}")
    
    if not language_id:
        return jsonify({'success': False, 'error': 'Language ID is required'}), 400
    
    # Convert language_id to integer
    try:
        language_id = int(language_id)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid language ID'}), 400
    
    # Check if user has added this language
    user_languages = db.get_user_languages(current_user.id)
    user_language_ids = [lang['language_id'] for lang in user_languages]
    print(f"🔍 Debug: User languages: {user_language_ids}")
    
    if language_id not in user_language_ids:
        return jsonify({'success': False, 'error': 'You can only practice languages you have added to your profile'}), 400
    
    try:
        # Get vocabulary for the language
        vocabulary = db.get_user_vocabulary(current_user.id, language_id, difficulty_level, 10)
        print(f"🔍 Debug: Found {len(vocabulary)} vocabulary items for practice")
        
        if not vocabulary:
            return jsonify({'success': False, 'error': 'No vocabulary found for this language and level'})
        
        # Get language name
        languages = db.get_languages()
        language_name = next((lang['name'] for lang in languages if lang['id'] == language_id), 'Unknown')
        print(f"🔍 Debug: Language name: {language_name}")
        
        # Generate sentence using OpenAI
        load_dotenv()
        api_key = os.getenv("APIKEY")
        print(f"🔍 Debug: API key loaded: {'Yes' if api_key and api_key != 'your_openai_api_key_here' else 'No'}")
        
        if not api_key or api_key == 'your_openai_api_key_here':
            return jsonify({'success': False, 'error': 'OpenAI API key not configured. Please set your API key in the .env file.'})
        
        vocab_words = [vocab['word'] for vocab in vocabulary[:5]]  # Use first 5 words
        vocab_str = ", ".join(vocab_words)
        print(f"🔍 Debug: Using vocabulary words: {vocab_str}")
        
        prompt = f"Generate a simple sentence in {language_name} using 2-3 words from this list: {vocab_str}. Also provide the English translation. Return in this exact format: SENTENCE|TRANSLATION"
        
        print(f"🔍 Debug: Sending request to OpenAI...")
        try:
            response_data = call_openai_api([
                {"role": "system", "content": "You are a helpful language learning assistant. Always respond with the format: SENTENCE|TRANSLATION"},
                {"role": "user", "content": prompt}
            ], max_tokens=100)
            
            content = response_data['choices'][0]['message']['content']
        except Exception as e:
            print(f"❌ Error calling OpenAI API: {str(e)}")
            return jsonify({'success': False, 'error': f'Failed to call OpenAI API: {str(e)}'})
        
        if content and '|' in content:
            parts = content.split('|')
            if len(parts) >= 2:
                sentence = parts[0].strip()
                translation = parts[1].strip()
                
                print(f"🔍 Debug: Parsed sentence: '{sentence}' | translation: '{translation}'")
                
                # Add sentence to database
                sentence_id = db.add_sentence(current_user.id, language_id, sentence, translation, difficulty_level=difficulty_level)
                
                return jsonify({
                    'success': True, 
                    'sentence': sentence,
                    'translation': translation,
                    'sentence_id': sentence_id
                })
        
        print(f"🔍 Debug: Failed to parse OpenAI response properly")
        return jsonify({'success': False, 'error': 'Failed to generate sentence'})
        
    except Exception as e:
        print(f"❌ Error in practice sentence generation: {str(e)}")
        return jsonify({'success': False, 'error': f'Failed to generate sentence: {str(e)}'})

@app.route('/api/practice/score-translation', methods=['POST'])
@login_required
def score_translation():
    data = request.get_json()
    user_translation = data.get('user_translation')
    correct_translation = data.get('correct_translation')
    
    if not user_translation or not correct_translation:
        return jsonify({'success': False, 'error': 'Both user translation and correct translation are required'}), 400
    
    try:
        # Simple similarity scoring (in a real app, you'd use more sophisticated NLP)
        similarity_score = calculate_similarity(user_translation, correct_translation)
        is_correct = similarity_score >= 0.6  # 60% similarity threshold
        
        return jsonify({
            'success': True,
            'is_correct': is_correct,
            'similarity_score': similarity_score,
            'correct_translation': correct_translation
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def calculate_similarity(user_answer, correct_answer):
    """Calculate similarity between user answer and correct answer"""
    if not correct_answer:
        return 0.0
    
    # Convert to lowercase and remove punctuation for comparison
    import re
    clean_user = re.sub(r'[^\w\s]', '', user_answer.lower())
    clean_correct = re.sub(r'[^\w\s]', '', correct_answer.lower())
    
    # Check if user answer contains key words from correct answer
    correct_words = [word for word in clean_correct.split() if len(word) > 2]
    user_words = [word for word in clean_user.split() if len(word) > 2]
    
    if not correct_words:
        return 0.0
    
    matching_words = [word for word in correct_words if word in user_words]
    similarity = len(matching_words) / len(correct_words)
    
    return similarity

# Function to call OpenAI API directly using requests
def call_openai_api(messages, max_tokens=200):
    """Call OpenAI API directly using requests to avoid proxy issues"""
    api_key = os.getenv("APIKEY")
    if not api_key or api_key == 'your_openai_api_key_here':
        raise ValueError("OpenAI API key not configured")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-4",
        "messages": messages,
        "max_tokens": max_tokens
    }
    
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=30
    )
    
    if response.status_code != 200:
        raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
    
    return response.json()

if __name__ == '__main__':
    # Initialize database
    db.init_database()
    
    # Create development user if in dev mode
    ensure_dev_user()
    
    # Set development mode environment variable
    if DEV_MODE:
        os.environ['DEV_MODE'] = 'true'
        print("🚀 Development mode enabled")
        print("📝 Use 'dev' / 'password123' to login")
    
    app.run(debug=True, use_reloader=False)
