from flask import Flask, render_template, request, jsonify
from database import create_tables, get_sentence, check_translation

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_sentence', methods=['POST'])
def generate_sentence():
    language = request.form['language']
    level = request.form['level']
    sentence = get_sentence(level, language)
    return render_template('sentence.html', sentence=sentence)

@app.route('/check_translation', methods=['POST'])
def check_translation_route():
    user_translation = request.form['translation']
    correct_translation = request.form['correct_sentence']
    result = check_translation(user_translation, correct_translation)
    return render_template('result.html', result=result)

@app.route('/api/generate_sentence', methods=['GET'])
def api_generate_sentence():
    # In a real application, generate a sentence dynamically
    sentence = "This is a generated sentence from the API."
    return jsonify({"sentence": sentence})

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
