'use strict';

const API_URL = 'http://127.0.0.1:5000/api/v1';

/* ═══════════════════════════════════════════════════════════════
   UTILITIES
   ═══════════════════════════════════════════════════════════════ */

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

/**
 * Extract a query-string parameter from the current URL.
 * @param {string} param
 * @returns {string|null}
 */
function getQueryParam(param) {
    return new URLSearchParams(window.location.search).get(param);
}

/* ═══════════════════════════════════════════════════════════════
   LOGIN PAGE  (login.html)
   ═══════════════════════════════════════════════════════════════ */

async function loginUser(email, password) {
    return fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
}

function showLoginError(message) {
    const el = document.getElementById('login-error');
    if (el) { el.textContent = message; el.hidden = false; }
}

function hideLoginError() {
    const el = document.getElementById('login-error');
    if (el) { el.hidden = true; el.textContent = ''; }
}

function initLoginPage() {
    const loginForm = document.getElementById('login-form');
    if (!loginForm) return;

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
                    const err = await response.json();
                    if (err.message) message = err.message;
                } catch (_) { /* keep default */ }
                showLoginError(message);
            }
        } catch (_) {
            showLoginError('Network error. Please try again later.');
        }
    });
}

/* ═══════════════════════════════════════════════════════════════
   INDEX PAGE  (index.html)
   ═══════════════════════════════════════════════════════════════ */

/** All places fetched from the API — kept in memory for client-side filtering. */
let allPlaces = [];

/**
 * Show / hide the login link depending on authentication state,
 * then fetch places either way (GET /places/ is public).
 */
function checkAuthIndex() {
    const token     = getCookie('token');
    const loginLink = document.getElementById('login-link');

    if (loginLink) {
        loginLink.style.display = token ? 'none' : 'block';
    }

    fetchPlaces(token);
}

/**
 * Fetch the full list of places from the API.
 * @param {string|null} token  JWT or null if unauthenticated
 */
async function fetchPlaces(token) {
    const headers = token ? { Authorization: `Bearer ${token}` } : {};

    try {
        const response = await fetch(`${API_URL}/places/`, { headers });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const places = await response.json();
        allPlaces = places;
        displayPlaces(places);
    } catch (err) {
        const list = document.getElementById('places-list');
        if (list) {
            list.innerHTML = '<p class="no-reviews">Could not load places. Please try again later.</p>';
        }
    }
}

/**
 * Render an array of places into #places-list.
 * @param {Array} places
 */
function displayPlaces(places) {
    const list = document.getElementById('places-list');
    if (!list) return;

    list.innerHTML = '';

    if (places.length === 0) {
        list.innerHTML = '<p class="no-reviews">No places match your filter.</p>';
        return;
    }

    places.forEach((place) => {
        const article = document.createElement('article');
        article.className = 'place-card';
        article.dataset.price = place.price;

        article.innerHTML = `
            <h2>${escapeHTML(place.title)}</h2>
            <p class="price">$${place.price} <span>/ night</span></p>
            <footer class="card-footer">
                <a href="place.html?id=${encodeURIComponent(place.id)}" class="details-button">View Details</a>
            </footer>`;

        list.appendChild(article);
    });
}

/**
 * Filter the currently displayed place cards by maximum price.
 * Works purely on the DOM — no extra fetch needed.
 */
function initPriceFilter() {
    const select = document.getElementById('price-filter');
    if (!select) return;

    select.addEventListener('change', (event) => {
        const value = event.target.value;

        if (value === 'all') {
            displayPlaces(allPlaces);
            return;
        }

        const maxPrice = Number(value);
        const filtered = allPlaces.filter((p) => p.price <= maxPrice);
        displayPlaces(filtered);
    });
}

function initIndexPage() {
    if (!document.getElementById('places-list')) return;
    checkAuthIndex();
    initPriceFilter();
}

/* ═══════════════════════════════════════════════════════════════
   PLACE DETAILS PAGE  (place.html)
   ═══════════════════════════════════════════════════════════════ */

/**
 * Extract the place ID from ?id=<uuid> in the URL.
 * @returns {string|null}
 */
function getPlaceIdFromURL() {
    return getQueryParam('id');
}

/**
 * Show / hide the login link and the add-review section based on auth state,
 * then fetch place details.
 */
function checkAuthPlace() {
    const token         = getCookie('token');
    const loginLink     = document.getElementById('login-link');
    const addReview     = document.getElementById('add-review');
    const placeId       = getPlaceIdFromURL();

    if (loginLink) loginLink.style.display = token ? 'none' : 'block';
    if (addReview) addReview.hidden = !token;

    if (!placeId) {
        const el = document.getElementById('place-details');
        if (el) el.innerHTML = '<p class="no-reviews">No place ID specified.</p>';
        return;
    }

    fetchPlaceDetails(token, placeId);
}

/**
 * Fetch full place details + reviews from the API.
 * @param {string|null} token
 * @param {string} placeId
 */
