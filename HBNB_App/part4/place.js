document.addEventListener('DOMContentLoaded', () => {
    const placeId = getPlaceIdFromURL();
    if (!placeId) {
        window.location.href = 'index.html';
        return;
    }
    checkAuthentication(placeId);
});

function getPlaceIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
}

function getCookie(name) {
    const value = document.cookie
        .split('; ')
        .find(row => row.startsWith(name + '='));
    return value ? value.split('=')[1] : null;
}

function checkAuthentication(placeId) {
    const token = getCookie('token');
    const addReview = document.getElementById('add-review');
    const loginLink = document.getElementById('login-link');

    if (!token) {
        addReview.style.display = 'none';
        loginLink.style.display = 'block';
    } else {
        addReview.style.display = 'block';
        loginLink.style.display = 'none';
    }
    fetchPlaceDetails(token, placeId);
}

async function fetchPlaceDetails(token, placeId) {
    try {
        const headers = {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        // Fetch place details and reviews in parallel
        const [placeRes, reviewsRes] = await Promise.all([
            fetch(`http://localhost:5001/api/v1/places/${placeId}`, { headers }),
            fetch(`http://localhost:5001/api/v1/places/${placeId}/reviews`, { headers })
        ]);

        if (placeRes.ok) {
            const place = await placeRes.json();
            const reviews = reviewsRes.ok ? await reviewsRes.json() : [];
            displayPlaceDetails(place, reviews);
        } else {
            console.error('Failed to fetch place details');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function displayPlaceDetails(place, reviews) {
    const details = document.getElementById('place-details');
    const hostName = place.owner
        ? `${place.owner.first_name} ${place.owner.last_name}`
        : 'Unknown';

    details.innerHTML = `
        <h1>${place.title}</h1>
        <div class="place-info">
            <div class="info-item">
                <p class="label">Host</p>
                <p class="value">${hostName}</p>
            </div>
            <div class="info-item">
                <p class="label">Price per night</p>
                <p class="value accent">$${place.price}</p>
            </div>
            <div class="info-item">
                <p class="label">Location</p>
                <p class="value">${place.latitude}, ${place.longitude}</p>
            </div>
        </div>
        <p class="description">${place.description || 'No description available.'}</p>
        <h2>Amenities</h2>
        <ul class="amenities">
            ${place.amenities && place.amenities.length > 0
                ? place.amenities.map(a => `<li class="amenity-tag">${a.name}</li>`).join('')
                : '<li>No amenities listed.</li>'
            }
        </ul>
    `;

    const reviewsList = document.getElementById('reviews-list');
    if (reviews && reviews.length > 0) {
        reviewsList.innerHTML = reviews.map(r => `
            <div class="review-card">
                <div class="reviewer">
                    <div class="reviewer-avatar">${r.user_name ? r.user_name[0].toUpperCase() : 'U'}</div>
                    <span class="reviewer-name">${r.user_name || 'Anonymous'}</span>
                </div>
                <p class="review-rating">${'★'.repeat(r.rating)}${'☆'.repeat(5 - r.rating)} ${r.rating}/5</p>
                <p class="review-comment">${r.text}</p>
            </div>
        `).join('');
    } else {
        reviewsList.innerHTML = '<p>No reviews yet.</p>';
    }

    // Set the add-review link with the correct place ID
    const addReviewDiv = document.getElementById('add-review');
    addReviewDiv.innerHTML = `<a href="add_review.html?id=${place.id}" class="details-button">Add a Review</a>`;
}
