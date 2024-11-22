// Obsługa logowania
document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const response = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });

    const result = await response.json();
    const message = document.getElementById('message');
    if (response.ok) {
        message.textContent = 'Zalogowano pomyślnie!';
    } else {
        message.textContent = result.error || 'Wystąpił błąd logowania.';
    }
});

// Obsługa generowania sygnatur
document.getElementById('generateButton')?.addEventListener('click', async () => {
    const response = await fetch('/generate', { method: 'GET' });
    const result = await response.json();

    const signatureElement = document.getElementById('signature');
    if (response.ok) {
        signatureElement.textContent = `Twoja sygnatura: ${result.signature}`;
    } else {
        signatureElement.textContent = result.error || 'Wystąpił błąd.';
    }
});
