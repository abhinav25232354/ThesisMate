button = document.getElementById('question-asking-prompt-button');
right_before = document.querySelector('.right-before');
right_after = document.querySelector('.right-after');

button.addEventListener('click', function() {
    right_before.style.display = 'none';
    right_after.style.display = 'block';
});