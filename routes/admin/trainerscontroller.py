from flask import Blueprint, request, flash, redirect, url_for, render_template, current_app
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import MySQLdb.cursors  # Make sure to import this for using DictCursor
from .utilities import store_management_required  # Import the decorator
from helpers import allowed_file  # Import the allowed_file function from helpers.py
import MySQLdb.cursors 

# Define Blueprint for trainers management
trainers_bp = Blueprint('trainerscontroller', __name__)

@trainers_bp.route('/manage_trainers', methods=['GET'])
def manage_trainers():
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # Use DictCursor

    # Fetch pending trainers (is_approved = 0)
    cursor.execute("SELECT * FROM trainers WHERE is_approved = 0")
    pending_trainers = cursor.fetchall()

    # Fetch approved trainers (is_approved = 1)
    cursor.execute("SELECT * FROM trainers WHERE is_approved = 1")
    approved_trainers = cursor.fetchall()

    cursor.close()

    return render_template('manage_trainers.html', pending_trainers=pending_trainers, approved_trainers=approved_trainers)

# Route to Accept a Trainer (Set is_approved to 1)
@trainers_bp.route('/trainer/accept_trainer/<int:trainer_id>', methods=['POST'])
def accept_trainer(trainer_id):
    mysql = current_app.config['mysql']  # Access mysql connection
    cursor = mysql.connection.cursor()

    # Update the trainer's approval status
    cursor.execute("UPDATE trainers SET is_approved = 1 WHERE trainerid = %s", (trainer_id,))
    mysql.connection.commit()

    cursor.close()
    
    flash('Trainer accepted successfully!', 'success')
    return redirect(url_for('trainerscontroller.manage_trainers'))

# Route to Reject a Trainer (Delete from the database)
@trainers_bp.route('/trainer/reject_trainer/<int:trainer_id>', methods=['POST'])
def reject_trainer(trainer_id):
    mysql = current_app.config['mysql']  # Access mysql connection
    cursor = mysql.connection.cursor()

    # Delete the trainer record from the database
    cursor.execute("DELETE FROM trainers WHERE trainerid = %s", (trainer_id,))
    mysql.connection.commit()

    cursor.close()
    
    flash('Trainer rejected and removed successfully!', 'danger')
    return redirect(url_for('trainerscontroller.manage_trainers'))


@trainers_bp.route('/trainer/details/<int:trainer_id>', methods=['GET'])
def trainer_details(trainer_id):
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        # Fetch trainer details
        cursor.execute("SELECT * FROM trainers WHERE trainerid = %s", (trainer_id,))
        trainer_details = cursor.fetchone()

        # Fetch all users added by the trainer
        cursor.execute('''
            SELECT tua.AssignmentID, u.firstname, u.lastname, tua.StartDate, tua.EndDate
            FROM Trainer_User_Assignment tua
            JOIN users u ON tua.userid = u.userid
            WHERE tua.trainerid = %s
        ''', (trainer_id,))
        users_added = cursor.fetchall()

        # Fetch all exercises (workouts) added by the trainer
        cursor.execute('''
            SELECT w.*
            FROM workouts w
            WHERE w.authorid = %s  -- Use the correct column name here, replace 'authorid' if necessary
        ''', (trainer_id,))
        exercises_added = cursor.fetchall()

        # Fetch all nutrition plans added by the trainer
        cursor.execute('''
            SELECT dp.*
            FROM dietplans dp
            WHERE dp.authorid = %s
        ''', (trainer_id,))
        dietplans_added = cursor.fetchall()

    except MySQLdb.Error as e:
        flash(f"An error occurred: {e}", 'danger')
        return redirect(url_for('trainer.trainer_homepage'))

    finally:
        cursor.close()

    return render_template('trainer_details.html', 
                           trainer=trainer_details, 
                           users_added=users_added, 
                           exercises_added=exercises_added, 
                           dietplans_added=dietplans_added)


# Route to Delete a Trainer
@trainers_bp.route('/trainer/delete/<int:trainer_id>', methods=['POST'])
def delete_trainer(trainer_id):
    mysql = current_app.config['mysql']  # Access mysql connection
    cursor = mysql.connection.cursor()

    # Delete the trainer record from the database
    cursor.execute("DELETE FROM trainers WHERE trainerid = %s", (trainer_id,))
    mysql.connection.commit()

    cursor.close()
    
    flash('Trainer account deleted successfully!', 'danger')
    return redirect(url_for('trainerscontroller.manage_trainers'))