document.addEventListener('DOMContentLoaded', function() {
    fetch('/data')
    .then(response => response.json())
    .then(data => {
        // Line chart for steps and calories burned
        const ctx = document.getElementById('IntakeChart').getContext('2d');
        const IntakeChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday'], 
                datasets: [
                    {
                        label: 'Water Intake (ml)',
                        data: [3000, 3100, 2900, 3050, 3000, 2950], // Water intake data
                        backgroundColor: '#7CF5FF',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Calories Intake (kcal)',
                        data: [1700, 1750, 1680, 1720, 1700, 1690], // Calorie intake data
                        backgroundColor: '#FABC3F',
                        borderColor: '#FABC3F',
                        borderWidth: 1
                    },
                    {
                        label: 'Protein Intake (g)',
                        data: [80, 82, 78, 81, 80, 79], // Protein intake data
                        backgroundColor: '#FF6363',
                        borderColor: '#FF6363',
                        borderWidth: 1
                    },
                    {
                        label: 'Carbs Intake (g)',
                        data: [250, 240, 245, 250, 250, 255], // Carb intake data
                        backgroundColor: '#B6FFA1',
                        borderColor: '#B6FFA1',
                        borderWidth: 1
                    },
                    {
                        label: 'Weight (kg)',
                        data: [66.5, 66.2, 66.0, 65.8, 65.6, 65.3], // Weight data
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // Pie chart for water intake
        const pieCtx = document.getElementById('waterChart').getContext('2d');
        const pieChart = new Chart(pieCtx, {
            type: 'pie',
            data: {
                datasets: [{
                    data: [data.WaterInTake.current, data.WaterInTake.goal - data.WaterInTake.current],
                    backgroundColor: ['#7CF5FF', '#302F2F'], 
                    borderWidth: 0
                }]
            }
        });

        // Pie chart for calories intake
        const pieCtx2 = document.getElementById('CaloriesChart').getContext('2d');
        const pieChart2 = new Chart(pieCtx2, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [data.Calories.current, data.Calories.goal - data.Calories.current],
                    backgroundColor: ['#FABC3F', '#302F2F'],
                    borderWidth: 0
                }]
            }
        });

        // Pie chart for carbs intake
        const pieCtx3 = document.getElementById('CarbsChart').getContext('2d');
        const pieChart3 = new Chart(pieCtx3, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [data.Carbs.current, data.Carbs.goal - data.Carbs.current],
                    backgroundColor: ['#B6FFA1', '#302F2F'], 
                    borderWidth: 0
                }]
            }
        });

        // Pie chart for protein intake
        const pieCtx4 = document.getElementById('ProtienChart').getContext('2d');
        const pieChart4 = new Chart(pieCtx4, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [data.Protein.current, data.Protein.goal - data.Protein.current],
                    backgroundColor: ['#FF6363', '#302F2F'], 
                    borderWidth: 0
                }]
            }
        });

        
    });
});

// Function to show the div when the button is clicked
document.querySelector('.Update-button').addEventListener('click', function(event) {
    const wrapper = document.querySelector('.wrapper1');
    wrapper.classList.remove('hidden'); // Show the div
});

// Function to hide the div when clicked outside
document.addEventListener('click', function(event) {
    const wrapper = document.querySelector('.wrapper1');
    const button = document.querySelector('.Update-button');

    // Check if the clicked target is not the wrapper or its children and not the button
    if (!wrapper.contains(event.target) && event.target !== button) {
        wrapper.classList.add('hidden'); // Hide the div
    }
});



function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    document.getElementById('current-time').textContent = timeString;
}

// Call updateTime every second to keep the time updated
setInterval(updateTime, 1000);

// Call it once on page load to set the initial time
updateTime();


let stopwatchInterval;
let isRunning = false;

document.getElementById('startButton').addEventListener('click', function () {
    if (!isRunning) {
        const startTime = Date.now();
        isRunning = true;

        function updateTime() {
            const currentTime = Date.now();
            const elapsedTime = currentTime - startTime;

            const hours = Math.floor(elapsedTime / (1000 * 60 * 60)).toString().padStart(2, '0');
            const minutes = Math.floor((elapsedTime % (1000 * 60 * 60)) / (1000 * 60)).toString().padStart(2, '0');
            const seconds = Math.floor((elapsedTime % (1000 * 60)) / 1000).toString().padStart(2, '0');

            document.getElementById('time').textContent = `${hours}:${minutes}:${seconds}`;
        }

        stopwatchInterval = setInterval(updateTime, 1000);
    }
});

document.getElementById('resetButton').addEventListener('click', function () {
    clearInterval(stopwatchInterval);  // Stop the stopwatch
    document.getElementById('time').textContent = "00:00:00";  // Reset the displayed time
    isRunning = false;  // Allow the stopwatch to be started again
});