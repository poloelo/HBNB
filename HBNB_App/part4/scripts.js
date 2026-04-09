document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault(); // empêche le rechargement de la page

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            await loginUser(email, password);
        });
    }
});

async function loginUser(email, password) {
    try {
        const response = await fetch('http://localhost:5001/api/v1/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        if (response.ok) {
            const data = await response.json();
            // Stocke le JWT dans un cookie accessible partout sur le site
            document.cookie = `token=${data.access_token}; path=/`;
            window.location.href = 'index.html'; // redirect
        } else {
            alert('Login failed: ' + response.statusText);
        }
    } catch (error) {
        alert('Network error: ' + error.message);
    }
}