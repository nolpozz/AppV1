# LinguaLearn - AI-Powered Language Learning App

A modern web application that helps users learn languages through personalized vocabulary, AI-generated sentences, and interactive practice sessions.

## 🚀 Live Demo

**Demo Account Credentials:**
- **Username:** `demo`
- **Password:** `demo123`

## ✨ Features

- **User Authentication**: Secure login and registration system
- **Multi-Language Support**: 15+ languages including Spanish, French, German, Italian, Portuguese, Russian, Japanese, Korean, Chinese, Arabic, Hindi, Dutch, Swedish, Norwegian, and Danish
- **Personalized Vocabulary**: Add and manage your own vocabulary words
- **AI-Generated Sentences**: Practice with sentences automatically generated from your vocabulary using OpenAI GPT-4
- **Interactive Practice Sessions**: Vocabulary and sentence practice with scoring and feedback
- **Progress Tracking**: Monitor your learning progress with detailed statistics
- **Modern UI/UX**: Clean, responsive design with intuitive navigation

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite with SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **AI Integration**: OpenAI GPT-4 API
- **Authentication**: Flask-Login
- **Styling**: Custom CSS with Font Awesome icons

## 📋 Prerequisites

Before running this application, make sure you have:

- Python 3.7 or higher
- pip (Python package installer)
- An OpenAI API key (for AI sentence generation)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/lingualearn.git
cd lingualearn
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
# Development Environment Variables
DEV_MODE=true
FLASK_ENV=development

# OpenAI API Key (get yours from https://platform.openai.com/api-keys)
APIKEY=your_openai_api_key_here
```

**Important**: Replace `your_openai_api_key_here` with your actual OpenAI API key.

### 4. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### 5. Create Your First Account

1. Visit `http://localhost:5000`
2. Click "Sign up" to create a new account
3. Add languages to your profile
4. Add vocabulary words
5. Start practicing!

## 🎯 How to Use

### Getting Started

1. **Register/Login**: Create an account or use the demo credentials
2. **Add Languages**: Select languages you want to learn from the dashboard
3. **Add Vocabulary**: Add words in your target languages
4. **Practice**: Start vocabulary or sentence practice sessions

### Practice Modes

- **Vocabulary Practice**: Test your knowledge of individual words
- **Sentence Practice**: Translate AI-generated sentences using your vocabulary

### AI Features

- **Automatic Sentence Generation**: The app generates practice sentences using your vocabulary and OpenAI GPT-4
- **Smart Scoring**: Translation accuracy is evaluated using similarity algorithms
- **Personalized Content**: All practice content is based on your own vocabulary

## 🔧 Development Setup

### For Developers

1. **Clone and install** as described above
2. **Run development setup**:
   ```bash
   python dev_setup.py
   ```
3. **Reset database** (if needed):
   ```bash
   python reset_db.py
   ```

### Database Schema

The app uses SQLite with the following main tables:
- `users`: User accounts and authentication
- `languages`: Available languages
- `user_languages`: User-language relationships
- `vocabulary`: User vocabulary words
- `sentences`: Generated practice sentences
- `learning_sessions`: Practice session tracking
- `practice_records`: Individual practice results

## 🌟 Demo Walkthrough

### For Visitors

1. **Access the Demo**: Use the demo credentials above
2. **Explore Languages**: Add Spanish, French, or any language you're interested in
3. **Add Vocabulary**: Add a few words like "hello", "goodbye", "thank you"
4. **Try Practice**: Start a sentence practice session to see AI-generated content
5. **Experience the Flow**: See how the app generates personalized sentences from your vocabulary

### Demo Features to Try

- **Language Selection**: Add multiple languages to your profile
- **Vocabulary Management**: Add words with translations
- **AI Sentence Generation**: Watch as the app creates practice sentences
- **Interactive Practice**: Complete a practice session with scoring
- **Progress Tracking**: View your learning statistics

## 🔒 Security Notes

- Demo accounts are automatically created for testing
- All user data is stored locally in SQLite
- OpenAI API calls are made securely with proper error handling
- Passwords are hashed using Werkzeug security functions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT-4 API
- Flask community for the excellent web framework
- Font Awesome for the beautiful icons

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/lingualearn/issues) page
2. Create a new issue with detailed information
3. Include your Python version and any error messages

---

**Happy Learning! 🌍📚**