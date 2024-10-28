from flask import current_app, request, redirect, url_for, flash, render_template, Blueprint
from werkzeug.utils import secure_filename
import os
import MySQLdb


UPLOAD_FOLDER = 'static/uploads/resumes'  # Define your upload folder path here
ALLOWED_EXTENSIONS = {'pdf'}  # Define allowed file extensions

def allowed_file(filename):
    """Check if the uploaded file is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

careers_bp = Blueprint('careers', __name__)

@careers_bp.route('/careers')
def careers_page():
    return render_template('careers.html')

@careers_bp.route('/apply/<specialty>', methods=['GET'])
def apply_trainer(specialty):
    return render_template('apply.html', specialty=specialty)



@careers_bp.route('/submit_application', methods=['POST'])
def submit_application():
    specialty = request.form.get('specialty')
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    email = request.form.get('email')
    password = request.form.get('password')  
    experienceyears = request.form.get('experienceyears')
    bio = request.form.get('bio')
    resume = request.files.get('resume')
    
    image = request.files.get('profile_picture')
    
    image_filename = image.filename if image else None
    
    if image:
        image.save(f"static/uploads/trainerspp/{image_filename}")

    # Get MySQL instance from the app context
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor() 
    
    # Ensure the SQL statement is correctly formatted
    cursor.execute('INSERT INTO trainers (specialty, firstname, lastname, email, passwordhash, experienceyears, bio, resume, profilepic) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                   (specialty, firstname, lastname, email, password, experienceyears, bio, resume.filename, image_filename))
    
    # Handle resume upload and save to the server
    if resume and allowed_file(resume.filename):
        filename = secure_filename(resume.filename)
        resume_path = os.path.join(UPLOAD_FOLDER, filename)
        resume.save(resume_path)

        # Commit the changes to the database
        mysql.connection.commit()

        flash('Your application has been submitted successfully!', 'success')
    else:
        flash('Invalid resume file. Please upload a PDF file.', 'error')

    cursor.close()  # Close the cursor
    return redirect(url_for('careers.careers_page'))