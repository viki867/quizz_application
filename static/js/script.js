// ====== Simple JS for Quiz Page ======

// Timer countdown (optional)
function startTimer(duration, display) {
    let timer = duration, minutes, seconds;
    let countdown = setInterval(function () {
        minutes = parseInt(timer / 60, 10);
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.textContent = minutes + ":" + seconds;

        if (--timer < 0) {
            clearInterval(countdown);
            alert("Time's up!");
            // Optionally auto-submit quiz
        }
    }, 1000);
}

// Example usage (on quiz page)
window.onload = function () {
    let timerDisplay = document.querySelector('#timer');
    if (timerDisplay) {
        let duration = 60 * 5; // 5 minutes
        startTimer(duration, timerDisplay);
    }
};

// Simple alert for buttons
document.querySelectorAll('.btn-custom').forEach(btn => {
    btn.addEventListener('click', () => {
        console.log('Button clicked:', btn.textContent);
    });
});
