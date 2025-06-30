class VocabularyPractice {
    constructor() {
        this.sessionId = sessionId;
        this.languageId = languageId;
        this.languageName = languageName;
        this.currentQuestion = 0;
        this.totalQuestions = 10;
        this.score = 0;
        this.totalAnswered = 0;
        this.startTime = Date.now();
        this.questions = [];
        this.currentQuestionData = null;
        
        this.init();
    }
    
    async init() {
        await this.loadQuestions();
        this.startTimer();
        this.showQuestion();
        this.bindEvents();
    }
    
    async loadQuestions() {
        try {
            const response = await fetch(`/api/practice/vocabulary?language_id=${this.languageId}&limit=${this.totalQuestions}`);
            this.questions = await response.json();
            
            if (this.questions.length === 0) {
                this.showNoVocabularyMessage();
                return;
            }
            
            // Shuffle questions
            this.questions = this.shuffleArray(this.questions);
        } catch (error) {
            console.error('Error loading questions:', error);
            this.showError('Failed to load vocabulary questions');
        }
    }
    
    showNoVocabularyMessage() {
        const container = document.getElementById('question-container');
        container.innerHTML = `
            <div class="no-vocabulary-card">
                <h2>No Vocabulary Available</h2>
                <p>You need to add some vocabulary for ${this.languageName} before you can practice.</p>
                <a href="/dashboard" class="btn btn-primary">Back to Dashboard</a>
            </div>
        `;
    }
    
    showError(message) {
        const container = document.getElementById('question-container');
        container.innerHTML = `
            <div class="error-card">
                <h2>Error</h2>
                <p>${message}</p>
                <a href="/dashboard" class="btn btn-primary">Back to Dashboard</a>
            </div>
        `;
    }
    
    shuffleArray(array) {
        const shuffled = [...array];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
    }
    
    showQuestion() {
        if (this.currentQuestion >= this.questions.length) {
            this.endPractice();
            return;
        }
        
        this.currentQuestionData = this.questions[this.currentQuestion];
        const questionText = document.getElementById('question-text');
        const answerOptions = document.getElementById('answer-options');
        
        questionText.textContent = this.currentQuestionData.word;
        
        // Generate answer options
        const options = this.generateAnswerOptions();
        answerOptions.innerHTML = options.map(option => `
            <button class="answer-option" data-answer="${option}">
                ${option}
            </button>
        `).join('');
        
        // Update question number
        document.getElementById('question-number').textContent = this.currentQuestion + 1;
        document.getElementById('total-questions').textContent = this.questions.length;
        
        // Show question container
        document.getElementById('question-container').style.display = 'block';
        document.getElementById('feedback-container').style.display = 'none';
        document.getElementById('results-container').style.display = 'none';
    }
    
    generateAnswerOptions() {
        const correctAnswer = this.currentQuestionData.translation || 'No translation available';
        const options = [correctAnswer];
        
        // Get other random translations for wrong answers
        const otherQuestions = this.questions.filter(q => q.id !== this.currentQuestionData.id);
        const randomQuestions = this.shuffleArray(otherQuestions).slice(0, 3);
        
        randomQuestions.forEach(q => {
            const translation = q.translation || 'No translation available';
            if (!options.includes(translation)) {
                options.push(translation);
            }
        });
        
        // Fill with generic options if needed
        const genericOptions = ['I don\'t know', 'Skip this question', 'Need help'];
        while (options.length < 4) {
            const option = genericOptions[options.length - 1] || `Option ${options.length + 1}`;
            if (!options.includes(option)) {
                options.push(option);
            }
        }
        
        return this.shuffleArray(options);
    }
    
    async handleAnswer(selectedAnswer) {
        const isCorrect = selectedAnswer === (this.currentQuestionData.translation || 'No translation available');
        this.totalAnswered++;
        
        if (isCorrect) {
            this.score++;
        }
        
        // Update score display
        document.getElementById('score').textContent = this.score;
        document.getElementById('total-answered').textContent = this.totalAnswered;
        
        // Record practice
        await this.recordPractice(selectedAnswer, isCorrect);
        
        // Show feedback
        this.showFeedback(isCorrect, selectedAnswer);
    }
    
    async recordPractice(userAnswer, isCorrect) {
        try {
            await fetch('/api/practice/record', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    vocabulary_id: this.currentQuestionData.id,
                    user_answer: userAnswer,
                    correct_answer: this.currentQuestionData.translation || 'No translation available',
                    is_correct: isCorrect,
                    response_time_ms: Date.now() - this.startTime
                })
            });
        } catch (error) {
            console.error('Error recording practice:', error);
        }
    }
    
    showFeedback(isCorrect, selectedAnswer) {
        const feedbackContainer = document.getElementById('feedback-container');
        const feedbackIcon = document.getElementById('feedback-icon');
        const feedbackTitle = document.getElementById('feedback-title');
        const feedbackMessage = document.getElementById('feedback-message');
        
        if (isCorrect) {
            feedbackIcon.textContent = '✓';
            feedbackIcon.className = 'feedback-icon correct';
            feedbackTitle.textContent = 'Correct!';
            feedbackMessage.textContent = 'Great job! You got it right.';
        } else {
            feedbackIcon.textContent = '✗';
            feedbackIcon.className = 'feedback-icon incorrect';
            feedbackTitle.textContent = 'Incorrect';
            feedbackMessage.textContent = `The correct answer was: "${this.currentQuestionData.translation || 'No translation available'}"`;
        }
        
        document.getElementById('question-container').style.display = 'none';
        feedbackContainer.style.display = 'block';
    }
    
    nextQuestion() {
        this.currentQuestion++;
        this.showQuestion();
    }
    
    endPractice() {
        const endTime = Date.now();
        const totalTime = Math.floor((endTime - this.startTime) / 1000);
        const accuracy = this.totalAnswered > 0 ? Math.round((this.score / this.totalAnswered) * 100) : 0;
        
        // Update results
        document.getElementById('final-score').textContent = `${this.score}/${this.totalAnswered}`;
        document.getElementById('accuracy').textContent = `${accuracy}%`;
        document.getElementById('final-time').textContent = this.formatTime(totalTime);
        
        // End session
        this.endSession();
        
        // Show results
        document.getElementById('question-container').style.display = 'none';
        document.getElementById('feedback-container').style.display = 'none';
        document.getElementById('results-container').style.display = 'block';
    }
    
    async endSession() {
        try {
            await fetch('/api/practice/end-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    words_practiced: this.totalAnswered,
                    sentences_practiced: 0,
                    correct_answers: this.score,
                    total_questions: this.totalAnswered
                })
            });
        } catch (error) {
            console.error('Error ending session:', error);
        }
    }
    
    startTimer() {
        this.timerInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
            document.getElementById('timer').textContent = this.formatTime(elapsed);
        }, 1000);
    }
    
    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    
    bindEvents() {
        // Answer option clicks
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('answer-option')) {
                const answer = e.target.dataset.answer;
                this.handleAnswer(answer);
            }
        });
        
        // Next question button
        document.getElementById('next-question').addEventListener('click', () => {
            this.nextQuestion();
        });
        
        // Practice again button
        document.getElementById('practice-again').addEventListener('click', () => {
            window.location.reload();
        });
    }
}

// Initialize practice when page loads
document.addEventListener('DOMContentLoaded', () => {
    new VocabularyPractice();
}); 