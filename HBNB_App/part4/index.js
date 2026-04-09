document.addEventListener('DOMContentLoaded', () => {
    checkAuthentication();

    document.getElementById('price-filter').addEventListener('change', (event) => {
        applyPriceFilter(event.target.value);
    });
});

function getCookie(name) {
    const value = document.cookie
        .split('; ')
        .find(row => row.startsWith(name + '='));
    return value ? value.split('=')[1] : null;
}

function checkAuthentication() {
    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');

    if (!token) {
        loginLink.style.display = 'block';
    } else {
        loginLink.style.display = 'none';
    }
    // Fetch places for all visitors (the GET endpoint is public)
    fetchPlaces(token);
}

async function fetchPlaces(token) {
    try {
        const headers = {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        const response = await fetch('http://localhost:5001/api/v1/places/', {
            method: 'GET',
            headers: headers
        });
        if (response.ok) {
            const places = await response.json();
            displayPlaces(places);
        }
    } catch (error) {
        console.error('Error fetching places:', error);
    }
}

function displayPlaces(places) {
    const placesList = document.getElementById('places-list');
    placesList.innerHTML = '';

    places.forEach(place => {
        const card = document.createElement('article');
        card.className = 'place-card';
        card.dataset.price = place.price;
        card.innerHTML = `
            <h3>${place.title}</h3>
            <p class="price">$${place.price} / night</p>
            <a href="place.html?id=${place.id}" class="details-button">View Details</a>
        `;
        placesList.appendChild(card);
    });

    // Apply current filter value immediately after rendering
    const currentFilter = document.getElementById('price-filter').value;
    applyPriceFilter(currentFilter);
}

function applyPriceFilter(selected) {
    const cards = document.querySelectorAll('.place-card');
    cards.forEach(card => {
        const price = parseFloat(card.dataset.price);
        if (selected === 'all' || price <= parseFloat(selected)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}
