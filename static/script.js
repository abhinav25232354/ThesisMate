button = document.getElementById('question-asking-prompt-button');
right_before = document.querySelector('.right-before');
right_after = document.querySelector('.right-after');

button.addEventListener('click', function () {
    right_before.style.display = 'none';
    right_after.style.display = 'block';
});

// To Handle PDF Upload Toggle
// document.addEventListener("DOMContentLoaded", () => {
//     alert("Welcome to AI Researcher! Please note that this is an early version and may contain bugs. Your feedback is appreciated.");
//     const pdfToggle = document.getElementById('pdf-toggle');
//     if (pdfToggle) {
//         pdfToggle.addEventListener('click', function() {
//             pdfToggle.classList.toggle('on');
//         });
//     }
// });

function togglePDFUpload() {
    const pdfToggle = document.getElementById('pdf-toggle');
    const inputField = document.querySelector(".question-asking-prompt");
    const uploadButton = document.querySelector(".service-toggle-pdfUpload");
        if (!pdfToggle.classList.contains('on')) {
            pdfToggle.classList.add('on');
            inputField.placeholder = "Please upload a PDF or Paste Link Here...";
            // uploadButton.style.display = "block";

        } else {
            pdfToggle.classList.remove('on');
            inputField.placeholder = "Type your question here...";
            // uploadButton.style.display = "none";
        }
}

// const answerDiv = document.getElementById("answer-para");
// // Assuming `responseText` is your API's markdown output
// answerDiv.innerHTML = marked.parse(responseText);


function toggleAbout() {
    let fadeInterval; // global int erval to prevent multiple intervals
    const about = document.querySelector('.about');
    const form = document.querySelector('.question-asking-whole-form');
    clearInterval(fadeInterval); // stop any ongoing animation

    // Get current computed opacity
    let currentOpacity = parseFloat(getComputedStyle(about).opacity);
    if (isNaN(currentOpacity)) currentOpacity = 1; // default to 1 if not set

    if (currentOpacity > 0) {
        // fade out
        let opacity = currentOpacity;
        fadeInterval = setInterval(() => {
            opacity -= 0.05;
            if (opacity <= 0) opacity = 0;
            about.style.opacity = opacity;
            if (opacity === 0) {
                clearInterval(fadeInterval);
                about.style.display = 'none';
                form.style.display = 'block';
            }
        }, 20);
    } else {
        // fade in
        about.style.display = 'block';
        form.style.display = 'none';
        let opacity = 0;
        fadeInterval = setInterval(() => {
            opacity += 0.05;
            if (opacity >= 1) opacity = 1;
            about.style.opacity = opacity;
            if (opacity === 1) {
                clearInterval(fadeInterval);
            }
        }, 20);
    }
}
