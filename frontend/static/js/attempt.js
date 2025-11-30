/**
 * Quiz taking JavaScript
 * Handles answer selection, validation, and submission
 */

// Track selected answers: { question_id: answer_id }
let selectedAnswers = {};

/**
 * Initialize quiz taking functionality
 */
function initQuizTaking() {
    const form = document.getElementById('quiz-form');

    if (form) {
        // Set up answer selection handlers
        setupAnswerSelections();

        // Set up form submission
        form.addEventListener('submit', handleQuizSubmit);
    }
}

/**
 * Set up click handlers for answer options
 */
function setupAnswerSelections() {
    const answerOptions = document.querySelectorAll('.answer-option');

    answerOptions.forEach(option => {
        option.addEventListener('click', function(e) {
            // Don't trigger twice if clicking directly on radio
            if (e.target.classList.contains('answer-radio')) {
                handleAnswerSelect(this);
                return;
            }

            // Select the radio button
            const radio = this.querySelector('.answer-radio');
            if (radio) {
                radio.checked = true;
                handleAnswerSelect(this);
            }
        });
    });

    // Also handle direct radio changes
    const radios = document.querySelectorAll('.answer-radio');
    radios.forEach(radio => {
        radio.addEventListener('change', function() {
            handleAnswerSelect(this.closest('.answer-option'));
        });
    });
}

/**
 * Handle answer selection
 * @param {Element} answerOption - The clicked answer option element
 */
function handleAnswerSelect(answerOption) {
    const questionBlock = answerOption.closest('.question-block');
    const questionId = questionBlock.dataset.questionId;
    const answerId = answerOption.dataset.answerId;

    // Update tracking
    selectedAnswers[questionId] = answerId;

    // Update visual feedback
    updateAnswerVisuals(questionBlock, answerId);

    // Clear any error messages
    clearFormError();
}

/**
 * Update visual styling for selected answer
 * @param {Element} questionBlock - The question block element
 * @param {string} selectedAnswerId - The selected answer ID
 */
function updateAnswerVisuals(questionBlock, selectedAnswerId) {
    const allOptions = questionBlock.querySelectorAll('.answer-option');

    allOptions.forEach(option => {
        if (option.dataset.answerId === selectedAnswerId) {
            option.classList.add('selected');
        } else {
            option.classList.remove('selected');
        }
    });
}

/**
 * Handle quiz form submission
 * @param {Event} event - Form submit event
 */
async function handleQuizSubmit(event) {
    event.preventDefault();
    clearFormError();

    const form = event.target;
    const attemptId = form.dataset.attemptId;

    // Validate all questions answered
    const questionBlocks = document.querySelectorAll('.question-block');
    const unansweredQuestions = [];

    questionBlocks.forEach((block, index) => {
        const questionId = block.dataset.questionId;
        if (!selectedAnswers[questionId]) {
            unansweredQuestions.push(index + 1);
        }
    });

    if (unansweredQuestions.length > 0) {
        showFormError(
            `Please answer all questions. Unanswered: Question${unansweredQuestions.length > 1 ? 's' : ''} ${unansweredQuestions.join(', ')}`
        );
        return;
    }

    // Build submission data
    const answers = Object.entries(selectedAnswers).map(([questionId, answerId]) => ({
        question_id: questionId,
        selected_answer_id: answerId,
    }));

    // Disable submit button
    const submitBtn = document.getElementById('submit-btn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';

    try {
        const response = await fetch(`/attempts/${attemptId}/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ answers }),
        });

        if (response.ok) {
            // Redirect to results page
            window.location.href = `/results/${attemptId}`;
        } else {
            const errorData = await response.json();
            showFormError(errorData.detail || 'Failed to submit quiz. Please try again.');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Quiz';
        }
    } catch (error) {
        showFormError('An error occurred while submitting. Please try again.');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Quiz';
        console.error('Quiz submit error:', error);
    }
}

/**
 * Show form error message
 * @param {string} message - Error message to display
 */
function showFormError(message) {
    const errorEl = document.getElementById('form-error');
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.style.display = 'block';
    }
}

/**
 * Clear form error message
 */
function clearFormError() {
    const errorEl = document.getElementById('form-error');
    if (errorEl) {
        errorEl.textContent = '';
        errorEl.style.display = 'none';
    }
}
