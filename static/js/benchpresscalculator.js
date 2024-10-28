document.getElementById('calculate').addEventListener('click', function() {
    // Get the input values
    const weight = parseFloat(document.getElementById('weight').value);
    const reps = parseInt(document.getElementById('reps').value);

    // Check if values are valid
    if (isNaN(weight) || isNaN(reps)) {
        alert('Please enter valid values for both weight and reps.');
        return;
    }

    // Epley formula to calculate 1RM in KG
    const oneRM_kg = weight * (1 + reps / 30);

    // Display the result in KG
    document.getElementById('result').innerText = oneRM_kg.toFixed(2) + ' lbs';
});
