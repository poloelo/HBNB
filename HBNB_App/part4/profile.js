document.addEventListener('DOMContentLoaded', () => {
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

    loadProfile(token, payload.sub, payload.is_admin);
});

// ── Helpers ─────────────────────────────────────────────────────────────────

function getCookie(name) {
    const entry = document.cookie.split('; ').find(r => r.startsWith(name + '='));
    return entry ? entry.split('=')[1] : null;
}

/**
 * Décode la partie payload d'un JWT (sans vérification de signature).
 * Flask-JWT-Extended place l'identity dans la claim 'sub'.
 */
function parseJWT(token) {
    try {
        const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
        return JSON.parse(atob(base64));
    } catch (e) {
        return null;
    }
}

// ── Chargement des données ───────────────────────────────────────────────────

async function loadProfile(token, userId, isAdmin) {
    try {
        const headers = { 'Authorization': `Bearer ${token}` };

        // Requêtes parallèles : infos utilisateur + liste des lieux
        const [userRes, placesRes] = await Promise.all([
            fetch(`http://localhost:5001/api/v1/users/${userId}`, { headers }),
            fetch('http://localhost:5001/api/v1/places/')
        ]);

        if (!userRes.ok) {
            showError('Impossible de charger le profil.');
            return;
        }

        const user       = await userRes.json();
        const placesList = placesRes.ok ? await placesRes.json() : [];

        // On récupère les détails complets de chaque lieu (owner_id inclus)
        // en parallèle pour filtrer ceux appartenant à l'utilisateur
        const fullPlaces = await Promise.all(
            placesList.map(p =>
                fetch(`http://localhost:5001/api/v1/places/${p.id}`)
                    .then(r => r.ok ? r.json() : null)
                    .catch(() => null)
            )
        );

        const myPlaces = fullPlaces.filter(p => p && p.owner && p.owner.id === userId);

        displayProfile(user, myPlaces, isAdmin);

    } catch (err) {
        console.error('Erreur chargement profil :', err);
        showError('Erreur réseau, veuillez réessayer.');
    }
}

// ── Rendu ────────────────────────────────────────────────────────────────────

function displayProfile(user, places, isAdmin) {
    const initial    = (user.first_name?.[0] || 'U').toUpperCase();
    const memberSince = user.created_at
        ? new Date(user.created_at).toLocaleDateString('fr-FR', { year: 'numeric', month: 'long' })
        : '';

    // Carte d'identité
    document.getElementById('profile-header').innerHTML = `
        <div class="profile-avatar">${initial}</div>
        <div class="profile-info">
            <h1>${user.first_name} ${user.last_name}</h1>
            <p class="email">${user.email}</p>
            <span class="badge${isAdmin ? ' admin' : ''}">
                ${isAdmin ? '⭐ Administrateur' : 'Membre'}
                ${memberSince ? ' · depuis ' + memberSince : ''}
            </span>
        </div>
        <div class="profile-actions">
            <a href="create_place.html" class="btn-primary" style="width:auto; padding:10px 20px;">
                + Créer un lieu
            </a>
        </div>
    `;

    // Lieux publiés
    const placesSection = document.getElementById('my-places');
    if (places.length === 0) {
        placesSection.outerHTML = `
            <div class="empty-state">
                <p>Vous n'avez encore publié aucun lieu.</p>
                <a href="create_place.html" class="details-button">Créer mon premier lieu</a>
            </div>
        `;
        return;
    }

    placesSection.innerHTML = places.map(p => `
        <article class="place-card">
            <h3>${p.title}</h3>
            <p class="price">$${p.price} / nuit</p>
            <a href="place.html?id=${p.id}" class="details-button">Voir les détails</a>
        </article>
    `).join('');
}

function showError(message) {
    document.getElementById('profile-header').innerHTML = `
        <div class="profile-info">
            <p style="color: #EF4444;">${message}</p>
        </div>
    `;
}
