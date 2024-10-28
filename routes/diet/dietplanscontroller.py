from datetime import datetime
from flask import current_app, request, redirect, session, url_for, flash, render_template, Blueprint
from werkzeug.utils import secure_filename
import os
import MySQLdb

dietplans_bp = Blueprint('dietplans', __name__)

@dietplans_bp.route('/dietplans')
def dietplans():
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch all diet plans
    cursor.execute('SELECT * FROM dietplans')
    dietplans = cursor.fetchall()

    cursor.close()
    return render_template('dietplans.html', dietplans=dietplans)


@dietplans_bp.route('/dietplan/<int:dietplan_id>')
def dietplan(dietplan_id):
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch the specific diet plan along with the trainer's data
    query = """
        SELECT dp.*, t.firstname, t.lastname, t.specialty, t.profilepic
        FROM dietplans dp
        JOIN trainers t ON dp.authorid = t.trainerid
        WHERE dp.dietplanid = %s
    """
    cursor.execute(query, (dietplan_id,))
    dietplan = cursor.fetchone()
    
    print(dietplan)

    cursor.close()
    
    if dietplan:
        return render_template('dietplan.html', dietplan=dietplan)
    else:
        flash('Diet plan not found.', 'danger')
        return redirect(url_for('dietplans.dietplans'))


UPLOAD_FOLDER = 'static/uploads/dietplans'  # Define your upload folder path
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed image types

def allowed_file(filename):
    """Check if the uploaded file is an allowed type."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@dietplans_bp.route('/adddietplan', methods=['POST'])
def add_diet_plan():
    # Ensure the trainer is logged in
    if 'trainer_id' not in session:
        flash('You must be logged in as a trainer to add a diet plan.', 'warning')
        return redirect(url_for('signin.signin'))  # Redirect to login if not logged in

    # Get form data
    diet_name = request.form['diet_name']
    description = request.form['description']
    core_principles = request.form['core_principles']
    timing_frequency = request.form['timing_frequency']
    best_suited_for = request.form['best_suited_for']
    easy_to_follow = request.form['easy_to_follow']
    studies = request.form['studies']
    image = request.files['image']

    # Get the current logged-in trainer's ID from session (assuming it's stored in session)
    author_id = session['trainer_id']  # Ensure trainer's ID is in the session

    # Validate and save the image
    image = request.files.get('image')  # Use .get() for safe access
    image_filename = secure_filename(image.filename) if image else None  # Secure the filename

    # Save the uploaded image to the correct directory if it exists
    if image:
        image_path = os.path.join('static/uploads/dietplans', image_filename)
        image.save(image_path)

    # Insert the diet plan data into the database
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor()
    cursor.execute('''
        INSERT INTO dietplans (authorid, dietname, description, image, publishdate, coreprinciples, timingfrequency, bestsuitedfor, easytofollow, studies)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (author_id, diet_name, description, image_filename, datetime.now(), core_principles, timing_frequency, best_suited_for, easy_to_follow, studies))
    
    mysql.connection.commit()
    cursor.close()

    flash('Diet plan added successfully!', 'success')
    return redirect(url_for('trainer.trainer_homepage'))  # Redirect back to trainer homepage

@dietplans_bp.route('/delete_diet_plan/<int:plan_id>', methods=['POST'])
def delete_diet_plan(plan_id):
    # Ensure trainer is logged in
    if 'trainer_id' not in session:
        flash('You must be logged in to delete a diet plan.', 'warning')
        return redirect(url_for('signin.signin'))

    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor()

    # Ensure the logged-in trainer owns the diet plan
    cursor.execute('DELETE FROM dietplans WHERE dietplanid = %s AND authorid = %s', (plan_id, session['trainer_id']))
    mysql.connection.commit()
    cursor.close()

    flash('Diet plan deleted successfully!', 'success')
    return redirect(url_for('trainer.trainer_homepage'))
