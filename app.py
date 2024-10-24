from flask import Flask, render_template, request, jsonify
from database import create_tables, get_sentence, check_translation, add_sentences, store_words, get_vocab
from openai import OpenAI
from dotenv import load_dotenv
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_words', methods=['POST'])
def add_words():
    language = request.form.get('language')
    level = request.form.get('level')
    if(not level):
        level = 'Low'
    response = request.form.get('response')
    file = request.files.get('file')
    
    # Validate input
    if not language or not response:
        return jsonify({"error": "Language and response are required/Must add words"}), 400
    
    # Read words from the uploaded file if provided
    if file and file.filename.endswith('.txt'):
        response = file.read().decode('utf-8').strip()  # Read and strip any whitespace/newlines

    # Ensure response is not empty after processing the file
    if not response:
        return jsonify({"error": "No words found in the response or file"}), 400

    try:
        store_words(language, level, response)
        return render_template('index.html')
        #return jsonify({"message": "Words added successfully"}), 201  # 201 Created
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # 500 Internal Server Error


@app.route('/generate_sentence', methods=['POST'])
def generate_sentence():
    language = request.form.get('language')
    level = request.form.get('level')
    if(not level):
        level = 'Low'
    sentence = get_sentence(language, level)
    if(sentence is None):
        sentence = generate_api_sentence(language, level)
    return render_template('sentence.html', sentence=sentence)

@app.route('/check_translation', methods=['POST'])
def check_translation_route():
    user_translation = request.form.get('translation')
    correct_translation = request.form.get('correct_sentence')
    result = check_translation(user_translation, correct_translation)
    return render_template('result.html', result=result)

# @app.route('/generate_api_sentence', methods=['POST'])

def generate_api_sentence(language, level):
    load_dotenv()
    
    # Retrieve vocabulary based on language and level
    vocab = get_vocab(language, level)
    if not vocab:
        raise ValueError("No vocabulary found for the given language and level.")
    
    # Format the vocabulary for the prompt
    vocab_str = ", ".join(vocab)
    
    # Create a prompt for generating sentences
    prompt = f"Generate multiple sentences in {language} using the following vocab: {vocab_str}. Ensure that two or three words from the vocab are used per sentence."

    try:
        client = OpenAI(
            # This is the default and can be omitted
            api_key=os.getenv("APIKEY"),
        )

        res = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that helps generate sentences",
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-4",
            max_tokens=150
        )
        
        # Extract generated sentences from the response
        generated_sentences = res['choices'][0]['message']['content'].strip().split('\n')

        # Remove any empty strings from the list
        generated_sentences = [sentence for sentence in generated_sentences if sentence]
        
        # Store multiple sentences in the database
        add_sentences(language, level, generated_sentences)
        
        # Retrieve and return a sentence from the database
        sentence = get_sentence(language, level)
        return sentence

    except Exception as e:
        print(f"Error generating sentences: {e}")
        return None


if __name__ == '__main__':
    create_tables()
    app.run(debug=False)
