from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from flask_bcrypt import Bcrypt
from datetime import datetime
import os

signup_bp = Blueprint('signup',__name__)
# Create an instance of Bcrypt
bcrypt = Bcrypt()

@signup_bp.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Collecting all necessary data from the multi-step form
        first_name = request.form.get('firstName', '').strip()
        last_name = request.form.get('lastName', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        date_of_birth = request.form.get('dateOfBirth', '').strip()
        gender = request.form.get('gender', '').strip()

        weight = request.form.get('weight', '').strip()
        height = request.form.get('height', '').strip()
        goal = request.form.get('goal', '').strip()
        fitnessgoal = request.form.get('fitnessgoal', '').strip()
        trainingExperience = request.form.get('trainingExperience', '').strip()
        activityLevel = request.form.get('activityLevel', '').strip()
        bodyFatPercentage = request.form.get('bodyFatPercentage', '').strip()
        muscleMass = request.form.get('muscleMass', '').strip()
        waistSize = request.form.get('waistSize', '').strip()
        hipSize = request.form.get('hipSize', '').strip()
        chestSize = request.form.get('chestSize', '').strip()
        armSize = request.form.get('armSize', '').strip()
        thighSize = request.form.get('thighSize', '').strip()
        restingHeartRate = request.form.get('restingHeartRate', '').strip()
        bloodPressure = request.form.get('bloodPressure', '').strip()
        vo2Max = request.form.get('vo2Max', '').strip()
        injuries = request.form.get('injuries', '').strip()
        chronicConditions = request.form.get('chronicConditions', '').strip()
        
        calroies = request.form.get('caloriesgoal', '').strip()
        protien = request.form.get('protiengoal', '').strip()
        carb = request.form.get('carbgoal', '').strip()
        steps = request.form.get('stepsgoal', '').strip()
        water = request.form.get('watergoal', '').strip()

        # Check if email already exists
        mysql = current_app.config['mysql']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Email address already exists. Please use a different email.', 'danger')
            cursor.close()
            return render_template('register.html')

        # Hash the password using bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Upload profile picture (if any)
        profile_pic = request.files.get('profilepic')
        profile_pic_filename = None

        if profile_pic:
            if not profile_pic.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                flash('Only image files are allowed for the profile picture.', 'danger')
                cursor.close()
                return render_template('register.html')

            profile_pic_filename = profile_pic.filename
            upload_folder = os.path.join(current_app.root_path, 'static/uploads/userspp')
            os.makedirs(upload_folder, exist_ok=True)
            profile_pic_path = os.path.join(upload_folder, profile_pic_filename)
            profile_pic.save(profile_pic_path)

        # Insert user data into the users table
        try:
            cursor.execute(
                'INSERT INTO users (firstname, lastname, email, passwordhash, gender, dateofbirth, phone, profilepic, address) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                (first_name, last_name, email, hashed_password, gender, date_of_birth, phone, profile_pic_filename, address)
            )
            mysql.connection.commit()
        except Exception as e:
            mysql.connection.rollback()
            flash('Registration failed. Please try again.', 'danger')
            cursor.close()
            return render_template('register.html')

        # Fetch the newly created user's id
        user_id = cursor.lastrowid

        # Calculate the age based on the date_of_birth
        birth_date = datetime.strptime(date_of_birth, '%Y-%m-%d')
        age = (datetime.now() - birth_date).days // 365

        # Store user information in the session
        session['loggedin'] = True
        session['id'] = user_id
        session['email'] = email
        session['firstName'] = first_name
        session['weight'] = weight
        session['height'] = height
        session['age'] = age
        session['fitness_goal'] = goal

        # Insert user properties
        cursor.execute(
            'INSERT INTO userprop (userid, weight, height, goalweight,fitnessgoal, trainingexperience, activitylevel, bodyfatpercentage, musclemass, waistsize, hipsize, chestsize, armsize, thighsize, restingheartrate, bloodpressure, vo2max, injuries, chronicconditions,caloriesgoal,protiengoal,carbgoal,stepsgoal,watergoal) VALUES (%s,%s,%s,%s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s)',
            (user_id, weight, height, goal,fitnessgoal, trainingExperience, activityLevel, bodyFatPercentage, muscleMass, waistSize, hipSize, chestSize, armSize, thighSize, restingHeartRate, bloodPressure, vo2Max, injuries, chronicConditions, calroies, protien, carb, steps, water)
        )
        
        mysql.connection.commit()  # Commit the transaction

        flash('Registration successful!', 'success')
        cursor.close()  # Close the cursor

        # Redirect to startpage after successful registration
        return redirect(url_for('startpage'))

    return render_template('register.html')