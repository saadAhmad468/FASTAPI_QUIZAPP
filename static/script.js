// static/script.js
document.addEventListener('DOMContentLoaded', function() {
    // Handle login form submission
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}&grant_type=password`
                });
                
                if (!response.ok) {
                    throw new Error('Login failed');
                }
                
                const data = await response.json();
                localStorage.setItem('access_token', data.access_token);
                window.location.href = '/dashboard';
            } catch (error) {
                document.getElementById('login-message').textContent = 'Login failed. Please try again.';
                console.error('Error:', error);
            }
        });
    }
});

// Add this to your existing script.js
document.addEventListener('DOMContentLoaded', function() {
    // Admin form submission
    const addQuestionForm = document.getElementById('addQuestionForm');
    if (addQuestionForm) {
        addQuestionForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const token = localStorage.getItem('access_token');

            const questionData = {
                category: document.getElementById('category').value,
                question_text: document.getElementById('questionText').value,
                correct_answer: document.getElementById('correctAnswer').value
            };

            try {
                const response = await fetch('/admin/add-question', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(questionData)
                });

                if (!response.ok) {
                    throw new Error('Failed to add question');
                }

                alert('Question added successfully!');
                location.reload();
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to add question');
            }
        });
    }
});