import MySQLdb
from flask import Blueprint, request, flash, redirect, url_for, render_template, current_app


# Define Blueprint for exercises management
workouts_bp = Blueprint('workoutscontroller', __name__)

@workouts_bp.route('/workoutplan')
def workoutplan():
    # Get MySQL connection from app config
    mysql = current_app.config['mysql']  
    cursor = mysql.connection.cursor()

    # Execute query to retrieve workouts
    cursor.execute("SELECT * FROM workouts")
    workouts_data = []

    # Fetch all workouts and append to workouts_data list
    for workout in cursor.fetchall():
        workouts_data.append({
            'id': workout[0],  # Assuming the first column is 'id'
            'workoutname': workout[1],  # Assuming the second column is 'workoutname'
            'maingoal': workout[2],  # Adjust index according to your table structure
            'traininglevel': workout[3],
            'daysperweek': workout[4],
            'timeperworkout': workout[5],
            'equipmentrequired': workout[6],
            'targetgender': workout[7],
            'supps': workout[8],
            'image': workout[9],
            'description': workout[10]
        })

    # Close the cursor
    cursor.close()

    # Render the template and pass workouts_data to it
    return render_template('workoutplan.html', workouts=workouts_data)



# Route to handle form submission and add a new workout
@workouts_bp.route('/add_workout', methods=['POST'])
def add_workout():
    # Get MySQL connection from app config
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor()

    # Collect form data
    workoutname = request.form['workoutname']
    maingoal = request.form['maingoal']
    traininglevel = request.form['traininglevel']
    daysperweek = request.form['daysperweek']
    timeperworkout = request.form['timeperworkout']
    equipmentrequired = request.form['equipmentrequired']
    targetgender = request.form['targetgender']
    recommendersupps = request.form['recommendersupps']
    description = request.form['description']
    
    # Handle image upload
    image = request.files['image']
    image_filename = image.filename if image else None
    if image :
        # Secure the filename and save the image to the 'static/uploads/workout_images' folder
       image.save(f"static/uploads/workouts/{image_filename}")

    try:
        # Insert the collected data into the database
        cursor.execute("""
            INSERT INTO workouts (workoutname, maingoal, traininglevel, daysperweek, timeperworkout, 
                                  equipmentrequired, targetgender, supps, image, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (workoutname, maingoal, traininglevel, daysperweek, timeperworkout, equipmentrequired, 
              targetgender, recommendersupps, image_filename, description))
        
        # Commit the changes to the database
        mysql.connection.commit()

        flash("Workout plan added successfully!", "success")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        mysql.connection.rollback()
    finally:
        # Close the cursor
        cursor.close()

    # Redirect back to the workout plan page
    return redirect(url_for('workoutscontroller.workoutplan'))


@workouts_bp.route('/delete_workout/<int:workout_id>', methods=['POST'])
def delete_workout(workout_id):
    # Get MySQL connection from app config
    mysql = current_app.config['mysql']  
    cursor = mysql.connection.cursor()

    # Execute the delete query
    cursor.execute("DELETE FROM workouts WHERE id = %s", (workout_id,))
    
    # Commit the changes
    mysql.connection.commit()
    cursor.close()

    flash('Workout deleted successfully!', 'success')
    return redirect(url_for('workoutscontroller.workoutplan'))


@workouts_bp.route('/edit_workout/<int:workout_id>', methods=['GET'])
def edit_workout(workout_id):
    # Get MySQL connection from app config
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor()

    # Fetch the workout data for the specified ID
    cursor.execute("SELECT * FROM workouts WHERE id = %s", (workout_id,))
    workout = cursor.fetchone()

    # Check if workout exists
    if not workout:
        flash('Workout not found!', 'danger')
        return redirect(url_for('workoutscontroller.workoutplan'))

    # Prepare workout data to send to the template
    workout_data = {
        'id': workout[0],
        'workoutname': workout[1],
        'maingoal': workout[2],
        'traininglevel': workout[3],
        'daysperweek': workout[4],
        'timeperworkout': workout[5],
        'equipmentrequired': workout[6],
        'targetgender': workout[7],
        'supps': workout[8],
        'image': workout[9],
        'description': workout[10]
    }

    # Close the cursor
    cursor.close()

    # Render the edit template with the workout data and workout_id
    return render_template('editworkout.html', workout=workout_data, workout_id=workout_id)



@workouts_bp.route('/workouts')
def workouts():
    
    # Get MySQL connection from app config
    mysql = current_app.config['mysql']  
    cursor = mysql.connection.cursor()

    # Execute query to retrieve workouts
    cursor.execute("SELECT * FROM workouts")
    workouts_data = []

    # Fetch all workouts and append to workouts_data list
    for workout in cursor.fetchall():
        workouts_data.append({
            'id': workout[0],  # Assuming the first column is 'id'
            'workoutname': workout[1],  # Assuming the second column is 'workoutname'
            'maingoal': workout[2],  # Adjust index according to your table structure
            'traininglevel': workout[3],
            'daysperweek': workout[4],
            'timeperworkout': workout[5],
            'equipmentrequired': workout[6],
            'targetgender': workout[7],
            'supps': workout[8],
            'image': workout[9],
            'description': workout[10]
        })

    # Close the cursor
    cursor.close()
    return render_template('workouts.html', workouts=workouts_data)

@workouts_bp.route('/workout/<int:workout_id>')
def view_workout(workout_id):
    # Get MySQL connection from app config
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor()

    # Fetch the workout data for the specified workout ID
    cursor.execute("SELECT * FROM workouts WHERE id = %s", (workout_id,))
    
    # Convert the workout data into a dictionary
    workout_data = cursor.fetchone()
    
    if not workout_data:
        flash('Workout not found!', 'danger')
        return redirect(url_for('workoutscontroller.workoutplan'))
    
    # Creating a dictionary for the workout
    workout = {
        'id': workout_data[0],  # Assuming the first column is 'id'
        'workoutname': workout_data[1],  # Assuming the second column is 'workoutname'
        'maingoal': workout_data[2],  # Adjust index according to your table structure
        'traininglevel': workout_data[3],
        'daysperweek': workout_data[4],
        'timeperworkout': workout_data[5],
        'equipmentrequired': workout_data[6],
        'targetgender': workout_data[7],
        'supps': workout_data[8],
        'image': workout_data[9],
        'description': workout_data[10]
    }

    # Fetch the workout days, exercises, sets, and reps
    query = """
        SELECT 
            wd.DayID,
            wd.name,
            e.exercisename,
            de.Sets,
            de.Reps
        FROM 
            WorkoutDay wd
        JOIN 
            DayExercise de ON wd.DayID = de.DayID
        JOIN 
            exercise e ON de.ExerciseID = e.exerciseid
        WHERE 
            wd.WorkoutID = %s
    """
    cursor.execute(query, (workout_id,))
    workout_days = cursor.fetchall()

    # Prepare the data structure for workout days
    days_data = {}
    for DayID, name, exercisename, Sets, Reps in workout_days:
        if DayID not in days_data:
            days_data[DayID] = {
                'day_name': name,
                'exercises': []
            }
        days_data[DayID]['exercises'].append({
            'exercise_name': exercisename,
            'sets': Sets,
            'reps': Reps
        })

    # Close the cursor
    cursor.close()

    # Render the workout details page with the workout and days data
    return render_template('workout.html', workout=workout, workout_days=days_data)


