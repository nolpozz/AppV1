document.addEventListener("DOMContentLoaded", () => {
    let sentenceElement = document.getElementById("sentence");
    let newSentenceButton = document.getElementById("new-sentence-btn");
    let translationForm = document.getElementById("translation-form");
    let translationInput = document.getElementById("translation");
    let correctSentenceInput = document.getElementById("correct_sentence");
    let resultElement = document.getElementById("result");

    const apiUrl = '/generate_sentence';
    const checkTranslationUrl = '/check_translation';

    let getNewSentence = () => {
        fetch(apiUrl)
            .then(response => response.json())
            .then(data => {
                sentenceElement.innerText = data.sentence;
                correctSentenceInput.value = data.sentence; // Update hidden field
                resultElement.innerText = ''; // Clear previous result
                translationInput.value = ''; // Clear translation input
            })
            .catch(error => console.error('Error fetching sentence:', error));
    };

    let checkTranslation = (event) => {
        event.preventDefault(); // Prevent form from submitting traditionally

        let translation = translationInput.value;
        let correctSentence = correctSentenceInput.value;

        fetch(checkTranslationUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ translation: translation, correct_sentence: correctSentence })
        })
            .then(response => response.json())
            .then(data => {
                if (data.correct) {
                    resultElement.innerText = 'Correct!';
                    resultElement.style.color = 'green';
                } else {
                    resultElement.innerText = 'Incorrect!';
                    resultElement.style.color = 'red';
                }
            })
            .catch(error => console.error('Error checking translation:', error));
    };

    newSentenceButton.addEventListener("click", getNewSentence);
    translationForm.addEventListener("submit", checkTranslation);
});
