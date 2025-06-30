// Global variables
let languages = [];
let vocabulary = [];

// Initialize profile page
document.addEventListener('DOMContentLoaded', function() {
    loadLanguages();
    loadVocabulary();
    setupEventListeners();
});

// Load available languages
async function loadLanguages() {
    try {
        const response = await fetch('/api/languages');
        languages = await response.json();
        populateLanguageSelects();
    } catch (error) {
        console.error('Error loading languages:', error);
    }
}

// Populate language select elements
function populateLanguageSelects() {
    const selects = ['languageSelect', 'bulkLanguageSelect'];
    
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

// Load vocabulary
async function loadVocabulary() {
    try {
        const response = await fetch('/api/vocabulary');
        vocabulary = await response.json();
        displayVocabulary(vocabulary);
    } catch (error) {
        console.error('Error loading vocabulary:', error);
    }
}

// Display vocabulary in the list
function displayVocabulary(vocabList) {
    const container = document.getElementById('vocabularyList');
    
    if (vocabList.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-book"></i>
                <h3>No vocabulary found</h3>
                <p>Add some words to get started!</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = vocabList.map(vocab => `
        <div class="vocabulary-item">
            <div class="vocab-info">
                <div class="vocab-word">
                    <strong>${vocab.word}</strong>
                    ${vocab.translation ? `<span class="translation">${vocab.translation}</span>` : ''}
                </div>
                <div class="vocab-meta">
                    <span class="difficulty-badge ${vocab.difficulty_level}">${vocab.difficulty_level}</span>
                    <span class="mastery-level">Mastery: ${vocab.mastery_level}/5</span>
                    <span class="review-count">Reviews: ${vocab.review_count}</span>
                </div>
            </div>
            <div class="vocab-actions">
                <button class="btn-secondary btn-small" onclick="editVocabulary(${vocab.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn-outline btn-small" onclick="deleteVocabulary(${vocab.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
}

// Filter vocabulary
function filterVocabulary() {
    const languageFilter = document.getElementById('vocabLanguageFilter').value;
    const difficultyFilter = document.getElementById('vocabDifficultyFilter').value;
    
    let filteredVocab = vocabulary;
    
    if (languageFilter) {
        filteredVocab = filteredVocab.filter(vocab => vocab.language_id == languageFilter);
    }
    
    if (difficultyFilter) {
        filteredVocab = filteredVocab.filter(vocab => vocab.difficulty_level === difficultyFilter);
    }
    
    displayVocabulary(filteredVocab);
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

function showBulkAddModal() {
    document.getElementById('bulkAddModal').style.display = 'flex';
}

function hideBulkAddModal() {
    document.getElementById('bulkAddModal').style.display = 'none';
}

// Add language
async function addLanguage() {
    const languageId = document.getElementById('languageSelect').value;
    const proficiencyLevel = document.getElementById('proficiencyLevel').value;
    
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
            body: JSON.stringify({ language_id: languageId, proficiency_level: proficiencyLevel })
        });
        
        const data = await response.json();
        
        if (data.success) {
            hideAddLanguageModal();
            window.location.reload();
        } else {
            alert(data.error || 'Failed to add language');
        }
    } catch (error) {
        console.error('Error adding language:', error);
        alert('An error occurred while adding the language');
    }
}

// Bulk add vocabulary
async function bulkAddVocabulary() {
    const languageId = document.getElementById('bulkLanguageSelect').value;
    const words = document.getElementById('bulkWords').value;
    const difficulty = document.getElementById('bulkDifficulty').value;
    
    if (!languageId || !words) {
        alert('Please fill in all required fields');
        return;
    }
    
    try {
        const response = await fetch('/api/bulk-add-vocabulary', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                language_id: languageId,
                words: words,
                difficulty_level: difficulty
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            hideBulkAddModal();
            document.getElementById('bulkWords').value = '';
            alert(`Successfully added ${data.added_count} words!`);
            loadVocabulary(); // Reload vocabulary list
        } else {
            alert(data.error || 'Failed to add vocabulary');
        }
    } catch (error) {
        console.error('Error adding vocabulary:', error);
        alert('An error occurred while adding vocabulary');
    }
}

// Change proficiency level
async function changeProficiency(languageId) {
    const newLevel = prompt('Enter new proficiency level (beginner/intermediate/advanced):');
    
    if (!newLevel || !['beginner', 'intermediate', 'advanced'].includes(newLevel.toLowerCase())) {
        alert('Please enter a valid proficiency level');
        return;
    }
    
    try {
        const response = await fetch('/api/add-language', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                language_id: languageId, 
                proficiency_level: newLevel.toLowerCase() 
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            window.location.reload();
        } else {
            alert(data.error || 'Failed to update proficiency level');
        }
    } catch (error) {
        console.error('Error updating proficiency:', error);
        alert('An error occurred while updating proficiency level');
    }
}

// Remove language
async function removeLanguage(languageId) {
    if (!confirm('Are you sure you want to remove this language? This will also remove all associated vocabulary and sentences.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/remove-language`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ language_id: languageId })
        });
        
        const data = await response.json();
        
        if (data.success) {
            window.location.reload();
        } else {
            alert(data.error || 'Failed to remove language');
        }
    } catch (error) {
        console.error('Error removing language:', error);
        alert('An error occurred while removing the language');
    }
}

// Edit vocabulary
function editVocabulary(vocabId) {
    const vocab = vocabulary.find(v => v.id === vocabId);
    if (!vocab) return;
    
    const newTranslation = prompt('Enter new translation (leave empty to keep current):', vocab.translation || '');
    const newDifficulty = prompt('Enter new difficulty level (beginner/intermediate/advanced):', vocab.difficulty_level);
    
    if (newTranslation === null || newDifficulty === null) return;
    
    if (!['beginner', 'intermediate', 'advanced'].includes(newDifficulty.toLowerCase())) {
        alert('Please enter a valid difficulty level');
        return;
    }
    
    // Here you would typically make an API call to update the vocabulary
    // For now, we'll just show a message
    alert('Vocabulary editing feature will be implemented in the next update!');
}

// Delete vocabulary
async function deleteVocabulary(vocabId) {
    if (!confirm('Are you sure you want to delete this vocabulary item?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/vocabulary/${vocabId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadVocabulary(); // Reload vocabulary list
            alert('Vocabulary deleted successfully!');
        } else {
            alert(data.error || 'Failed to delete vocabulary');
        }
    } catch (error) {
        console.error('Error deleting vocabulary:', error);
        alert('An error occurred while deleting vocabulary');
    }
} 