async function fetchPlaceDetails(token, placeId) {
    const headers = token ? { Authorization: `Bearer ${token}` } : {};

    try {
        const [placeRes, reviewsRes] = await Promise.all([
            fetch(`${API_URL}/places/${placeId}`, { headers }),
            fetch(`${API_URL}/places/${placeId}/reviews`, { headers })
        ]);

        if (!placeRes.ok) throw new Error(`Place not found (HTTP ${placeRes.status})`);

        const place   = await placeRes.json();
        const reviews = reviewsRes.ok ? await reviewsRes.json() : [];

        displayPlaceDetails(place);
        displayReviews(reviews);

        /* Attach review form now that we know the placeId */
        initReviewForm(token, placeId);

    } catch (err) {
        const el = document.getElementById('place-details');
        if (el) el.innerHTML = `<p class="no-reviews">${escapeHTML(err.message)}</p>`;
    }
}

/**
 * Render place details into #place-details.
 * @param {Object} place  Full place object from the API
 */
function displayPlaceDetails(place) {
    const container = document.getElementById('place-details');
    if (!container) return;

    const ownerName = place.owner
        ? `${escapeHTML(place.owner.first_name)} ${escapeHTML(place.owner.last_name)}`
        : 'Unknown';

    const amenitiesHTML = (place.amenities && place.amenities.length)
        ? place.amenities.map((a) => `<li>${escapeHTML(a.name)}</li>`).join('')
        : '<li>None listed</li>';

    container.innerHTML = `
        <article class="place-details">
            <header class="place-details-header">
                <h1>${escapeHTML(place.title)}</h1>
                <p class="price">$${place.price} <span>/ night</span></p>
            </header>

            <section class="place-info">
                <div class="place-info-grid">
                    <div class="info-item">
                        <p class="info-label">Host</p>
                        <p class="info-value">${ownerName}</p>
                    </div>
                    <div class="info-item">
                        <p class="info-label">Price per night</p>
                        <p class="info-value">$${place.price}</p>
                    </div>
                    <div class="info-item">
                        <p class="info-label">Latitude</p>
                        <p class="info-value">${place.latitude}</p>
                    </div>
                    <div class="info-item">
                        <p class="info-label">Longitude</p>
                        <p class="info-value">${place.longitude}</p>
                    </div>
                </div>

                <h2 class="section-title">Description</h2>
                <p class="place-description">${escapeHTML(place.description || 'No description available.')}</p>

                <h2 class="section-title">Amenities</h2>
                <ul class="amenities-list">${amenitiesHTML}</ul>
            </section>
        </article>`;

    document.title = `HBNB - ${place.title}`;
}

/**
 * Render reviews into #reviews-list and show the section.
 * @param {Array} reviews
 */
function displayReviews(reviews) {
    const section = document.getElementById('reviews-section');
    const list    = document.getElementById('reviews-list');
    if (!section || !list) return;

    section.hidden = false;
    list.innerHTML = '';

    if (reviews.length === 0) {
        list.innerHTML = '<p class="no-reviews">No reviews yet. Be the first!</p>';
        return;
    }

    reviews.forEach((review) => {
        const stars = buildStars(review.rating);
        const initial = review.user_id ? review.user_id[0].toUpperCase() : '?';

        const article = document.createElement('article');
        article.className = 'review-card';
        article.innerHTML = `
            <div class="review-card-inner">
                <header class="review-header">
                    <div class="reviewer-avatar" aria-hidden="true">${initial}</div>
                    <div>
                        <p class="reviewer-name">Guest</p>
                        <p class="review-date">${formatDate(review.created_at)}</p>
                    </div>
                </header>
                <div class="star-rating" aria-label="Rating: ${review.rating} out of 5">
                    ${stars}
                </div>
                <p class="review-text">${escapeHTML(review.text)}</p>
            </div>`;

        list.appendChild(article);
    });
}

/* ═══════════════════════════════════════════════════════════════
   ADD REVIEW FORM  (place.html — authenticated only)
   ═══════════════════════════════════════════════════════════════ */

