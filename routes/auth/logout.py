from flask import Blueprint, redirect, url_for, flash, session

# Create a Blueprint for logout
logout_bp = Blueprint('logout', __name__)

@logout_bp.route('/logout')
def logout():
    # Clear the session
    session.clear()
    
    # Optionally, flash a message
    flash('You have been logged out.', 'info')
    
    # Redirect to login page (or home page)
    return redirect(url_for('startpage'))
