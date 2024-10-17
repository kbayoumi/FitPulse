from flask import Flask, session, request, flash, redirect, url_for, render_template, jsonify
from database import init_db  # Import the init_db function
import MySQLdb.cursors
from routes import register_routes
from functools import wraps
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Set the upload folder path for product images
UPLOAD_PRODUCT_FOLDER = 'static/uploads/productsimg/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Check if the upload directory exists, if not, create it
upload_product_folder = 'static/uploads/productsimg/'
if not os.path.exists(upload_product_folder):
    os.makedirs(upload_product_folder)

app.config['UPLOAD_FOLDER'] = UPLOAD_PRODUCT_FOLDER
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize the database by calling the init_db function
mysql = init_db(app)

# Store mysql instance in the app config
app.config['mysql'] = mysql

# Register the routes
register_routes(app)

@app.route('/')
def startpage():
    # Clear the session to log the user out
    session.clear()
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')

    if not user_id:
        flash('You must be logged in to view the dashboard.', 'warning')
        return redirect(url_for('signin.signin'))  # Redirect to login page if not logged in

    # Reset current values if a new day has started
    reset_current_values_if_new_day(user_id)

    mysql = app.config['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        # Fetch the user's profile and health data
        cursor.execute('''
            SELECT u.firstname, u.lastname, u.email, u.phone, u.profilepic, 
                   p.weight, p.height, p.caloriesgoal, p.caloriescurrent, p.watergoal, p.watercurrent, 
                   p.protiengoal, p.protiencurrent, p.carbgoal, p.carbcurrent, p.stepsgoal, p.stepscurrent
            FROM users u
            JOIN userprop p ON u.userid = p.userid
            WHERE u.userid = %s
        ''', (user_id,))
        user_data = cursor.fetchone()

        # Fetch the assigned workouts for the user
        cursor.execute('''
            SELECT w.*
            FROM Trainer_User_Assignment tua
            JOIN workouts w ON tua.workoutid = w.id
            WHERE tua.userid = %s
        ''', (user_id,))
        assigned_workouts = cursor.fetchall()

    except MySQLdb.Error as e:
        flash(f"An error occurred: {e}", 'danger')
        return redirect(url_for('dashboard'))  # Redirect back to dashboard in case of error
    finally:
        cursor.close()

    return render_template(
        'mainpage.html',
        user_data=user_data,  # Pass user data to template
        assigned_workouts=assigned_workouts  # Pass assigned workouts to template
    )


@app.route('/data')
def data():
    user_id = session.get('user_id')

    mysql = app.config['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute('''
        SELECT caloriesgoal, caloriescurrent, watergoal, watercurrent, 
               protiengoal, protiencurrent, carbgoal, carbcurrent, stepsgoal, stepscurrent
        FROM userprop WHERE userid = %s
    ''', (user_id,))
    
    user_goals = cursor.fetchone()
    cursor.close()

    dashboard_data = {
        'Steps': {
            'goal': user_goals['stepsgoal'],
            'current': user_goals['stepscurrent']
        },
        'WaterInTake': {
            'goal': user_goals['watergoal'],
            'current': user_goals['watercurrent']
        },
        'Calories': {
            'goal': user_goals['caloriesgoal'],
            'current': user_goals['caloriescurrent']
        },
        'Protein': {
            'goal': user_goals['protiengoal'],
            'current': user_goals['protiencurrent']
        },
        'Carbs': {
            'goal': user_goals['carbgoal'],
            'current': user_goals['carbcurrent']
        }
    }

    return jsonify(dashboard_data)

@app.route('/update_water', methods=['POST'])
def update_water():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json()
    water_amount = data['amount']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Fetch current water and goal
    cursor.execute('SELECT watercurrent, watergoal FROM userprop WHERE userid = %s', (user_id,))
    user_data = cursor.fetchone()

    new_water_total = min(user_data['watercurrent'] + water_amount, user_data['watergoal'])

    cursor.execute('''
        UPDATE userprop SET watercurrent = %s WHERE userid = %s
    ''', (new_water_total, user_id))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"success": True})

@app.route('/update_calories', methods=['POST'])
def update_calories():
    user_id = session.get('user_id')
    new_calories = int(request.form['calories'])
    print("Received calories:", new_calories)  # Debugging line

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Fetch current calories and goal
    cursor.execute('SELECT caloriescurrent, caloriesgoal FROM userprop WHERE userid = %s', (user_id,))
    user_data = cursor.fetchone()

    new_calories_total = min(user_data['caloriescurrent'] + new_calories, user_data['caloriesgoal'])

    cursor.execute('''
        UPDATE userprop SET caloriescurrent = %s WHERE userid = %s
    ''', (new_calories_total, user_id))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('dashboard'))

@app.route('/update_carbs', methods=['POST'])
def update_carbs():
    user_id = session.get('user_id')
    new_carbs = int(request.form['carbs'])

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Fetch current carbs and goal
    cursor.execute('SELECT carbcurrent, carbgoal FROM userprop WHERE userid = %s', (user_id,))
    user_data = cursor.fetchone()

    new_carbs_total = min(user_data['carbcurrent'] + new_carbs, user_data['carbgoal'])

    cursor.execute('''
        UPDATE userprop SET carbcurrent = %s WHERE userid = %s
    ''', (new_carbs_total, user_id))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('dashboard'))

@app.route('/update_protein', methods=['POST'])
def update_protein():
    user_id = session.get('user_id')
    new_protein = int(request.form['protein'])
    print("Received protein:", new_protein)  # Debugging line

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Fetch current protein and goal
    cursor.execute('SELECT protiencurrent, protiengoal FROM userprop WHERE userid = %s', (user_id,))
    user_data = cursor.fetchone()

    new_protein_total = min(user_data['protiencurrent'] + new_protein, user_data['protiengoal'])

    cursor.execute('''
        UPDATE userprop SET protiencurrent = %s WHERE userid = %s
    ''', (new_protein_total, user_id))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('dashboard'))

def reset_current_values_if_new_day(user_id):
    # Get the last reset date from the database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT last_reset FROM userprop WHERE userid = %s', (user_id,))
    result = cursor.fetchone()
    last_reset = result['last_reset'] if result else None

    # Get the current date
    current_date = datetime.now().date()

    # If there's no last reset date or it's a new day, reset the current values
    if not last_reset or last_reset < current_date:  # Remove .date()
        # Fetch current values before resetting
        cursor.execute('''
            SELECT watercurrent, caloriescurrent, carbcurrent, protiencurrent
            FROM userprop WHERE userid = %s
        ''', (user_id,))
        current_values = cursor.fetchone()

        # Insert the daily progress into user_progress table
        cursor.execute('''
            INSERT INTO user_progress (userid, record_date, water_current, calories_current, carbs_current, protein_current)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                water_current = VALUES(water_current),
                calories_current = VALUES(calories_current),
                carbs_current = VALUES(carbs_current),
                protein_current = VALUES(protein_current)
        ''', (user_id, current_date, current_values['watercurrent'], current_values['caloriescurrent'], current_values['carbcurrent'], current_values['protiencurrent']))

        # Reset current values to zero
        cursor.execute('''
            UPDATE userprop 
            SET watercurrent = 0, caloriescurrent = 0, carbcurrent = 0, protiencurrent = 0,
                last_reset = %s 
            WHERE userid = %s
        ''', (current_date, user_id))
        mysql.connection.commit()

    cursor.close()

@app.route('/user_progress')
def user_progress():
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to view your progress.', 'warning')
        return redirect(url_for('signin.signin'))

    mysql = app.config['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute('''
        SELECT record_date, water_current, calories_current, carbs_current, protein_current
        FROM user_progress
        WHERE userid = %s
        ORDER BY record_date DESC
    ''', (user_id,))
    progress_data = cursor.fetchall()
    cursor.close()

    # Prepare data for the chart
    labels = [record['record_date'].strftime('%Y-%m-%d') for record in progress_data]
    calories_data = [record['calories_current'] for record in progress_data]
    water_data = [record['water_current'] for record in progress_data]
    carbs_data = [record['carbs_current'] for record in progress_data]
    protein_data = [record['protein_current'] for record in progress_data]

    return render_template('progress.html', labels=labels, 
                           calories_data=calories_data, 
                           water_data=water_data,
                           carbs_data=carbs_data,
                           protein_data=protein_data)


if __name__ == '__main__':
    app.run(debug=True)