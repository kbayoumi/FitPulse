# admin/utilities.py

from flask import session, flash, redirect, url_for, render_template
from functools import wraps

# Function to restrict routes to admins
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_role') not in ['admin', 'general', 'StoreManager']:
            flash("You don't have permission to access this page.", "danger")
            return redirect(url_for('admin_login'))  # Ensure this URL exists
        return f(*args, **kwargs)
    return decorated_function


# Define decorator to restrict access to users with the "Store Management" role
def store_management_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Ensure user is logged in and has "Store Management" role
        if 'user_role' not in session or session['user_role'] != 'StoreManager':
            flash("You don't have permission to access this page.", "danger")
            return redirect(url_for('admin_auth.admin_login'))  # Redirect to admin login if unauthorized
        return f(*args, **kwargs)
    return decorated_function




# Define admin_homepage function
def admin_Homepage():
    return render_template('admin_Homepage.html')