function initReviewForm(token, placeId) {
    const form = document.getElementById('review-form');
    if (!form || !token) return;

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const errorEl = document.getElementById('review-error');
        if (errorEl) errorEl.hidden = true;

        const ratingInput = form.querySelector('input[name="rating"]:checked');
        const textInput   = document.getElementById('review-text');

        if (!ratingInput) {
            showReviewError('Please select a rating.');
            return;
        }
        if (!textInput.value.trim()) {
            showReviewError('Please write your review.');
            return;
        }

        try {
            const response = await fetch(`${API_URL}/reviews/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({
                    place_id: placeId,
                    text:     textInput.value.trim(),
                    rating:   Number(ratingInput.value)
                })
            });

            if (response.ok) {
                form.reset();
                /* Reload reviews */
                const reviewsRes = await fetch(`${API_URL}/places/${placeId}/reviews`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                const reviews = reviewsRes.ok ? await reviewsRes.json() : [];
                displayReviews(reviews);
            } else {
                let msg = 'Could not submit review.';
                try { const e = await response.json(); if (e.message) msg = e.message; } catch (_) {}
                showReviewError(msg);
            }
        } catch (_) {
            showReviewError('Network error. Please try again.');
        }
    });
}

function showReviewError(msg) {
    const el = document.getElementById('review-error');
    if (el) { el.textContent = msg; el.hidden = false; }
}

function initPlacePage() {
    if (!document.getElementById('place-details')) return;
    checkAuthPlace();
}

/* ═══════════════════════════════════════════════════════════════
   HELPERS
   ═══════════════════════════════════════════════════════════════ */

/** Build 5 star spans for a numeric rating (1-5). */
function buildStars(rating) {
    return Array.from({ length: 5 }, (_, i) =>
        `<span class="star${i < rating ? '' : ' empty'}" aria-hidden="true">&#9733;</span>`
    ).join('');
}

/** Format an ISO date string to a human-readable month + year. */
function formatDate(isoString) {
    if (!isoString) return '';
    try {
        return new Date(isoString).toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
    } catch (_) {
        return isoString;
    }
}

/** Escape user-supplied strings before injecting into innerHTML. */
function escapeHTML(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

/* ═══════════════════════════════════════════════════════════════
   ADD REVIEW PAGE  (add_review.html — authenticated only)
   ═══════════════════════════════════════════════════════════════ */

/**
 * Check authentication; redirect to index.html if no token found.
 * @returns {string} JWT token
 */
function checkAuthentication() {
    const token = getCookie('token');
    if (!token) {
        window.location.href = 'index.html';
    }
    return token;
}

/**
 * POST a review to the API.
 * @param {string} token
 * @param {string} placeId
 * @param {string} reviewText
 * @param {number} rating
 * @returns {Promise<Response>}
 */
async function submitReview(token, placeId, reviewText, rating) {
    return fetch(`${API_URL}/reviews/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ place_id: placeId, text: reviewText, rating })
    });
}

/**
 * Handle the API response: show success or error feedback.
 * @param {Response} response
 * @param {HTMLFormElement} form
 */
async function handleResponse(response, form) {
    const successEl = document.getElementById('review-success');
    const errorEl   = document.getElementById('review-error');

    if (response.ok) {
        if (errorEl)   { errorEl.hidden = true; errorEl.textContent = ''; }
        if (successEl) { successEl.hidden = false; }
        form.reset();
    } else {
        let msg = 'Failed to submit review.';
        try {
            const data = await response.json();
            if (data.message) msg = data.message;
        } catch (_) { /* keep default */ }
        if (successEl) successEl.hidden = true;
        if (errorEl)   { errorEl.textContent = msg; errorEl.hidden = false; }
    }
}

function initAddReviewPage() {
    const reviewForm = document.getElementById('review-form');
    /* Only run on add_review.html — it has #review-success */
    if (!reviewForm || !document.getElementById('review-success')) return;

    const token   = checkAuthentication();   /* redirects if not logged in */
    const placeId = getPlaceIdFromURL();

    /* Update back-link to return to the correct place */
    const backLink = document.getElementById('back-link');
    if (backLink && placeId) {
        backLink.href = `place.html?id=${encodeURIComponent(placeId)}`;
    }

    /* Fetch and display the place name */
    if (placeId && token) {
        fetch(`${API_URL}/places/${placeId}`, {
            headers: { Authorization: `Bearer ${token}` }
        })
            .then((r) => r.ok ? r.json() : null)
            .then((place) => {
                const nameEl = document.getElementById('place-name');
                if (nameEl && place) nameEl.textContent = place.title;
            })
            .catch(() => {});
    }

    reviewForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const ratingInput = reviewForm.querySelector('input[name="rating"]:checked');
        const textInput   = document.getElementById('review-text');
        const errorEl     = document.getElementById('review-error');
        const successEl   = document.getElementById('review-success');

        /* Reset feedback */
        if (errorEl)   { errorEl.hidden = true;   errorEl.textContent = ''; }
        if (successEl) { successEl.hidden = true; }

        if (!ratingInput) {
            if (errorEl) { errorEl.textContent = 'Please select a rating.'; errorEl.hidden = false; }
            return;
        }
        if (!textInput.value.trim()) {
            if (errorEl) { errorEl.textContent = 'Please write your review.'; errorEl.hidden = false; }
            return;
        }

        if (!placeId) {
            if (errorEl) { errorEl.textContent = 'No place specified. Go back and try again.'; errorEl.hidden = false; }
            return;
        }

        try {
            const response = await submitReview(
                token,
                placeId,
                textInput.value.trim(),
                Number(ratingInput.value)
            );
            await handleResponse(response, reviewForm);
        } catch (_) {
            if (errorEl) { errorEl.textContent = 'Network error. Please try again later.'; errorEl.hidden = false; }
        }
    });
}

/* ═══════════════════════════════════════════════════════════════
   BOOTSTRAP — run the right init depending on the current page
   ═══════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
    initLoginPage();
    initIndexPage();
    initPlacePage();
    initAddReviewPage();
});
