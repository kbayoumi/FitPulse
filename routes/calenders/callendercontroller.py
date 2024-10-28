import MySQLdb
from flask import Blueprint, request, flash, redirect, url_for, render_template, current_app, session
from datetime import datetime

# Define Blueprint for calendar management
calender_bp = Blueprint('calendercontroller', __name__)

@calender_bp.route('/calender')
def calender():
    # Get the MySQL connection from Flask's current_app config
    mysql = current_app.config['mysql']  
    cursor = mysql.connection.cursor()

    # Get the logged-in user's ID from the session
    user_id = session.get('user_id')

    # Get the current day of the week (0 = Monday, 6 = Sunday)
    current_day = datetime.today().weekday()

    # Convert to your DayNumber system (1 = Saturday, 7 = Friday)
    day_number = (current_day + 3) % 7 or 7

    # SQL query to join Trainer_User_Assignment and WorkoutDay tables
    query = """
        SELECT W.DayID, W.WorkoutID, W.DayNumber , W.name 
        FROM Trainer_User_Assignment TUA
        JOIN WorkoutDay W ON TUA.workoutid = W.WorkoutID
        WHERE TUA.userid = %s AND W.DayNumber = %s
    """

    # Execute the query with the user_id and current day_number
    cursor.execute(query, (user_id, day_number))
    plans = cursor.fetchall()  # Fetch all matching plans

    cursor.close()  # Close the cursor

    # If there are no plans for today
    if not plans:
        return render_template('calender.html', plans=None)

    # Render the calender.html with the plans data
    return render_template('calender.html', plans=plans)
