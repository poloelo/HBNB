document.addEventListener('DOMContentLoaded', () => {
    const token = getCookie('token');
    const placeId = getPlaceIdFromURL();

    // Redirect unauthenticated users to the index page
    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    // Update the back link to return to the correct place page
    const backLink = document.querySelector('.back-link');
    if (backLink && placeId) {
        backLink.href = `place.html?id=${placeId}`;
    }

    const form = document.getElementById('review-form');
    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const comment = document.getElementById('comment').value;
        const rating = document.querySelector('input[name="rating"]:checked');

        if (!rating) {
            alert('Please select a rating.');
            return;
        }

        await submitReview(token, placeId, comment, parseInt(rating.value));
    });
});

function getCookie(name) {
    const value = document.cookie
        .split('; ')
        .find(row => row.startsWith(name + '='));
    return value ? value.split('=')[1] : null;
}

function getPlaceIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
}

async function submitReview(token, placeId, reviewText, rating) {
    try {
        const response = await fetch('http://localhost:5001/api/v1/reviews/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                text: reviewText,
                rating: rating,
                place_id: placeId
            })
        });

        handleResponse(response, placeId);
    } catch (error) {
        alert('Network error: ' + error.message);
    }
}

async function handleResponse(response, placeId) {
    if (response.ok) {
        alert('Review submitted successfully!');
        document.getElementById('review-form').reset();
        window.location.href = `place.html?id=${placeId}`;
    } else {
        const data = await response.json().catch(() => ({}));
        const message = data.message || data.msg || response.statusText;
        alert('Failed to submit review: ' + message);
    }
}
