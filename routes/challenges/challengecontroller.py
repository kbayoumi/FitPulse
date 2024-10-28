import MySQLdb
from flask import Blueprint, request, flash, redirect, url_for, current_app, session , render_template

# Define Blueprint for challenge management
challenges_bp = Blueprint('challengecontroller', __name__)


@challenges_bp.route('/manage_challenges')
def manage_challenges():
    mysql = current_app.config['mysql']  # Fetch the MySQL connection from Flask's current_app config
    cursor = mysql.connection.cursor()

    # Query to fetch all recipes data
    cursor.execute("SELECT * FROM challenges")  # Adjust this query as needed
    challenges = cursor.fetchall()  # Fetch all recipes

    cursor.close()

    # Render the fetched recipes in the manage_recipes.html template
    return render_template('manage_challenges.html', challenges=challenges)


@challenges_bp.route('/add_challenge', methods=['POST'])
def add_challenge():
    mysql = current_app.config['mysql']
    

    # Extract form data
    challengename = request.form['challengename']
    startdate = request.form['startdate']
    enddate = request.form['enddate']
    equipment = request.form['equipment']
    rewardpoints = request.form['rewardpoints']
    experiencelevel = request.form['experiencelevel']

    # Insert challenge data into the database
    cursor = mysql.connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO challenges (name, StartDate, EndDate, equipment,rewardpoints ,experiencelevel) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (challengename, startdate, enddate, equipment,rewardpoints ,experiencelevel))
        
        mysql.connection.commit()
        flash('Challenge added successfully!', 'success')
    except Exception as e:
        mysql.connection.rollback()
        print(f'SQL Error: {str(e)}')  # Debugging
        flash(f'Error adding challenge: {str(e)}', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('challengecontroller.manage_challenges'))

@challenges_bp.route('/edit_challenge/<int:challengeid>', methods=['GET'])
def edit_challenge(challengeid):
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor()
    
    try:
        # Fetch exercises
        cursor.execute("SELECT exerciseid, exercisename FROM exercise")
        exercises = cursor.fetchall()
        
        cursor.execute("""
            SELECT e.exerciseid, e.exercisename , ce.reps, ce.sets, ce.timetocomplete
            FROM exercise e
            JOIN challenge_exercise ce ON e.exerciseid = ce.exerciseid
            WHERE ce.challengeid = %s
        """, (challengeid,))
        exercises_selected = cursor.fetchall()
        print(exercises_selected)

        # Fetch the challenge details by ID
        cursor.execute("SELECT * FROM challenges WHERE challengeid = %s", (challengeid,))
        challenge = cursor.fetchone()  # Fetch one challenge

        # If no challenge is found, redirect with an error message
        if not challenge:
            flash('Challenge not found!', 'danger')
            return redirect(url_for('challengecontroller.manage_challenges'))
    
    except Exception as e:
        flash(f"Error fetching data: {str(e)}", 'danger')
        return redirect(url_for('challengecontroller.manage_challenges'))
    
    finally:
        cursor.close()

    # Render the edit_challenge.html with the challenge details and exercises list
    return render_template('edit_challenge.html', challenge=challenge, exercises=exercises , exercises_selected=exercises_selected)




@challenges_bp.route('/update_challenge/<int:challengeid>', methods=['POST'])
def update_challenge(challengeid):
    mysql = current_app.config['mysql']

    # Extract form data
    challengename = request.form['challengename']
    startdate = request.form['startdate']
    enddate = request.form['enddate']
    equipment = request.form['equipment']
    rewardpoints = request.form['rewardpoints']
    experiencelevel = request.form['experiencelevel']

    # Update the challenge in the database
    cursor = mysql.connection.cursor()

    try:
        cursor.execute("""
            UPDATE challenges 
            SET name = %s, StartDate = %s, EndDate = %s, equipment = %s, rewardpoints = %s, experiencelevel = %s 
            WHERE challengeid = %s
        """, (challengename, startdate, enddate, equipment, rewardpoints, experiencelevel, challengeid))
        
        mysql.connection.commit()
        flash('Challenge updated successfully!', 'success')
    except Exception as e:
        mysql.connection.rollback()
        print(f'SQL Error: {str(e)}')  # Debugging
        flash(f'Error updating challenge: {str(e)}', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('challengecontroller.manage_challenges'))




