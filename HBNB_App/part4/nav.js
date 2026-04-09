/**
 * nav.js — Gestion de la navigation selon l'état d'authentification
 *
 * Affiche/masque automatiquement les liens de navigation en fonction
 * de la présence du cookie JWT 'token'.
 *
 * Inclure ce script dans TOUTES les pages HTML, avant le script spécifique
 * à chaque page :
 *   <script src="nav.js"></script>
 */
(function () {
    function getCookie(name) {
        const entry = document.cookie.split('; ').find(r => r.startsWith(name + '='));
        return entry ? entry.split('=')[1] : null;
    }

    document.addEventListener('DOMContentLoaded', function () {
        const token = getCookie('token');

        const loginLink    = document.getElementById('login-link');
        const profileLink  = document.getElementById('profile-link');
        const addPlaceLink = document.getElementById('add-place-link');
        const logoutLink   = document.getElementById('logout-link');

        if (token) {
            // Connecté : masquer Login, montrer les actions utilisateur
            if (loginLink)    loginLink.style.display    = 'none';
            if (profileLink)  profileLink.style.display  = 'inline-flex';
            if (addPlaceLink) addPlaceLink.style.display = 'inline-flex';
            if (logoutLink)   logoutLink.style.display   = 'inline-flex';
        } else {
            // Non connecté : afficher Login, masquer les actions utilisateur
            if (loginLink)    loginLink.style.display    = '';
            if (profileLink)  profileLink.style.display  = 'none';
            if (addPlaceLink) addPlaceLink.style.display = 'none';
            if (logoutLink)   logoutLink.style.display   = 'none';
        }

        // Gestion du clic Déconnexion
        if (logoutLink) {
            logoutLink.addEventListener('click', function (e) {
                e.preventDefault();
                document.cookie = 'token=; max-age=0; path=/';
                window.location.href = 'index.html';
            });
        }
    });
}());
