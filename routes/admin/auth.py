from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
import MySQLdb.cursors

# Create a Blueprint for admin authentication
admin_auth_bp = Blueprint('admin_auth', __name__)

@admin_auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    mysql = current_app.config['mysql']  # Access the MySQL connection from the app config
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Query the database to check if the admin email exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM admins WHERE email = %s", (email,))
        admin = cursor.fetchone()
        cursor.close()

        if admin:
            # Check the password (assuming it's stored in plain text, consider hashing it)
            if admin['password'] == password:
                session['user_id'] = admin['id']
                session['user_role'] = admin['role']  # Save the user's role
                session['normaluser'] = False
                flash("Welcome, Admin!", "success")
                return redirect(url_for('admin_auth.admin_Homepage'))
            else:
                flash('Invalid email or password', 'danger')
        else:
            flash('No admin found with this email', 'danger')
        
        return redirect(url_for('admin_auth.admin_login'))

    return render_template('admin_login.html')

@admin_auth_bp.route('/admin/Homepage')
def admin_Homepage():
    return render_template('admin_Homepage.html')
