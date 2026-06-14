document.getElementById('loginForm').addEventListener('submit', async function(event) {
    event.preventDefault(); // Prevent the form from submitting the traditional way

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const messageElement = document.getElementById('message');

    // The login endpoint expects form data, not JSON.
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    try {
        const response = await fetch('http://127.0.0.1:8000/auth/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData,
        });

        if (!response.ok) {
            throw new Error('Login failed! Please check your credentials.');
        }

        const data = await response.json();
        
        // IMPORTANT: Store the token in the browser's local storage
        localStorage.setItem('accessToken', data.access_token);
        
        messageElement.textContent = 'Login successful! Redirecting...';
        
        // Redirect to the main admin page after a successful login
         window.location.href = 'admin_dashboard.html'; 

    } catch (error) {
        messageElement.textContent = error.message;
    }
});