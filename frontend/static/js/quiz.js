/**
 * Quiz management JavaScript
 * Handles dynamic question/answer forms and CRUD operations
 */

let questionCount = 0;

/**
 * Initialize the quiz form event handlers
 */
function initQuizForm() {
    const form = document.getElementById('quiz-form');
    const addQuestionBtn = document.getElementById('add-question-btn');

    if (form) {
        form.addEventListener('submit', handleQuizSubmit);
    }

    if (addQuestionBtn) {
        addQuestionBtn.addEventListener('click', addQuestion);
    }
}

/**
 * Add a new question to the form
 * @param {Object} questionData - Optional existing question data for editing
 */
function addQuestion(questionData = null) {
    questionCount++;
    const questionId = questionCount;

    const questionHtml = `
        <div class="question-block" data-question-id="${questionId}">
            <div class="question-header">
                <h3>Question ${questionId}</h3>
                <button type="button" class="btn btn-danger btn-sm" onclick="removeQuestion(${questionId})">Remove</button>
            </div>
            <div class="form-group">
                <label for="question-${questionId}-text">Question Text</label>
                <input type="text"
                       id="question-${questionId}-text"
                       name="questions[${questionId}][text]"
                       required
                       maxlength="1000"
                       value="${questionData?.text || ''}"
                       placeholder="Enter your question">
                <span class="error-message" id="question-${questionId}-text-error"></span>
            </div>
            <div class="form-group">
                <label for="question-${questionId}-points">Points</label>
                <input type="number"
                       id="question-${questionId}-points"
                       name="questions[${questionId}][points]"
                       min="1"
                       max="100"
                       value="${questionData?.points || 1}">
            </div>
            <div class="answers-container" id="answers-${questionId}">
                <h4>Answers</h4>
                <div class="answers-list" id="answers-list-${questionId}">
                    <!-- Answers will be added here -->
                </div>
                <button type="button" class="btn btn-secondary btn-sm" onclick="addAnswer(${questionId})">Add Answer</button>
            </div>
        </div>
    `;

    document.getElementById('questions-list').insertAdjacentHTML('beforeend', questionHtml);

    // Add initial answers or load existing
    if (questionData?.answers) {
        questionData.answers.forEach(answer => addAnswer(questionId, answer));
    } else {
        // Add two default answers
        addAnswer(questionId, { text: '', is_correct: true });
        addAnswer(questionId, { text: '', is_correct: false });
    }

    updateQuestionNumbers();
}

/**
 * Remove a question from the form
 * @param {number} questionId - The question ID to remove
 */
function removeQuestion(questionId) {
    const questions = document.querySelectorAll('.question-block');
    if (questions.length <= 1) {
        showFormError('A quiz must have at least one question.');
        return;
    }

    const questionBlock = document.querySelector(`[data-question-id="${questionId}"]`);
    if (questionBlock) {
        questionBlock.remove();
        updateQuestionNumbers();
    }
}

/**
 * Update question numbers after add/remove
 */
function updateQuestionNumbers() {
    const questions = document.querySelectorAll('.question-block');
    questions.forEach((q, index) => {
        const header = q.querySelector('h3');
        if (header) {
            header.textContent = `Question ${index + 1}`;
        }
    });
}

let answerCounts = {};

/**
 * Add an answer to a question
 * @param {number} questionId - The question ID
 * @param {Object} answerData - Optional existing answer data
 */
function addAnswer(questionId, answerData = null) {
    if (!answerCounts[questionId]) {
        answerCounts[questionId] = 0;
    }
    answerCounts[questionId]++;
    const answerId = answerCounts[questionId];

    const isCorrect = answerData?.is_correct || false;
    const answerText = answerData?.text || '';

    const answerHtml = `
        <div class="answer-row" data-answer-id="${answerId}">
            <input type="radio"
                   name="questions[${questionId}][correct]"
                   value="${answerId}"
                   ${isCorrect ? 'checked' : ''}
                   title="Mark as correct answer">
            <input type="text"
                   name="questions[${questionId}][answers][${answerId}][text]"
                   required
                   maxlength="500"
                   value="${answerText}"
                   placeholder="Enter answer option">
            <button type="button" class="btn btn-danger btn-sm" onclick="removeAnswer(${questionId}, ${answerId})">×</button>
        </div>
    `;

    document.getElementById(`answers-list-${questionId}`).insertAdjacentHTML('beforeend', answerHtml);
}

/**
 * Remove an answer from a question
 * @param {number} questionId - The question ID
 * @param {number} answerId - The answer ID to remove
 */
function removeAnswer(questionId, answerId) {
    const answersList = document.getElementById(`answers-list-${questionId}`);
    const answers = answersList.querySelectorAll('.answer-row');

    if (answers.length <= 2) {
        showFormError('Each question must have at least 2 answers.');
        return;
    }

    const answerRow = answersList.querySelector(`[data-answer-id="${answerId}"]`);
    if (answerRow) {
        // Check if removing the correct answer
        const radio = answerRow.querySelector('input[type="radio"]');
        if (radio && radio.checked) {
            // Select another answer as correct
            const remainingRadios = answersList.querySelectorAll('input[type="radio"]:not([value="' + answerId + '"])');
            if (remainingRadios.length > 0) {
                remainingRadios[0].checked = true;
            }
        }
        answerRow.remove();
    }
}

/**
 * Handle quiz form submission
 * @param {Event} event - Form submit event
 */
