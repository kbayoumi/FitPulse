import MySQLdb
from flask import Blueprint, request, flash, redirect, url_for, render_template, current_app


# Define Blueprint for exercises management
exercises_bp = Blueprint('exercisescontroller', __name__)


'''
    The Following Routes are for the Exercise Category Management

    1- manage_exercises_categories & rendering manage_exerciseCategory.html
    2- add_exercise_category & redirecting to manage_exercises_categories
    3- edit_exercise_category & rendering edit_exercise_category.html
    4- delete_exercise_category & redirecting to manage_exercises_categories

'''

# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


'''
    The Following Route are for the Exercise Category Management
    it fetch all the categories from the database and render them in the manage_exerciseCategory.html
'''

@exercises_bp.route('/manage_exercise_Categories')
def manage_exercises_categories():
    mysql = current_app.config['mysql']  
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT id, name, image, description FROM exercise_category")
    categories = cursor.fetchall()

    cursor.close()

    return render_template('manage_exerciseCategory.html', categories=categories)


'''
    The Following Route is for adding a new exercise category
    it takes the category name and description from the form and insert them into the database
    then redirect to manage_exercises_categories
'''

@exercises_bp.route('/add_exercise_category', methods=['POST'])
def add_exercise_category():

    mysql = current_app.config['mysql']  
    exercisecategoryname = request.form['exercisecategoryname']
    description = request.form['description']

    # Upload image (if any)
    image = request.files['image']
    image_filename = image.filename if image else None

    # Save the uploaded image to the correct directory
    if image:
        image.save(f"static/uploads/category_images/{image_filename}")

    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO exercise_category (name, image, description) 
        VALUES (%s, %s, %s)
    """, (exercisecategoryname, image_filename, description))

    mysql.connection.commit()
    cursor.close()

    flash('Exercise category added successfully!', 'success')
    return redirect(url_for('exercisescontroller.manage_exercises_categories'))



''' 
    The Following Route is for editing an existing exercise category
    it fetches the category details from the database and render them in the edit_exercise_category.html
    then update the category details in the database and redirect to manage_exercises_categories
'''

@exercises_bp.route('/edit_exercise_category/<int:category_id>', methods=['GET', 'POST'])
def edit_exercise_category(category_id):

    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT * FROM exercise_category WHERE id = %s", (category_id,))
    category = cursor.fetchone()

    if request.method == 'POST':

        category_name = request.form.get('categoryname')
        description = request.form.get('description')

        if not category_name or not description:
            flash('Category name and description cannot be empty!', 'error')
            return render_template('edit_exercise_category.html', category=category)

        # Handle image upload
        image = request.files.get('image')

        # Use existing image if no new image is uploaded
        if image and image.filename:
            image_filename = image.filename
            # Save new image
            image.save(f"static/uploads/category_images/{image_filename}")
        else:
            image_filename = category[2]  # Retain old image filename

        try:
            cursor.execute("""
                UPDATE exercise_category
                SET name = %s, image = %s, description = %s
                WHERE id = %s
            """, (category_name, image_filename, description, category_id))
            mysql.connection.commit()
            flash('Exercise category updated successfully!', 'success')
        except MySQLdb.IntegrityError as e:
            mysql.connection.rollback()  
            flash('Error updating category: ' + str(e), 'error')
        
        cursor.close()
        return redirect(url_for('exercisescontroller.manage_exercises_categories'))

    cursor.close()

    return render_template('edit_exercise_category.html', category=category)


'''
    The Following Route is for deleting an existing exercise category
    it deletes the category from the database and redirect to manage_exercises_categories
'''

@exercises_bp.route('/delete_exercise_category/<int:category_id>', methods=['POST'])
def delete_exercise_category(category_id):

    mysql = current_app.config['mysql'] 
    cursor = mysql.connection.cursor()

    try:

        cursor.execute("DELETE FROM exercise_category WHERE id = %s", (category_id,))
        mysql.connection.commit()
        flash('Exercise category deleted successfully!', 'success')

    except MySQLdb.IntegrityError as e:
        mysql.connection.rollback() 
        flash('Error deleting category: ' + str(e), 'error')

    finally:
        cursor.close()

    return redirect(url_for('exercisescontroller.manage_exercises_categories'))



# ------------------------------------Exercise-Category-Management-Ends-Here-------------------------------------------------------


'''
    The Following Route are for the Exercise Management
    it fetch all the exercises from the database and render them in the manage_exercises.html

'''

@exercises_bp.route('/manage_exercises')
def manage_exercises():
    mysql = current_app.config['mysql']  
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT id, name FROM exercise_category")
    categories = cursor.fetchall()

    cursor.execute("""
        SELECT e.exerciseid, e.exercisename, ec.name AS categoryname, e.type, e.equipment, 
               e.targetmuscle, e.image, e.videourl 
        FROM exercise e 
        JOIN exercise_category ec ON e.categoryid = ec.id
    """)
    exercises = cursor.fetchall()

    # Prepare exercises data for rendering
    exercises_data = []
    for exercise in exercises:
        exercises_data.append({
            'exerciseid': exercise[0],
            'exercisename': exercise[1],
            'categoryname': exercise[2],
            'type': exercise[3],
            'equipment': exercise[4],
            'targetmuscle': exercise[5],
            'image': exercise[6],
            'videourl': exercise[7],
        })

    cursor.close()

    return render_template('manage_exercises.html', categories=categories, exercises=exercises_data)


'''
    The Following Route is for adding a new exercise
    it takes the exercise details from the form and insert them into the database
    then redirect to manage_exercises
'''

@exercises_bp.route('/add_exercise', methods=['POST'])
def add_exercise():
    mysql = current_app.config['mysql']  
    exercisename = request.form['exercisename']
    categoryid = request.form['categoryid']
    type = request.form['type']
    equipment = request.form['equipment']
    experiencelevel = request.form['experiencelevel']
    mechanics = request.form['mechanics']
    forcetype = request.form['forcetype']
    secondarymuscles = request.form['secondarymuscles']
    targetmuscle = request.form['targetmuscle']
    videourl = request.form['videourl']
    overview = request.form['overview']
    instructions = request.form['instructions']

    # Upload images (if any)
    image = request.files['image']
    targetmuscleimage = request.files['targetmuscleimage']
    
    image_filename = image.filename if image else None
    targetmuscleimage_filename = targetmuscleimage.filename if targetmuscleimage else None

    # Save the uploaded images to the correct directory
    if image:
        image.save(f"static/uploads/exercise_images/{image_filename}")
    if targetmuscleimage:
        targetmuscleimage.save(f"static/uploads/exercise_images/{targetmuscleimage_filename}")

    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO exercise (categoryid, exercisename, image, type, equipment, experiencelevel, mechanics, forcetype, secondarymuscles, targetmuscle, videourl, targetmuscleimage, overview, instructions) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (categoryid, exercisename, image_filename, type, equipment, experiencelevel, mechanics,
          forcetype, secondarymuscles, targetmuscle, videourl, targetmuscleimage_filename, overview, instructions))
    
    mysql.connection.commit()
    cursor.close()

    flash('Exercise added successfully!', 'success')
    return redirect(url_for('exercisescontroller.manage_exercises'))


'''
    The Following Route handles the editing of an existing exercise
    it fetches the exercise details from the database and render them in the edit_exercise.html
    then update the exercise details in the database and redirect to manage_exercises
'''

@exercises_bp.route('/edit_exercise/<int:exercise_id>', methods=['GET', 'POST'])
def edit_exercise(exercise_id):
    mysql = current_app.config['mysql']  
    cursor = mysql.connection.cursor()

    cursor.execute("""SELECT * FROM exercise WHERE exerciseid = %s""", (exercise_id,))
    exercise = cursor.fetchone()

    if exercise:
        
        image_filename = exercise[3]  
        targetmuscleimage_filename = exercise[12] 
    else:
        flash('Exercise not found!', 'error')
        return redirect(url_for('exercisescontroller.manage_exercises'))

    if request.method == 'POST':
        exercisename = request.form['exercisename']
        categoryid = request.form['categoryid']
        type = request.form['type']
        equipment = request.form['equipment']
        experiencelevel = request.form['experiencelevel']
        mechanics = request.form['mechanics']
        forcetype = request.form['forcetype']
        secondarymuscles = request.form['secondarymuscles']
        targetmuscle = request.form['targetmuscle']
        videourl = request.form['videourl']
        overview = request.form['overview']
        instructions = request.form['instructions']

        image = request.files['image']
        targetmuscleimage = request.files['targetmuscleimage']

        image_filename = image.filename if image and image.filename else exercise[3]
        targetmuscleimage_filename = targetmuscleimage.filename if targetmuscleimage and targetmuscleimage.filename else exercise[12]

        if image and image.filename:
            image.save(f"static/uploads/exercise_images/{image_filename}")
        if targetmuscleimage and targetmuscleimage.filename:
            targetmuscleimage.save(f"static/uploads/exercise_images/{targetmuscleimage_filename}")

        cursor.execute(""" 
            UPDATE exercise 
            SET categoryid = %s, exercisename = %s, image = %s, type = %s, equipment = %s, 
                experiencelevel = %s, mechanics = %s, forcetype = %s, secondarymuscles = %s, targetmuscle = %s, 
                videourl = %s, targetmuscleimage = %s, overview = %s, instructions = %s
            WHERE exerciseid = %s
        """, (categoryid, exercisename, image_filename, type, equipment, experiencelevel, mechanics,
              forcetype, secondarymuscles, targetmuscle, videourl, targetmuscleimage_filename, overview, instructions, exercise_id))

        mysql.connection.commit()
        cursor.close()

        flash('Exercise updated successfully!', 'success')
        return redirect(url_for('exercisescontroller.manage_exercises'))

    cursor.execute("SELECT id, name FROM exercise_category")
    categories = cursor.fetchall()

    cursor.close()

    return render_template('edit_exercise.html', exercise=exercise, categories=categories)


''' 
    The Following Route is for deleting an existing exercise
    it deletes the exercise from the database and redirect to manage_exercises
'''

@exercises_bp.route('/delete_exercise/<int:exercise_id>', methods=['POST'])
def delete_exercise(exercise_id):
    mysql = current_app.config['mysql'] 
    cursor = mysql.connection.cursor()

    try:

        cursor.execute("DELETE FROM exercise WHERE exerciseid = %s", (exercise_id,))
        mysql.connection.commit()
        flash('Exercise deleted successfully!', 'success')
    except Exception as e:
        mysql.connection.rollback()  
        flash('An error occurred while deleting the exercise: ' + str(e), 'error')
    finally:
        cursor.close()

    return redirect(url_for('exercisescontroller.manage_exercises'))


# ------------------------------------Exercise-Management-Ends-Here-------------------------------------------------------


# ------------------------------------Exercise-Rendering-Starts-Here-------------------------------------------------------



'''
    The Following Route renders all exercise categories on the exercisesCategory.html page.
    It fetches exercise categories from the database.
'''
@exercises_bp.route('/exercisesCategory')
def exercisesCategory():
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Fetch all exercise categories
    cursor.execute("SELECT id, name, image, description FROM exercise_category")
    exercise_categories = cursor.fetchall()
    cursor.close()
    return render_template('exercisesCategory.html', exercise_categories=exercise_categories)


'''
    The Following Route fetches and renders all exercises.
    It fetches exercises and their related categories from the database.
'''
@exercises_bp.route('/exercises')
def exercises():

     # Get the category_id from the URL query parameter
    category_id = request.args.get('category_id')
    
    # Get the MySQL connection from the current app context
    mysql = current_app.config['mysql']
    
    # Use DictCursor to fetch rows as dictionaries
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Fetch all exercises for the given category_id
    cursor.execute("SELECT * FROM exercise WHERE categoryid = %s", [category_id])
    exercises = cursor.fetchall()
    cursor.close()
    
    # Fetch the category name for the header
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT name FROM exercise_category WHERE id = %s", [category_id])
    category = cursor.fetchone()
    cursor.close()
    
    # Render the template with exercises and category
    return render_template('exercises.html', exercises=exercises, category=category)


'''
    The Following Route fetches exercises by a specific category and renders them.
    It filters exercises based on the selected category.
'''
@exercises_bp.route('/exercise/<int:exerciseid>')
def exercise(exerciseid):
    mysql = current_app.config['mysql']
    
    # Use DictCursor to fetch rows as dictionaries
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Fetch exercise details using exerciseid
    cursor.execute("SELECT * FROM exercise WHERE exerciseid = %s", [exerciseid])
    exercise = cursor.fetchone()
    cursor.close()
    
    # Check if exercise exists
    if not exercise:
        return "Exercise not found", 404
    
    # Render the template with exercise details
    return render_template('exercise.html', exercise=exercise)

# ------------------------------------Exercise-Rendering-Ends-Here-------------------------------------------------------
