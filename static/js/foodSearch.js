document.getElementById('searchButton').addEventListener('click', function() {
    const foodName = document.getElementById('foodSearch').value;
    const apiKey = 'MA5SryEx9s1s84qOXC1yuc2nzQQTgEGw2YHAaKP5'; 
    const url = `https://api.nal.usda.gov/fdc/v1/foods/search?query=${encodeURIComponent(foodName)}&api_key=${apiKey}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.foods && data.foods.length > 0) {
                displayResults(data.foods);
            } else {
                document.getElementById('searchResults').innerHTML = '<p>No results found.</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            document.getElementById('searchResults').innerHTML = '<p>There was an error fetching the data.</p>';
        });
});

function displayResults(foods) {
    const resultsDiv = document.getElementById('searchResults');
    resultsDiv.innerHTML = ''; 

    foods.forEach(food => {
        const foodItem = document.createElement('div');
        foodItem.className = 'result-item';
        foodItem.innerHTML = `
            <h4>${food.description}</h4>
            <p>Calories: ${getCalories(food)}</p>
            <p>Protein: ${getProtein(food)} grams</p>
            <p>Carbs: ${getCarbs(food)} grams</p>
            <p>Weight: ${getWeight(food)} grams</p>
        `;
        resultsDiv.appendChild(foodItem);
    });
}

function getCalories(food) {
    const energyNutrient = food.foodNutrients.find(nutrient => nutrient.nutrientName === 'Energy' || nutrient.nutrientName === 'Calories');
    return energyNutrient ? `${energyNutrient.value} ${energyNutrient.unitName}` : 'N/A';
}

function getProtein(food) {
    const proteinNutrient = food.foodNutrients.find(nutrient => nutrient.nutrientName === 'Protein');
    return proteinNutrient ? `${proteinNutrient.value}` : 'N/A';
}

function getCarbs(food) {
    const carbsNutrient = food.foodNutrients.find(nutrient => nutrient.nutrientName === 'Carbohydrate, by difference');
    return carbsNutrient ? `${carbsNutrient.value}` : 'N/A';
}

function getWeight(food) {
    return food.servingSize ? food.servingSize : 'N/A';
}