async function handleQuizSubmit(event) {
    event.preventDefault();
    clearFormErrors();

    const form = event.target;
    const quizId = form.dataset.quizId;
    const isEdit = !!quizId;

    // Gather form data
    const title = document.getElementById('quiz-title').value.trim();

    if (!title) {
        showFieldError('title', 'Quiz title is required.');
        return;
    }

    const questions = gatherQuestions();

    if (!validateQuestions(questions)) {
        return;
    }

    const quizData = {
        title: title,
        questions: questions
    };

    try {
        const url = isEdit ? `/quizzes/${quizId}` : '/quizzes';
        const method = isEdit ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(quizData)
        });

        if (response.ok) {
            window.location.href = '/my-quizzes';
        } else {
            const errorData = await response.json();
            handleApiError(errorData);
        }
    } catch (error) {
        showFormError('An error occurred while saving the quiz. Please try again.');
        console.error('Quiz save error:', error);
    }
}

/**
 * Gather question data from the form
 * @returns {Array} Array of question objects
 */
function gatherQuestions() {
    const questions = [];
    const questionBlocks = document.querySelectorAll('.question-block');

    questionBlocks.forEach((block, index) => {
        const questionId = block.dataset.questionId;
        const textInput = block.querySelector(`input[name="questions[${questionId}][text]"]`);
        const pointsInput = block.querySelector(`input[name="questions[${questionId}][points]"]`);
        const correctRadio = block.querySelector(`input[name="questions[${questionId}][correct]"]:checked`);
        const answerInputs = block.querySelectorAll(`input[name^="questions[${questionId}][answers]"][name$="[text]"]`);

        const answers = [];
        answerInputs.forEach((input) => {
            const match = input.name.match(/answers\]\[(\d+)\]/);
            const answerId = match ? match[1] : null;
            const isCorrect = correctRadio && correctRadio.value === answerId;

            answers.push({
                text: input.value.trim(),
                is_correct: isCorrect
            });
        });

        questions.push({
            text: textInput ? textInput.value.trim() : '',
            points: pointsInput ? parseInt(pointsInput.value, 10) || 1 : 1,
            answers: answers
        });
    });

    return questions;
}

/**
 * Validate questions before submission
 * @param {Array} questions - Array of question objects
 * @returns {boolean} True if valid
 */
function validateQuestions(questions) {
    if (questions.length === 0) {
        showFormError('A quiz must have at least one question.');
        return false;
    }

    for (let i = 0; i < questions.length; i++) {
        const q = questions[i];

        if (!q.text) {
            showFormError(`Question ${i + 1}: Question text is required.`);
            return false;
        }

        if (q.answers.length < 2) {
            showFormError(`Question ${i + 1}: Each question must have at least 2 answers.`);
            return false;
        }

        const correctCount = q.answers.filter(a => a.is_correct).length;
        if (correctCount !== 1) {
            showFormError(`Question ${i + 1}: Each question must have exactly one correct answer.`);
            return false;
        }

        for (let j = 0; j < q.answers.length; j++) {
            if (!q.answers[j].text) {
                showFormError(`Question ${i + 1}: Answer ${j + 1} text is required.`);
                return false;
            }
        }
    }

    return true;
}

/**
 * Load existing quiz data into the form
 * @param {Object} quizData - Quiz data object
 */
function loadQuizData(quizData) {
    if (!quizData) return;

    // Clear existing questions
    document.getElementById('questions-list').innerHTML = '';
    questionCount = 0;
    answerCounts = {};

    // Add questions from quiz data
    if (quizData.questions && quizData.questions.length > 0) {
        quizData.questions.forEach(question => {
            addQuestion(question);
        });
    } else {
        addQuestion();
    }
}

/**
 * Delete a quiz with confirmation
 * @param {string} quizId - The quiz ID to delete
 */
async function deleteQuiz(quizId) {
    if (!confirm('Are you sure you want to delete this quiz? This action cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch(`/quizzes/${quizId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            // Remove the quiz card from the DOM
            const quizCard = document.querySelector(`[data-quiz-id="${quizId}"]`);
            if (quizCard) {
                quizCard.remove();
            }

            // Check if there are no more quizzes
            const remainingQuizzes = document.querySelectorAll('.quiz-card');
            if (remainingQuizzes.length === 0) {
                location.reload();
            }
        } else {
            const errorData = await response.json();
            alert(errorData.detail || 'Failed to delete quiz.');
        }
    } catch (error) {
        alert('An error occurred while deleting the quiz.');
        console.error('Quiz delete error:', error);
    }
}

/**
 * Show an error message for a specific field
 * @param {string} field - Field name
 * @param {string} message - Error message
 */
function showFieldError(field, message) {
    const errorEl = document.getElementById(`${field}-error`);
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.style.display = 'block';
    }
}

/**
 * Show a general form error
 * @param {string} message - Error message
 */
function showFormError(message) {
    const errorEl = document.getElementById('form-error');
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.style.display = 'block';
    }
}

/**
 * Clear all form errors
 */
function clearFormErrors() {
    const errorElements = document.querySelectorAll('.error-message, .form-error');
    errorElements.forEach(el => {
        el.textContent = '';
        el.style.display = 'none';
    });
}

/**
 * Handle API error responses
 * @param {Object} errorData - Error response data
 */
function handleApiError(errorData) {
    if (errorData.detail) {
        if (Array.isArray(errorData.detail)) {
            // Validation errors from Pydantic
            const messages = errorData.detail.map(err => {
                const field = err.loc ? err.loc.join(' > ') : 'Field';
                return `${field}: ${err.msg}`;
            });
            showFormError(messages.join('\n'));
        } else {
            showFormError(errorData.detail);
        }
    } else {
        showFormError('An error occurred. Please check your input and try again.');
    }
}
