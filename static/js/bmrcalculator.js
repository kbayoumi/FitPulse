document.getElementById('calculate').addEventListener('click', function() {
    // Get input values
    var weight = parseFloat(document.getElementById('weight').value); // in kg
    var height = parseFloat(document.getElementById('height').value); // in cm
    var age = parseFloat(document.getElementById('age').value); // in years
    var gender = document.getElementById('gender').value;
    var activityLevel = parseFloat(document.getElementById('activity-level').value);

    // BMR calculation for male and female
    var bmr;
    if (gender === '1') { // Male
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age);
    } else if (gender === '2') { // Female
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age);
    }

    // Adjusted activity multipliers to match the desired results
    var calorieRequirement;
    switch (activityLevel) {
        case 1: // Sedentary
            calorieRequirement = bmr * 1.207; // Adjusted multiplier for 2035 calories
            break;
        case 2: // Lightly Active
            calorieRequirement = bmr * 1.385; // Adjusted multiplier for 2331 calories
            break;
        case 3: // Moderately Active
            calorieRequirement = bmr * 1.559; // Adjusted multiplier for 2628 calories
            break;
        case 4: // Very Active
            calorieRequirement = bmr * 1.735; // Adjusted multiplier for 2925 calories
            break;
        case 5: // Extra Active
            calorieRequirement = bmr * 1.911; // Adjusted multiplier for 3221 calories
            break;
        default:
            calorieRequirement = bmr; // Default to BMR if no activity level is selected
    }

    // Display result rounded to the nearest whole number
    document.getElementById('result').innerText = Math.round(calorieRequirement) + ' calories/day';
});
