import os
import MySQLdb
from flask import Blueprint, request, flash, redirect, url_for, render_template, current_app,session

# Define Blueprint for profile management
profile_bp = Blueprint('profile_bp', __name__)

@profile_bp.route('/profile')
def profile():
    # Get the user ID from the session
    user_id = session.get('user_id')  # Change 'userid' to 'user_id'
    print(f"User ID from session: {user_id}")  # Debug print statement
    
    if user_id is None:
        return "User not logged in", 403  # Or redirect to a login page

    # Fetch the MySQL connection from Flask's current_app config
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor()

    # Select everything from the 'users' and 'userprop' tables for the given user ID
    query = """
        SELECT users.*, userprop.* 
        FROM users 
        JOIN userprop ON users.userid = userprop.userid
        WHERE users.userid = %s
    """
    
    cursor.execute(query, (user_id,))
    user_data = cursor.fetchone()  # Fetch a single record for the user
    
    
    workouts_query = """
        SELECT 
            t.firstname, 
            t.lastname, 
            w.workoutname, 
            w.maingoal, 
            d.dietname, 
            tua.StartDate, 
            tua.EndDate,
            w.id,
            d.dietplanid
        FROM 
            Trainer_User_Assignment tua
        JOIN 
            trainers t ON tua.trainerid = t.trainerid
        JOIN 
            workouts w ON tua.workoutid = w.id
        JOIN 
            dietplans d ON tua.dietplanid = d.dietplanid
        WHERE 
            tua.userid = %s
    """

    cursor.execute(workouts_query, (user_id,))
    workouts = cursor.fetchall()
    
    print(f"Workouts: {workouts}")  # Debug print statement

    
     # Select orders related to the user
    order_query = """
        SELECT orderid, orderdate, orderstatus, totalamount
        FROM orders
        WHERE userid = %s
        ORDER BY orderdate DESC
    """

    cursor.execute(order_query, (user_id,))
    orders = cursor.fetchall()  # Fetch all the orders for the user


    cursor.close()  # Close the cursor
    
    print(f"Fetched user data: {user_data}")  # Debug print statement


    # Check if user_data is empty
    if user_data is None:
        return "User not found", 404  # Handle case where user does not exist

    # Pass the data to the profile template
    return render_template('profile.html', user_data=user_data , orders=orders , workouts = workouts)  # Adjust this route as needed  




