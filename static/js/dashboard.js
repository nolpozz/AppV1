// Global variables
let languages = [];
let userLanguages = [];
let currentSessionId = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadLanguages();
    loadUserLanguages();
    setupEventListeners();
});

// Load available languages
async function loadLanguages() {
    try {
        const response = await fetch('/api/languages');
        languages = await response.json();
        
        // Populate language selects in modals
        populateLanguageSelects();
    } catch (error) {
        console.error('Error loading languages:', error);
    }
}

// Load user's languages
async function loadUserLanguages() {
    try {
        const response = await fetch('/api/user-languages');
        userLanguages = await response.json();
        
        // Update vocabulary language select to only show user's languages
        updateVocabularyLanguageSelect();
    } catch (error) {
        console.error('Error loading user languages:', error);
    }
}

// Populate language select elements
function populateLanguageSelects() {
    const selects = ['languageSelect'];
    
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (select) {
            select.innerHTML = '<option value="">Select a language...</option>';
            languages.forEach(lang => {
                const option = document.createElement('option');
                option.value = lang.id;
                option.textContent = `${lang.flag_emoji} ${lang.name}`;
                select.appendChild(option);
            });
        }
    });
}

// Update vocabulary language select to only show user's languages
function updateVocabularyLanguageSelect() {
    const select = document.getElementById('vocabLanguageSelect');
    if (select) {
        select.innerHTML = '<option value="">Select a language...</option>';
        
        if (userLanguages.length === 0) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'No languages added yet';
            option.disabled = true;
            select.appendChild(option);
            return;
        }
        
        userLanguages.forEach(userLang => {
            const language = languages.find(lang => lang.id === userLang.language_id);
            if (language) {
                const option = document.createElement('option');
                option.value = userLang.language_id;
                option.textContent = `${language.flag_emoji} ${language.name}`;
                select.appendChild(option);
            }
        });
    }
}

// Setup event listeners
function setupEventListeners() {
    // Modal close buttons
    document.querySelectorAll('.modal-close').forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
            }
        });
    });
    
    // Close modal when clicking outside
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.style.display = 'none';
            }
        });
    });
}

// Modal functions
function showAddLanguageModal() {
    document.getElementById('addLanguageModal').style.display = 'flex';
}

function hideAddLanguageModal() {
    document.getElementById('addLanguageModal').style.display = 'none';
}

function showAddVocabularyModal() {
    document.getElementById('addVocabularyModal').style.display = 'flex';
}

function hideAddVocabularyModal() {
    document.getElementById('addVocabularyModal').style.display = 'none';
}

// Add language
async function addLanguage() {
    const languageId = document.getElementById('languageSelect').value;
    
    if (!languageId) {
        alert('Please select a language');
        return;
    }
    
    try {
        const response = await fetch('/api/add-language', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ language_id: languageId })
        });
        
        const data = await response.json();
        
        if (data.success) {
            hideAddLanguageModal();
            // Reload page to show new language
            window.location.reload();
        } else {
            alert(data.error || 'Failed to add language');
        }
    } catch (error) {
        console.error('Error adding language:', error);
        alert('An error occurred while adding the language');
    }
}

// Add vocabulary
async function addVocabulary() {
    const languageId = document.getElementById('vocabLanguageSelect').value;
    const word = document.getElementById('vocabWord').value;
    const translation = document.getElementById('vocabTranslation').value;
    
    if (!languageId || !word) {
        alert('Please fill in all required fields');
        return;
    }
    
    try {
        const response = await fetch('/api/add-vocabulary', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                language_id: languageId,
                word: word,
                translation: translation
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            hideAddVocabularyModal();
            // Clear form
            document.getElementById('vocabWord').value = '';
            document.getElementById('vocabTranslation').value = '';
            alert('Vocabulary added successfully!');
        } else {
            alert(data.error || 'Failed to add vocabulary');
        }
    } catch (error) {
        console.error('Error adding vocabulary:', error);
        alert('An error occurred while adding vocabulary');
    }
}

// Start practice session
async function startPractice(languageId, sessionType) {
    try {
        // Start session
        const sessionResponse = await fetch('/api/practice/start-session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                language_id: languageId,
                session_type: sessionType
            })
        });
        
        const sessionData = await sessionResponse.json();
        
        if (sessionData.success) {
            currentSessionId = sessionData.session_id;
            
            // Redirect to practice page
            const practiceUrl = sessionType === 'vocabulary' 
                ? `/practice/vocabulary?language_id=${languageId}&session_id=${currentSessionId}`
                : `/practice/sentences?language_id=${languageId}&session_id=${currentSessionId}`;
            
            window.location.href = practiceUrl;
        } else {
            alert('Failed to start practice session');
        }
    } catch (error) {
        console.error('Error starting practice:', error);
        alert('An error occurred while starting practice');
    }
}

// Utility function to show notifications
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    if (type === 'success') {
        notification.style.background = '#28a745';
    } else if (type === 'error') {
        notification.style.background = '#dc3545';
    } else {
        notification.style.background = '#17a2b8';
    }
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style); 