@challenges_bp.route('/add_challenge_exercise/<int:challengeid>', methods=['POST'])
def add_challenge_exercise(challengeid):
    mysql = current_app.config['mysql']

    # Extract form data
    exerciseid = request.form['exercise']
    reps = request.form['reps']
    sets = request.form['sets']
    timetocomplete = request.form['timetocomplete']

    # Insert data into the challenge_exercise table
    cursor = mysql.connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO challenge_exercise (challengeid, exerciseid, reps, sets, timetocomplete)
            VALUES (%s, %s, %s, %s, %s)
        """, (challengeid, exerciseid, reps, sets, timetocomplete))
        
        mysql.connection.commit()
        flash('Exercise added to challenge successfully!', 'success')
    except Exception as e:
        mysql.connection.rollback()
        print(f'SQL Error: {str(e)}')  # Debugging
        flash(f'Error adding exercise to challenge: {str(e)}', 'danger')
    finally:
        cursor.close()

    # Redirect back to edit challenge or any appropriate page
    return redirect(url_for('challengecontroller.edit_challenge', challengeid=challengeid))



@challenges_bp.route('/delete_challenge/<int:challengeid>', methods=['POST'])
def delete_challenge(challengeid):
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor()

    try:
        # Delete the challenge from the challenges table
        cursor.execute("DELETE FROM challenges WHERE challengeid = %s", (challengeid,))
        
        mysql.connection.commit()
        flash('Challenge deleted successfully!', 'success')
    except Exception as e:
        mysql.connection.rollback()
        print(f'SQL Error: {str(e)}')  # Debugging
        flash(f'Error deleting challenge: {str(e)}', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('challengecontroller.manage_challenges'))

@challenges_bp.route('/delete_challenge_exercise/<int:challengeid>', methods=['POST'])
def delete_challenge_exercise(challengeid):
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor()

    # Get the exerciseid from the form data
    exerciseid = request.form['exerciseid']

    try:
        # Delete the exercise from the challenge_exercise table
        cursor.execute("""
            DELETE FROM challenge_exercise 
            WHERE challengeid = %s AND exerciseid = %s
        """, (challengeid, exerciseid))

        mysql.connection.commit()
        flash('Exercise deleted from challenge successfully!', 'success')
    except Exception as e:
        mysql.connection.rollback()
        print(f'SQL Error: {str(e)}')  # Debugging
        flash(f'Error deleting exercise from challenge: {str(e)}', 'danger')
    finally:
        cursor.close()

    # Redirect back to the edit challenge page with the challenge ID
    return redirect(url_for('challengecontroller.edit_challenge', challengeid=challengeid))


@challenges_bp.route('/challenges')
def challenges():
    mysql = current_app.config['mysql']  # Fetch the MySQL connection from Flask's current_app config
    cursor = mysql.connection.cursor()

    user_id = session.get('user_id')  # Get the logged-in user's ID from the session

    # Fetch completed challenges for the logged-in user
    completed_challenges_query = """
        SELECT challengeid 
        FROM challenge_users 
        WHERE userid = %s AND done = 1
    """
    cursor.execute(completed_challenges_query, (user_id,))
    completed_challenges = cursor.fetchall()
    
    # Extract completed challenge IDs
    completed_challenge_ids = {challenge[0] for challenge in completed_challenges}

    # Query to fetch all challenges except those completed by the user
    cursor.execute("SELECT * FROM challenges")
    all_challenges = cursor.fetchall()

    # Filter out completed challenges
    challenges = [challenge for challenge in all_challenges if challenge[0] not in completed_challenge_ids]

    cursor.close()

    return render_template('challenges.html', challenges=challenges)


@challenges_bp.route('/challenge/<int:challengeid>')
def view_challenge_user(challengeid):
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor()

    try:
        # Fetch the challenge details by ID
        cursor.execute("SELECT * FROM challenges WHERE challengeid = %s", (challengeid,))
        challenge = cursor.fetchone()  # Fetch one challenge

        cursor.execute("""
            SELECT e.exerciseid, e.exercisename , ce.reps, ce.sets, ce.timetocomplete
            FROM exercise e
            JOIN challenge_exercise ce ON e.exerciseid = ce.exerciseid
            WHERE ce.challengeid = %s
        """, (challengeid,))
        exercises_selected = cursor.fetchall()
        
        print(exercises_selected)
        if not challenge:
            flash('Challenge not found!', 'danger')
            return redirect(url_for('challengecontroller.manage_challenges'))

        

    except Exception as e:
        flash(f"Error fetching challenge data: {str(e)}", 'danger')
        return redirect(url_for('challengecontroller.manage_challenges'))

    finally:
        cursor.close()

    # Render the challenge.html with the challenge details
    return render_template('challenge.html', challenge=challenge , exercises_selected=exercises_selected)


@challenges_bp.route('/claim_reward', methods=['POST'])
def claim_reward():
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor()

    # Get the challenge ID from the request data
    challenge_id = request.json.get('challenge_id')
    user_id = session.get('user_id')  # Assuming you store the logged-in user's ID in the session

    if not user_id:
        return {"message": "User not logged in"}, 403  # Unauthorized if user is not logged in

    try:
        # Fetch the reward points from the challenges table based on the challenge ID
        cursor.execute("SELECT rewardpoints FROM challenges WHERE challengeid = %s", (challenge_id,))
        result = cursor.fetchone()

        if not result:
            return {"message": "Challenge not found"}, 404  # Not found if no challenge matches the ID

        reward_points = result[0]
        # Calculate the ranking percentage
        ranking_percentage = reward_points / 10

        # Update the user's ranking percentage in the users table
        cursor.execute("""UPDATE users SET rankingpercentage = rankingpercentage + %s WHERE userid = %s""",
                       (ranking_percentage, user_id))

        # Insert the challenge_id, user_id, and done status into the challenge_users table
        cursor.execute("""INSERT INTO challenge_users (challengeid, userid, done) VALUES (%s, %s, %s)""",
                       (challenge_id, user_id, 1))  # Set done to 1 (True)

        mysql.connection.commit()

        # Instead of redirecting, return the URL for redirection
        return {"message": "Reward claimed successfully", "redirect_url": url_for('challengecontroller.challenges')}

    except Exception as e:
        mysql.connection.rollback()
        print(f'SQL Error: {str(e)}')  # Debugging
        return {"message": f'Error claiming reward: {str(e)}'}, 500  # Internal server error
    finally:
        cursor.close()