@profile_bp.route('/profile/update', methods=['POST'])
def update_user_profile():
    user_id = session.get('user_id')  # Ensure the user is logged in

    if user_id is None:
        flash('User not logged in', 'danger')
        return redirect(url_for('auth.login'))  # Redirect to the login page

    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT * FROM users WHERE userid = %s", (user_id,))
    existing_user = cursor.fetchone()
    
    cursor.execute("SELECT * FROM userprop WHERE userid = %s", (user_id,))
    existing_properties = cursor.fetchone()

    first_name = request.form.get('firstName', existing_user[1]).strip()
    last_name = request.form.get('lastName', existing_user[2]).strip()
    address = request.form.get('address', existing_user[3]).strip()
    phone = request.form.get('phone', existing_user[4]).strip()
    email = request.form.get('email', existing_user[5]).strip()
    gender = request.form.get('gender', existing_user[6]).strip()
    profile_pic = request.files.get('profilepic')
    
    weight = request.form.get('weight', existing_properties[2])
    height = request.form.get('height', existing_properties[3])
    goalweight = request.form.get('goalweight', existing_properties[4])
    fitnessgoal = request.form.get('fitnessgoal', existing_properties[5])
    trainingExperience = request.form.get('trainingexperience', existing_properties[6])
    activityLevel = request.form.get('activityLevel', existing_properties[7])
    bodyFatPercentage = request.form.get('bodyfat', existing_properties[8])
    muscleMass = request.form.get('musclemass', existing_properties[9])
    waistSize = request.form.get('waistsize', existing_properties[10])
    hipSize = request.form.get('hipsize', existing_properties[11])
    chestSize = request.form.get('chestsize', existing_properties[12])
    armSize = request.form.get('armsize', existing_properties[13])
    thighSize = request.form.get('thighsize', existing_properties[14])
    restingHeartRate = request.form.get('restingheartrate', existing_properties[15])
    bloodPressure = request.form.get('bloodpressure', existing_properties[16])
    vo2Max = request.form.get('vo2max', existing_properties[17])
    injuries = request.form.get('injuries', existing_properties[18])
    chronicConditions = request.form.get('chronicConditions', existing_properties[19])
    caloriesgoal = request.form.get('caloriesgoal', existing_properties[20])
    protiengoal = request.form.get('protiengoal', existing_properties[22])
    carbgoal = request.form.get('carbgoal', existing_properties[24])
    stepsgoal = request.form.get('stepsgoal', existing_properties[26])
    watergoal = request.form.get('watergoal', existing_properties[28])

    # Initialize profile_pic_filename
    profile_pic_filename = None

    # Check if the user uploaded a profile picture
    if profile_pic and profile_pic.filename:
        if not profile_pic.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            flash('Only image files are allowed for the profile picture.', 'danger')
            return redirect(url_for('profile_bp.profile'))

        # Save the new profile picture
        profile_pic_filename = profile_pic.filename
        upload_folder = os.path.join(current_app.root_path, 'static/uploads/userspp')
        os.makedirs(upload_folder, exist_ok=True)
        profile_pic_path = os.path.join(upload_folder, profile_pic_filename)
        profile_pic.save(profile_pic_path)
    else:
        # Use the existing filename if no new profile picture is uploaded
        profile_pic_filename = existing_user[9]  # Assuming index 7 is profilepic

    # Update the user's profile in the 'users' table
    update_user_query = """
        UPDATE users 
        SET firstname = %s, lastname = %s, address = %s, phone = %s, email = %s, gender = %s, profilepic = %s
        WHERE userid = %s
    """

    # Prepare user properties update query
    update_user_properties_query = """
        UPDATE userprop 
        SET weight = %s, height = %s, goalweight = %s, fitnessgoal = %s,
            trainingexperience = %s, activitylevel = %s, bodyfatpercentage = %s,
            musclemass = %s, waistsize = %s, hipsize = %s,
            chestsize = %s, armsize = %s, thighsize = %s,
            restingheartrate = %s, bloodpressure = %s, vo2max = %s,
            injuries = %s, chronicconditions = %s,
            caloriesgoal = %s, protiengoal = %s, carbgoal = %s,
            stepsgoal = %s, watergoal = %s
        WHERE userid = %s
    """

    try:
        # Update user info
        cursor.execute(update_user_query, (
            first_name, last_name, address, phone, email, gender, profile_pic_filename, user_id
        ))

        # Update user properties
        cursor.execute(update_user_properties_query, (
            weight, height, goalweight, fitnessgoal, trainingExperience, activityLevel,
            bodyFatPercentage, muscleMass, waistSize, hipSize, chestSize,
            armSize, thighSize, restingHeartRate, bloodPressure, vo2Max,
            injuries, chronicConditions,caloriesgoal,protiengoal,carbgoal,stepsgoal,watergoal, user_id
        ))

        mysql.connection.commit()  # Commit changes to the database

    except Exception as e:
        mysql.connection.rollback()  # Rollback on error
        print(f"Error updating profile: {str(e)}")
        flash('Error updating the profile in the database.', 'danger')

    cursor.close()
    
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile_bp.profile'))  # Adjust this route as needed




@profile_bp.route('/order/<int:order_id>')
def view_order(order_id):
    # Fetch the MySQL connection from Flask's current_app config
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor()

    order_total_query = """
        SELECT totalamount
        FROM orders
        WHERE orderid = %s
    """
    
    cursor.execute(order_total_query, (order_id,))
    order_total = cursor.fetchone()  # Fetch the total amount for this order

    # Query to get order details along with product image URL from the products table
    order_details_query = """
        SELECT od.orderdetailid, od.productid, od.quantity, od.priceperitem, p.imageurl
        FROM order_detail od
        JOIN products p ON od.productid = p.productid
        WHERE od.orderid = %s
    """
    cursor.execute(order_details_query, (order_id,))
    order_details = cursor.fetchall()  # Fetch all order details for this order
    
    print(f"Order details: {order_details}")

    cursor.close()  # Close the cursor

    if not order_details:
        return "Order details not found", 404  # Handle case where no details are found

    # Pass the order details to the order_details template
    return render_template('order_details.html', order_details=order_details , order_total=order_total)  # Adjust this route as needed


