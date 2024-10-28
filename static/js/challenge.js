document.querySelectorAll('.start-button').forEach(button => {
    button.addEventListener('click', () => {
        const time = parseInt(button.getAttribute('data-time'), 10);
        const sets = parseInt(button.getAttribute('data-sets'), 10);
        
        startTimer(time, sets);
    });
});

function startTimer(time, sets) {
    const progressContainer = document.getElementById('progress-container');
    const setMessage = document.getElementById('set-message');
    const finishedButton = document.getElementById('finished-button');
    const rewardMessage = document.getElementById('reward-message'); // Add a reference to the reward message element

    // Clear any existing progress bars
    progressContainer.innerHTML = '';
    
    // Show the timer container
    const timerContainer = document.getElementById('timer-container');
    timerContainer.classList.remove('hidden');

    let currentSet = 1;

    function runSet() {
        // Create a new progress bar for the current set
        const progressBar = document.createElement('div');
        progressBar.classList.add('progress-bar');
        progressBar.style.width = '100%'; // Reset the progress bar width
        progressContainer.appendChild(progressBar);

        let currentTime = time; // Current time starts at set time

        const interval = setInterval(() => {
            currentTime--;

            // Calculate the percentage of time left
            const percent = (currentTime / time) * 100;
            progressBar.style.width = percent + '%';

            // Update the set message with the remaining time
            setMessage.textContent = `Set ${currentSet} remaining: ${currentTime} seconds left`;

            if (currentTime <= 0) {
                clearInterval(interval); // Stop the timer
                setMessage.textContent = `Set ${currentSet} complete!`; // Update message
                
                currentSet++;
                
                // Check if there are more sets to run
                if (currentSet <= sets) {
                    runSet(); // Start next set
                } else {
                    setMessage.textContent = "Workout Complete!"; // Final message
                    // Show the Finished button and the reward message only after the last exercise is completed
                    finishedButton.classList.remove('hidden');
                    rewardMessage.classList.remove('hidden'); // Show the reward message
                }
            }
        }, 1000);
    }

    runSet(); // Start the first set
}
