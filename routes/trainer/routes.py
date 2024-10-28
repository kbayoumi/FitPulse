from flask import current_app, request, redirect, session, url_for, flash, render_template, Blueprint
import MySQLdb

trainer_bp = Blueprint('trainer', __name__)
@trainer_bp.route('/trainer_homepage')
def trainer_homepage():
    # Ensure trainer is logged in
    if 'trainer_id' not in session:
        flash('You must be logged in as a trainer to view this page.', 'warning')
        return redirect(url_for('signin.signin'))  # Redirect to login page if not logged in

    trainer_id = session['trainer_id']

    # Fetch trainer's specialty and diet plans
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        # Get the trainer's specialty
        cursor.execute('SELECT specialty, payrate,profilepic FROM trainers WHERE trainerid = %s', (trainer_id,))
        trainer = cursor.fetchone()

        # Fetch the diet plans created by this trainer
        cursor.execute('SELECT * FROM dietplans WHERE authorid = %s', (trainer_id,))
        diet_plans = cursor.fetchall()
        
        cursor.execute('SELECT * FROM dietplans')
        all_diet_plans = cursor.fetchall()

        # Fetch user requests made to this trainer
        cursor.execute('''
            SELECT tua.AssignmentID, tua.StartDate, tua.EndDate, u.firstname, u.lastname, tua.request
            FROM Trainer_User_Assignment tua
            JOIN users u ON tua.userid = u.userid
            WHERE tua.trainerid = %s AND tua.request = TRUE
        ''', (trainer_id,))
        user_requests = cursor.fetchall()
        
        # Fetch accepted users along with their first and last names
        cursor.execute('''
            SELECT u.firstname, u.lastname, tua.*
            FROM Trainer_User_Assignment tua
            JOIN users u ON tua.userid = u.userid
            WHERE tua.trainerid = %s AND tua.request = 0
        ''', (trainer_id,))

        users_accepted = cursor.fetchall()

        
        
        
        cursor.execute('SELECT * FROM workouts ')
        workouts_data = []
        for workout in cursor.fetchall():
            workouts_data.append({
                'id': workout['id'],
                'workoutname': workout['workoutname'],
                'maingoal': workout['maingoal'],
                'traininglevel': workout['traininglevel'],
                'daysperweek': workout['daysperweek'],
                'timeperworkout': workout['timeperworkout'],
                'equipmentrequired': workout['equipmentrequired'],
                'targetgender': workout['targetgender'],
                'supps': workout['supps'],
                'image': workout['image'],
                'description': workout['description']
            })
            
        
        print(f"Workouts fetched: {workouts_data}")  # Debug print
        
        

    except MySQLdb.Error as e:
        flash(f"An error occurred: {e}", 'danger')
        return redirect(url_for('trainer.trainer_homepage'))
    finally:
        cursor.close()

    return render_template('trainer_Homepage.html', 
            firstName=session['firstName'], 
            specialty=trainer['specialty'], 
            payrate=trainer['payrate'],
            diet_plans=diet_plans,
            user_requests=user_requests,
            workouts = workouts_data,
            all_diet_plans = all_diet_plans,
            users_accepted = users_accepted)  # Pass user requests to the template
    
    
    

@trainer_bp.route('/availabletrainers')
def availabletrainers():
    # Get the MySQL connection
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        # Fetch all approved trainers
        cursor.execute("""
            SELECT trainerid AS id, firstname, lastname, specialty, experienceyears, rating, bio, payrate , profilepic, resume
            FROM trainers 
            WHERE is_approved = TRUE AND specialty='Online Fitness Trainer' 
        """)
        trainers = cursor.fetchall()
    except MySQLdb.Error as e:
        flash(f"An error occurred: {e}", 'danger')
        trainers = []  # Fallback to an empty list
    finally:
        cursor.close()
    
    # Render the template and pass the list of trainers
    return render_template("online_trainers.html", trainers=trainers)




