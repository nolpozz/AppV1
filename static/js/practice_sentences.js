class SentencePractice {
    constructor() {
        this.sessionId = sessionId;
        this.languageId = languageId;
        this.languageName = languageName;
        this.currentQuestion = 0;
        this.totalQuestions = 5;
        this.score = 0;
        this.totalAnswered = 0;
        this.startTime = Date.now();
        this.questions = [];
        this.currentQuestionData = null;
        
        this.init();
    }
    
    async init() {
        this.startTimer();
        this.showQuestion();
        this.bindEvents();
    }
    
    async generateSentence() {
        try {
            const response = await fetch('/api/practice/generate-sentence', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    language_id: this.languageId,
                    difficulty_level: 'beginner'
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                return {
                    sentence: data.sentence,
                    translation: data.translation,
                    sentence_id: data.sentence_id
                };
            } else {
                throw new Error(data.error || 'Failed to generate sentence');
            }
        } catch (error) {
            console.error('Error generating sentence:', error);
            throw error;
        }
    }
    
    async showQuestion() {
        if (this.currentQuestion >= this.totalQuestions) {
            this.endPractice();
            return;
        }
        
        try {
            // Show loading state
            const questionText = document.getElementById('question-text');
            const translationInput = document.getElementById('translation-answer');
            const submitButton = document.getElementById('submit-answer');
            
            questionText.textContent = 'Generating sentence...';
            translationInput.value = '';
            translationInput.disabled = true;
            submitButton.disabled = true;
            
            // Generate new sentence
            this.currentQuestionData = await this.generateSentence();
            
            // Update question display
            questionText.textContent = this.currentQuestionData.sentence;
            translationInput.disabled = false;
            submitButton.disabled = false;
            
            // Update question number
            document.getElementById('question-number').textContent = this.currentQuestion + 1;
            document.getElementById('total-questions').textContent = this.totalQuestions;
            
            // Show question container
            document.getElementById('question-container').style.display = 'block';
            document.getElementById('feedback-container').style.display = 'none';
            document.getElementById('results-container').style.display = 'none';
            
            // Focus on input
            translationInput.focus();
            
        } catch (error) {
            this.showError('Failed to generate sentence. Please try again.');
        }
    }
    
    showError(message) {
        const container = document.getElementById('question-container');
        container.innerHTML = `
            <div class="error-card">
                <h2>Error</h2>
                <p>${message}</p>
                <button class="btn btn-primary" onclick="window.location.reload()">Try Again</button>
            </div>
        `;
    }
    
    async handleAnswer() {
        const userAnswer = document.getElementById('translation-answer').value.trim();
        
        if (!userAnswer) {
            alert('Please enter a translation');
            return;
        }
        
        this.totalAnswered++;
        
        // Score the translation
        const isCorrect = await this.scoreTranslation(userAnswer);
        
        if (isCorrect) {
            this.score++;
        }
        
        // Update score display
        document.getElementById('score').textContent = this.score;
        document.getElementById('total-answered').textContent = this.totalAnswered;
        
        // Record practice
        await this.recordPractice(userAnswer, isCorrect);
        
        // Show feedback
        this.showFeedback(isCorrect, userAnswer);
    }
    
    async scoreTranslation(userAnswer) {
        try {
            const response = await fetch('/api/practice/score-translation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_translation: userAnswer,
                    correct_translation: this.currentQuestionData.translation
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                return data.is_correct;
            } else {
                console.error('Error scoring translation:', data.error);
                return false;
            }
        } catch (error) {
            console.error('Error scoring translation:', error);
            return false;
        }
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
                    sentence_id: this.currentQuestionData.sentence_id,
                    user_answer: userAnswer,
                    correct_answer: this.currentQuestionData.translation,
                    is_correct: isCorrect,
                    response_time_ms: Date.now() - this.startTime
                })
            });
        } catch (error) {
            console.error('Error recording practice:', error);
        }
    }
    
    showFeedback(isCorrect, userAnswer) {
        const feedbackContainer = document.getElementById('feedback-container');
        const feedbackIcon = document.getElementById('feedback-icon');
        const feedbackTitle = document.getElementById('feedback-title');
        const feedbackMessage = document.getElementById('feedback-message');
        const correctTranslation = document.getElementById('correct-translation');
        
        if (isCorrect) {
            feedbackIcon.textContent = '✓';
            feedbackIcon.className = 'feedback-icon correct';
            feedbackTitle.textContent = 'Excellent Translation!';
            feedbackMessage.textContent = 'Your translation was accurate!';
        } else {
            feedbackIcon.textContent = '✗';
            feedbackIcon.className = 'feedback-icon incorrect';
            feedbackTitle.textContent = 'Keep Practicing';
            feedbackMessage.textContent = 'Your translation was close, but here\'s the correct translation:';
        }
        
        correctTranslation.textContent = this.currentQuestionData.translation;
        
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
                    words_practiced: 0,
                    sentences_practiced: this.totalAnswered,
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
        // Submit answer button
        document.getElementById('submit-answer').addEventListener('click', () => {
            this.handleAnswer();
        });
        
        // Enter key in textarea
        document.getElementById('translation-answer').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleAnswer();
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
    new SentencePractice();
}); 