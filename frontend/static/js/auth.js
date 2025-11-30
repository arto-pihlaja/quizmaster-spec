/**
 * Authentication JavaScript
 * Handles form submission and validation for auth pages
 */

/**
 * Show error message on form
 * @param {string} message - Error message to display
 */
function showFormError(message) {
    const errorEl = document.getElementById('form-error');
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.style.display = 'block';
    }
    const successEl = document.getElementById('form-success');
    if (successEl) {
        successEl.style.display = 'none';
    }
}

/**
 * Show success message on form
 * @param {string} message - Success message to display
 */
function showFormSuccess(message) {
    const successEl = document.getElementById('form-success');
    if (successEl) {
        successEl.textContent = message;
        successEl.style.display = 'block';
    }
    const errorEl = document.getElementById('form-error');
    if (errorEl) {
        errorEl.style.display = 'none';
    }
}

/**
 * Clear form messages
 */
function clearFormMessages() {
    const errorEl = document.getElementById('form-error');
    if (errorEl) {
        errorEl.style.display = 'none';
    }
    const successEl = document.getElementById('form-success');
    if (successEl) {
        successEl.style.display = 'none';
    }
}

/**
 * Validate password strength
 * @param {string} password - Password to validate
 * @returns {string|null} Error message or null if valid
 */
function validatePassword(password) {
    if (password.length < 8) {
        return 'Password must be at least 8 characters long';
    }
    if (!/[A-Z]/.test(password)) {
        return 'Password must contain at least one uppercase letter';
    }
    if (!/[a-z]/.test(password)) {
        return 'Password must contain at least one lowercase letter';
    }
    if (!/\d/.test(password)) {
        return 'Password must contain at least one digit';
    }
    return null;
}

/**
 * Initialize login form
 */
function initLoginForm() {
    const form = document.getElementById('login-form');
    if (!form) return;

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        clearFormMessages();

        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const submitBtn = document.getElementById('submit-btn');

        if (!email || !password) {
            showFormError('Please fill in all fields');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'Logging in...';

        try {
            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            });

            if (response.ok) {
                // Redirect to home or previous page
                const urlParams = new URLSearchParams(window.location.search);
                const redirectUrl = urlParams.get('redirect') || '/';
                window.location.href = redirectUrl;
            } else {
                const data = await response.json();
                if (response.status === 429) {
                    showFormError('Account locked. Please try again later.');
                } else {
                    showFormError(data.detail || 'Invalid credentials');
                }
                submitBtn.disabled = false;
                submitBtn.textContent = 'Login';
            }
        } catch (error) {
            showFormError('An error occurred. Please try again.');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Login';
        }
    });
}

/**
 * Initialize register form
 */
function initRegisterForm() {
    const form = document.getElementById('register-form');
    if (!form) return;

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        clearFormMessages();

        const email = document.getElementById('email').value.trim();
        const displayName = document.getElementById('display_name').value.trim();
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm_password').value;
        const submitBtn = document.getElementById('submit-btn');

        // Validation
        if (!email || !displayName || !password || !confirmPassword) {
            showFormError('Please fill in all fields');
            return;
        }

        if (password !== confirmPassword) {
            showFormError('Passwords do not match');
            return;
        }

        const passwordError = validatePassword(password);
        if (passwordError) {
            showFormError(passwordError);
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'Creating account...';

        try {
            const response = await fetch('/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email,
                    password,
                    display_name: displayName,
                }),
            });

            if (response.ok) {
                // Registration successful, redirect to home
                window.location.href = '/';
            } else {
                const data = await response.json();
                if (response.status === 409) {
                    showFormError('This email is already registered');
                } else {
                    showFormError(data.detail || 'Registration failed');
                }
                submitBtn.disabled = false;
                submitBtn.textContent = 'Create Account';
            }
        } catch (error) {
            showFormError('An error occurred. Please try again.');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Create Account';
        }
    });
}

/**
 * Initialize forgot password form
 */
function initForgotPasswordForm() {
    const form = document.getElementById('forgot-password-form');
    if (!form) return;

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        clearFormMessages();

        const email = document.getElementById('email').value.trim();
        const submitBtn = document.getElementById('submit-btn');

        if (!email) {
            showFormError('Please enter your email');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'Sending...';

        try {
            const response = await fetch('/auth/forgot-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email }),
            });

            const data = await response.json();

            if (response.ok) {
                showFormSuccess(data.message);
                form.reset();
            } else {
                showFormError(data.detail || 'Failed to send reset email');
            }
        } catch (error) {
            showFormError('An error occurred. Please try again.');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Send Reset Link';
        }
    });
}

/**
 * Initialize reset password form
 */
function initResetPasswordForm() {
    const form = document.getElementById('reset-password-form');
    if (!form) return;

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        clearFormMessages();

        const token = form.dataset.token;
        const newPassword = document.getElementById('new_password').value;
        const confirmPassword = document.getElementById('confirm_password').value;
        const submitBtn = document.getElementById('submit-btn');

        // Validation
        if (!newPassword || !confirmPassword) {
            showFormError('Please fill in all fields');
            return;
        }

        if (newPassword !== confirmPassword) {
            showFormError('Passwords do not match');
            return;
        }

        const passwordError = validatePassword(newPassword);
        if (passwordError) {
            showFormError(passwordError);
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'Resetting...';

        try {
            const response = await fetch('/auth/reset-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    token,
                    new_password: newPassword,
                }),
            });

            const data = await response.json();

            if (response.ok) {
                showFormSuccess(data.message + ' Redirecting to login...');
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            } else {
                showFormError(data.detail || 'Failed to reset password');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Reset Password';
            }
        } catch (error) {
            showFormError('An error occurred. Please try again.');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Reset Password';
        }
    });
}

/**
 * Initialize profile form
 */
function initProfileForm() {
    const form = document.getElementById('profile-form');
    if (!form) return;

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        clearFormMessages();

        const displayName = document.getElementById('display_name').value.trim();
        const submitBtn = document.getElementById('submit-btn');

        if (!displayName) {
            showFormError('Display name cannot be empty');
            return;
        }

        if (displayName.length > 50) {
            showFormError('Display name must be 50 characters or less');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'Saving...';

        try {
            const response = await fetch('/profile', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ display_name: displayName }),
            });

            if (response.ok) {
                showFormSuccess('Profile updated successfully');
            } else {
                const data = await response.json();
                showFormError(data.detail || 'Failed to update profile');
            }
        } catch (error) {
            showFormError('An error occurred. Please try again.');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Save Changes';
        }
    });
}