@trainer_bp.route('/request_trainer', methods=['POST'])
def request_trainer():
    # Get the trainer ID, start date, and end date from the form
    trainer_id = request.form.get('trainer_id')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    user_id = session.get('user_id')
    workoutid = None  # Use None to represent SQL NULL
    dietplanid = None  # Use None to represent SQL NULL

    print("Trainer ID:", trainer_id)
    print("Start Date:", start_date)
    print("End Date:", end_date)
    print("User ID:", user_id)

    # Add logic to handle trainer request (e.g., save to database, notify trainer, etc.)
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        # Check for existing requests with overlapping dates
        cursor.execute('''
            SELECT * FROM Trainer_User_Assignment 
            WHERE trainerid = %s AND userid = %s 
            AND ((StartDate <= %s AND EndDate >= %s) OR (StartDate <= %s AND EndDate >= %s))
        ''', (trainer_id, user_id, end_date, start_date, start_date, end_date))

        existing_request = cursor.fetchone()

        if existing_request:
            flash('You have already requested this trainer for an overlapping date range.', 'danger')
        else:
            # Insert the request into the Trainer_User_Assignment table if no conflicts
            cursor.execute('''
                INSERT INTO Trainer_User_Assignment (trainerid, StartDate, EndDate, userid, workoutid, dietplanid) 
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (trainer_id, start_date, end_date, user_id, workoutid, dietplanid))

            mysql.connection.commit()
            flash('Trainer request submitted successfully for the specified date range!', 'success')
    
    except MySQLdb.Error as e:
        flash(f"An error occurred: {e}", 'danger')
    
    finally:
        cursor.close()

    return redirect(url_for('trainer.availabletrainers'))


@trainer_bp.route('/handle_request', methods=['POST'])
def handle_request():
    assignment_id = request.form.get('assignment_id')
    action = request.form.get('action')

    print(f"Assignment ID: {assignment_id}, Action: {action}")  # Debugging

    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        if action == 'approve':
            print(f"Approving request with Assignment ID: {assignment_id}")
            cursor.execute('UPDATE Trainer_User_Assignment SET request = FALSE WHERE AssignmentID = %s', (assignment_id,))
            flash('Request approved successfully!', 'success')
        elif action == 'decline':
            print(f"Declining request with Assignment ID: {assignment_id}")
            cursor.execute('DELETE FROM Trainer_User_Assignment WHERE AssignmentID = %s', (assignment_id,))
            flash('Request declined and removed successfully.', 'success')

        mysql.connection.commit()
    except MySQLdb.Error as e:
        flash(f"An error occurred: {e}", 'danger')
    finally:
        cursor.close()

    return redirect(url_for('trainer.trainer_homepage'))




@trainer_bp.route('/assign_workout_and_diet', methods=['POST'])
def assign_workout_and_diet():
    user_id = request.form.get('userid')
    workout_id = request.form.get('workoutid')
    dietplan_id = request.form.get('dietplanid')

    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        # Update the Trainer_User_Assignment table with the assigned workout and diet plan
        cursor.execute('''
            UPDATE Trainer_User_Assignment
            SET workoutid = %s, dietplanid = %s
            WHERE userid = %s
        ''', (workout_id, dietplan_id, user_id))

        mysql.connection.commit()
        flash('Workout and diet plan assigned successfully!', 'success')
    except MySQLdb.Error as e:
        flash(f"An error occurred: {e}", 'danger')
    finally:
        cursor.close()

    return redirect(url_for('trainer.trainer_homepage'))



@trainer_bp.route('/terminate_user', methods=['POST'])
def terminate_user():
    user_id = request.form.get('userid')
    
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute('DELETE FROM Trainer_User_Assignment WHERE userid = %s', (user_id,))
    mysql.connection.commit()  # Commit the changes to the database
   

    return redirect(url_for('trainer.trainer_homepage'))  # Redirect back to homepage


from flask import request, render_template, redirect, url_for, current_app
import MySQLdb.cursors

@trainer_bp.route('/viewuser', methods=['GET'])
def viewuser():
    # Get the user ID from the query parameter
    userid = request.args.get('userid')

    if userid:
        # Get the MySQL connection
        mysql = current_app.config['mysql']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Query the users table
        cursor.execute('SELECT * FROM users WHERE userid = %s', (userid,))
        user = cursor.fetchone()

        print(f"User data: {user}")

        # Query the userprops table
        cursor.execute('SELECT * FROM userprop WHERE userid = %s', (userid,))
        userprops = cursor.fetchone()

        print(f"User properties: {userprops}")
        # Render the viewuser.html page and pass the user and userprops data
        return render_template('viewuser.html', user=user, userprops=userprops)
    
    # If no user ID is provided, redirect or handle appropriately
    return "User ID not provided", 400



@trainer_bp.route('/update_userprops', methods=['POST'])
def update_userprops():
    # Get the user ID and properties from the form data
    userid = request.form.get('userid')
    caloriesgoal = request.form.get('caloriesgoal')
    protiengoal = request.form.get('protiengoal')
    carbgoal = request.form.get('carbgoal')
    watergoal = request.form.get('watergoal')

    if userid:
        # Get the MySQL connection
        mysql = current_app.config['mysql']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Update the userprops table with the new values
        cursor.execute('''UPDATE userprop 
                        SET caloriesgoal = %s, 
                        protiengoal = %s, 
                        carbgoal = %s, 
                        watergoal = %s 
                        WHERE userid = %s''', 
                    (caloriesgoal, protiengoal, carbgoal, watergoal, userid))
        mysql.connection.commit()  # Commit the changes

        # Optionally, you can add a flash message or notification here

        return redirect(url_for('trainer.viewuser', userid=userid))  # Redirect to viewuser page
    
    return "User ID not provided", 400