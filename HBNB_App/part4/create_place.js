document.addEventListener('DOMContentLoaded', async () => {
    const token = getCookie('token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    const payload = parseJWT(token);
    if (!payload || !payload.sub) {
        window.location.href = 'login.html';
        return;
    }

    // Charger les équipements pour les cases à cocher
    await loadAmenities();

    // Soumettre le formulaire
    document.getElementById('create-place-form').addEventListener('submit', (e) => {
        e.preventDefault();
        submitPlace(token, payload.sub);
    });
});

// ── Helpers ──────────────────────────────────────────────────────────────────

function getCookie(name) {
    const entry = document.cookie.split('; ').find(r => r.startsWith(name + '='));
    return entry ? entry.split('=')[1] : null;
}

function parseJWT(token) {
    try {
        const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
        return JSON.parse(atob(base64));
    } catch (e) {
        return null;
    }
}

function showError(message) {
    const el = document.getElementById('form-error');
    el.textContent = message;
    el.style.display = 'block';
    el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideError() {
    document.getElementById('form-error').style.display = 'none';
}

// ── Équipements ───────────────────────────────────────────────────────────────

async function loadAmenities() {
    const container = document.getElementById('amenities-container');
    try {
        const res = await fetch('http://localhost:5001/api/v1/amenities/');
        if (!res.ok) {
            container.innerHTML = '<p class="field-hint">Impossible de charger les équipements.</p>';
            return;
        }
        const amenities = await res.json();
        if (amenities.length === 0) {
            container.innerHTML = '<p class="field-hint">Aucun équipement disponible.</p>';
            return;
        }
        container.innerHTML = amenities.map(a => `
            <label class="amenity-checkbox">
                <input type="checkbox" name="amenity" value="${a.id}" />
                <span>${a.name}</span>
            </label>
        `).join('');
    } catch (e) {
        container.innerHTML = '<p class="field-hint">Erreur réseau lors du chargement des équipements.</p>';
    }
}

// ── Soumission ────────────────────────────────────────────────────────────────

async function submitPlace(token, ownerId) {
    hideError();

    const title       = document.getElementById('title').value.trim();
    const description = document.getElementById('description').value.trim();
    const priceRaw    = document.getElementById('price').value;
    const latRaw      = document.getElementById('latitude').value;
    const lngRaw      = document.getElementById('longitude').value;

    const price     = parseFloat(priceRaw);
    const latitude  = parseFloat(latRaw);
    const longitude = parseFloat(lngRaw);

    // Validation côté client
    if (!title) {
        showError('Le titre est obligatoire.');
        return;
    }
    if (isNaN(price) || price <= 0) {
        showError('Le prix doit être un nombre positif.');
        return;
    }
    if (isNaN(latitude) || latitude < -90 || latitude > 90) {
        showError('La latitude doit être comprise entre -90 et 90.');
        return;
    }
    if (isNaN(longitude) || longitude < -180 || longitude > 180) {
        showError('La longitude doit être comprise entre -180 et 180.');
        return;
    }

    const amenityIds = Array.from(
        document.querySelectorAll('input[name="amenity"]:checked')
    ).map(cb => cb.value);

    try {
        const res = await fetch('http://localhost:5001/api/v1/places/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                title,
                description,
                price,
                latitude,
                longitude,
                owner_id: ownerId,
                amenities: amenityIds
            })
        });

        if (res.ok) {
            const place = await res.json();
            window.location.href = `place.html?id=${place.id}`;
        } else {
            const data   = await res.json().catch(() => ({}));
            const msg    = data.message || data.msg || `Erreur ${res.status}`;
            showError('Impossible de créer le lieu : ' + msg);
        }
    } catch (err) {
        showError('Erreur réseau : ' + err.message);
    }
}
