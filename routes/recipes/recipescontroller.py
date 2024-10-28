import MySQLdb
from flask import Blueprint, request, flash, redirect, url_for, render_template, current_app,session

# Define Blueprint for recipes management
recipes_bp = Blueprint('recipescontroller', __name__)

'''
    The Following Route is for the Recipe Management

    1- manage_recipes & rendering manage_recipes.html
'''

# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------

'''
    This route fetches all the recipes from the database and renders them in the manage_recipes.html
'''

@recipes_bp.route('/manage_recipes')
def manage_recipes():
    mysql = current_app.config['mysql']  # Fetch the MySQL connection from Flask's current_app config
    cursor = mysql.connection.cursor()

    # Query to fetch all recipes data
    cursor.execute("SELECT * FROM recipes")  # Adjust this query as needed
    recipes = cursor.fetchall()  # Fetch all recipes

    cursor.close()

    # Render the fetched recipes in the manage_recipes.html template
    return render_template('manage_recipes.html', recipes=recipes, check= session.get('normaluser'))





'''
    The Following Route is for adding a new recipe
    it takes the recipe details from the form and inserts them into the database
    then redirects to manage_recipes
'''
@recipes_bp.route('/add_recipe', methods=['POST'])
def add_recipe():
    mysql = current_app.config['mysql']
    authorid = session.get('user_id')

    print(f'Logged in user ID: {authorid}')  # Debugging line

    if authorid is None:
        flash('You must be logged in to add a recipe!', 'danger')
        return redirect(url_for('signin.signin'))

    # Get recipe details
    required_fields = ['recipename', 'category', 'description', 'preptime', 'cooktime', 'ingredients', 'nutritionsfacts', 'instructions', 'calories']
    for field in required_fields:
        if field not in request.form or not request.form[field]:
            flash(f'{field.replace("_", " ").capitalize()} is required.', 'danger')
            return redirect(url_for('recipescontroller.add_recipe'))

    recipename = request.form['recipename']
    category = request.form['category']
    description = request.form['description']
    preptime = request.form['preptime']
    cooktime = request.form['cooktime']
    ingredients = request.form['ingredients']
    nutritionfacts = request.form['nutritionsfacts']
    instructions = request.form['instructions']
    calories = request.form['calories']

    image = request.files.get('image')
    image_filename = image.filename if image else None

    if image:
        try:
            image.save(f"static/uploads/recipe_images/{image_filename}")
        except Exception as e:
            flash(f'Error saving image: {str(e)}', 'danger')

    cursor = mysql.connection.cursor()

    try:
        cursor.execute(""" 
            INSERT INTO recipes (authorid, recipename, category, image, description, preptime, cooktime, ingredients, nutritionfacts, instructions, publisheddate, calories) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)
        """, (authorid, recipename, category, image_filename, description, preptime, cooktime, ingredients, nutritionfacts, instructions, calories))
        
        mysql.connection.commit()
        flash('Recipe added successfully!', 'success')
    except Exception as e:
        mysql.connection.rollback()
        print(f'SQL Error: {str(e)}')  # Print the error to the console for debugging
        flash(f'Error adding recipe: {str(e)}', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('recipescontroller.manage_recipes'))




@recipes_bp.route('/edit_recipe/<int:recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor()

    # Fetch the recipe details
    cursor.execute("SELECT * FROM recipes WHERE recipeid = %s", (recipe_id,))
    recipe = cursor.fetchone()

    if request.method == 'POST':
        # Get the updated recipe details from the form
        recipename = request.form.get('recipename')
        category = request.form.get('category')
        description = request.form.get('description')
        preptime = request.form.get('preptime')
        cooktime = request.form.get('cooktime')
        ingredients = request.form.get('ingredients')
        nutritionfacts = request.form.get('nutritionsfacts')
        instructions = request.form.get('instructions')  # Added instructions

        if not recipename or not description:
            flash('Recipe name and description cannot be empty!', 'error')
            return render_template('edit_recipe.html', recipe=recipe)

        # Handle image upload
        image = request.files.get('image')

        # Use existing image if no new image is uploaded
        if image and image.filename:
            image_filename = image.filename
            # Save new image
            image.save(f"static/uploads/recipe_images/{image_filename}")
        else:
            image_filename = recipe[4]  # Assuming the image filename is in the 5th column

        try:
            # Update the recipe in the database
            cursor.execute("""
                UPDATE recipes
                SET recipename = %s, category = %s, image = %s, description = %s, 
                    preptime = %s, cooktime = %s, ingredients = %s, nutritionfacts = %s, instructions = %s
                WHERE recipeid = %s
            """, (recipename, category, image_filename, description, preptime, cooktime, ingredients, nutritionfacts, instructions, recipe_id))
            mysql.connection.commit()
            flash('Recipe updated successfully!', 'success')
        except MySQLdb.IntegrityError as e:
            mysql.connection.rollback()
            flash('Error updating recipe: ' + str(e), 'error')

        cursor.close()
        return redirect(url_for('recipescontroller.manage_recipes'))

    cursor.close()
    return render_template('edit_recipe.html', recipe=recipe)




@recipes_bp.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    mysql = current_app.config['mysql'] 
    cursor = mysql.connection.cursor()

    try:
        cursor.execute("DELETE FROM recipes WHERE recipeid = %s", (recipe_id,))
        mysql.connection.commit()
        flash('Recipe deleted successfully!', 'success')
    except Exception as e:
        mysql.connection.rollback()  
        flash('An error occurred while deleting the recipe: ' + str(e), 'error')
    finally:
        cursor.close()

    return redirect(url_for('recipescontroller.manage_recipes'))



# ---------------------------------------------------------------------------------------------------------------------


@recipes_bp.route('/recipes')
def recipes():
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT * FROM recipes")
    recipes = cursor.fetchall()

    cursor.close()

    return render_template('recipes.html', recipes=recipes)

@recipes_bp.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor()

    # Query to fetch the recipe details
    cursor.execute("SELECT * FROM recipes WHERE recipeid = %s", (recipe_id,))
    recipe = cursor.fetchone()

    # Use the correct index to fetch the authorid (assuming it's in a specific column in the recipe)
    # For example, if 'authorid' is the 4th column, recipe[3] would be used.
    # If you're unsure of the index, you can explicitly refer to the column name by using dictionary cursor
    authorid = recipe['authorid'] if isinstance(recipe, dict) else recipe[1]  # Adjust according to your database structure

    # Query to fetch the author (user) details based on the recipe's authorid
    cursor.execute("SELECT * FROM users WHERE userid = %s", (authorid,))
    author = cursor.fetchone()
    
    print(author)

    cursor.close()

    # Pass both recipe and author data to the template
    return render_template('recipe.html', recipe=recipe, author=author)




