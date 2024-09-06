from flask import Flask, render_template, request, jsonify
from database import create_tables, get_sentence, check_translation
import openai
from dotenv import load_dotenv
import os

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

# Using OpenAI to generate sentence
@app.route('/generate_api_sentence', methods=['POST'])
def generate_api_sentence():
    load_dotenv()
    openai.api_key = os.getenv("APIKEY")
    
    # Get the language and response from the form
    language = request.form.get('language')
    response = request.form.get('response')
    
    # Get the uploaded file (if any)
    file = request.files.get('file')
    
    if not language or not response:
        return jsonify({"error": "Language and response are required"}), 400
    
    # Optionally, process the file content (if applicable)
    if file and file.filename.endswith('.txt'):
        response = file.read().decode('utf-8')  # Assuming it's a text file
        # Process the file content if needed...
    
    prompt = f"Generate a sentence in {language} using the following vocab: {response}"
    # prompt = "Given the following vocab list in a language, write a single, grammatically correct sentence using only the words in the list plus necessary inflections and other grammatical pieces:\n" + ", ".join(vocab_list)
    
    
    response = openai.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an assistant that helps generate sentences."},
            {"role": "user", "content": prompt}
        ],
        model="gpt-4o",
        max_tokens=50
    )
    # # Use the chat model with the correct endpoint
    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",  # or "gpt-4" if you have access
    #     messages=[
    #         {"role": "system", "content": "You are an assistant that helps generate sentences."},
    #         {"role": "user", "content": prompt}
    #     ]
    # )
    
    sentence = response.choices[0].message.content
    return render_template('sentence.html', sentence=sentence)



if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
