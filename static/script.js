button = document.getElementById('question-asking-prompt-button');
right_before = document.querySelector('.right-before');
right_after = document.querySelector('.right-after');

button.addEventListener('click', function() {
    right_before.style.display = 'none';
    right_after.style.display = 'block';
});

// Get the raw markdown passed from Flask
const rawMarkdown = `{{ answer | safe }}`;

// Convert it into HTML using marked.js
document.querySelector(".answer").innerHTML = marked.parse(rawMarkdown);