'use strict';

const API_URL = 'http://127.0.0.1:5000/api/v1';

/* ── Utilities ────────────────────────────────────────────────────────────── */

/**
 * Read a single cookie value by name.
 * @param {string} name
 * @returns {string|null}
 */
function getCookie(name) {
    const match = document.cookie
        .split('; ')
        .find((row) => row.startsWith(name + '='));
    return match ? decodeURIComponent(match.split('=')[1]) : null;
}

/**
 * Write a cookie.
 * @param {string} name
 * @param {string} value
 * @param {string} [path='/']
 */
function setCookie(name, value, path = '/') {
    document.cookie = `${name}=${encodeURIComponent(value)}; path=${path}`;
}

/* ── Login page ───────────────────────────────────────────────────────────── */

/**
 * POST credentials to the login endpoint.
 * @param {string} email
 * @param {string} password
 * @returns {Promise<Response>}
 */
async function loginUser(email, password) {
    const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
    });
    return response;
}

/**
 * Show an error inside the login form.
 * @param {string} message
 */
function showLoginError(message) {
    const errorEl = document.getElementById('login-error');
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.hidden = false;
    }
}

function hideLoginError() {
    const errorEl = document.getElementById('login-error');
    if (errorEl) {
        errorEl.hidden = true;
        errorEl.textContent = '';
    }
}

/* ── Bootstrap ────────────────────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
    /* ── Login form ── */
    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            hideLoginError();

            const email    = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;

            if (!email || !password) {
                showLoginError('Please enter your email and password.');
                return;
            }

            try {
                const response = await loginUser(email, password);

                if (response.ok) {
                    const data = await response.json();
                    setCookie('token', data.access_token);
                    window.location.href = 'index.html';
                } else {
                    let message = 'Login failed. Please check your credentials.';
                    try {
                        const errData = await response.json();
                        if (errData.message) {
                            message = errData.message;
                        }
                    } catch (_) { /* keep default message */ }
                    showLoginError(message);
                }
            } catch (err) {
                showLoginError('Network error. Please try again later.');
            }
        });
    }
});
