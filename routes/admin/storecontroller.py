from flask import Blueprint, request, flash, redirect, url_for, render_template, current_app
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import MySQLdb.cursors  # Make sure to import this for using DictCursor
from .utilities import store_management_required  # Import the decorator
from helpers import allowed_file  # Import the allowed_file function from helpers.py


# Create a blueprint for store management
managestore_bp = Blueprint('storemanager', __name__)


'''
    The Following Routes are for the Store Management

    1- Manage the store Add / Edit / Delete Product From the DB
    2- Render the Mangment Pages
    3- Render the Store Page
    4- Render the View Product Page

'''


# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


'''
    The Following Route are for the Store Management
    it fetch all the products from the DB and render them in the manage_store.html
'''

@managestore_bp.route('/admin/manage_store')
@store_management_required
def manage_store():

    mysql = current_app.config['mysql']  
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Using '\n' as the separator for newlines
    cursor.execute("""
        SELECT p.*, GROUP_CONCAT(d.description SEPARATOR '/n') AS description
        FROM products p
        LEFT JOIN productdescription d ON p.productid = d.productid
        GROUP BY p.productid
    """)
    
    products = cursor.fetchall()
    cursor.close()  

    return render_template('manage_store.html', products=products)



'''
    The Following Route are for the Add Product Management
    it fetch all the products from the db and render them in the manage_store.html
'''


@managestore_bp.route('/admin/add_product', methods=['POST'])
@store_management_required
def add_product():
    # Print the request method and form data for debugging
    print(f"Request method: {request.method}")  # Check the method
    print(f"Form data: {request.form}")  # Output the form data to the console

    if request.method == 'POST':
        product_name = request.form.get('product_name')  # Using .get() to avoid KeyError
        price = request.form.get('price')
        stock_quantity = request.form.get('stockquantity')
        category = request.form.get('category')
        description_text = request.form.get('description')

        # Check if any of the required fields are missing
        if not all([product_name, price, stock_quantity, category]):
            flash('All fields are required!', 'error')
            return redirect(request.url)

        if 'image' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        file = request.files['image']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

        added_date = datetime.now()

        mysql = current_app.config['mysql']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute("""
            INSERT INTO products (productname, price, stockquantity, category, imageurl, addeddate)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (product_name, price, stock_quantity, category, filename, added_date))

        product_id = cursor.lastrowid

        descriptions = description_text.splitlines()
        for desc in descriptions:
            if desc.strip():
                cursor.execute("""
                    INSERT INTO productdescription (productid, description)
                    VALUES (%s, %s)
                """, (product_id, desc.strip()))

        mysql.connection.commit()
        cursor.close()

        flash('Product and descriptions added successfully!', 'success')
        return redirect(url_for('storemanager.manage_store'))

    return redirect(url_for('storemanager.manage_store'))



'''
    The Following Route are for the Edit Product Management
    it fetch the the product will be edited and allow the admin to edit any property for the product 
    Then render the edited Product again in the manage_store.html
'''


@managestore_bp.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@store_management_required
def edit_product(product_id):

    mysql = current_app.config['mysql'] 
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    
    cursor.execute("SELECT * FROM products WHERE productid = %s", (product_id,))
    product = cursor.fetchone()

    
    if product is None:
        flash('Product not found.', 'danger')
        return redirect(url_for('store.manage_store'))  

    if request.method == 'POST':
        product_name = request.form['product_name']
        price = request.form['price']
        stockquantity = request.form['stockquantity']
        category = request.form['category']
        addeddate = request.form['addeddate']

        # Check if the user uploaded a new image
        if 'product_image' in request.files:
            file = request.files['product_image']
            if file.filename != '':
                # Ensure the upload folder is set
                upload_folder = current_app.config['UPLOAD_FOLDER']  
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)

               
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)

                
                product['imageurl'] = filename 

        
        imageurl = request.form.get('imageurl', product['imageurl'])

        
        product['productname'] = product_name
        product['price'] = price
        product['stockquantity'] = stockquantity
        product['category'] = category
        product['addeddate'] = addeddate
        product['imageurl'] = imageurl  

        
        cursor.execute(""" 
            UPDATE products
            SET productname = %s, price = %s, stockquantity = %s, category = %s, addeddate = %s, imageurl = %s
            WHERE productid = %s
        """, (product['productname'], product['price'], product['stockquantity'], product['category'], product['addeddate'], product['imageurl'], product_id))

        mysql.connection.commit()
        cursor.close()  
        flash('Product updated successfully!', 'success')
        return redirect(url_for('storemanager.manage_store'))  

    return render_template('edit_product.html', product=product)



'''
    The Following Route are for the Delete Product Management
    it Delete the product 
    Then render the manage_store.html with the exeisting products
'''

@managestore_bp.route('/admin/delete_product/<int:product_id>', methods=['POST'])
@store_management_required
def delete_product(product_id):

    mysql = current_app.config['mysql']  
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    
    cursor.execute("SELECT * FROM products WHERE productid = %s", (product_id,))
    product = cursor.fetchone()

    if product is None:
        flash('Product not found.', 'danger')
        return redirect(url_for('store.manage_store'))  

    
    image_filename = product['imageurl']
    if image_filename:
        
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)
        
        
        if os.path.isfile(file_path):
            os.remove(file_path)

    
    cursor.execute("DELETE FROM productdescription WHERE productid = %s", (product_id,))

    
    cursor.execute("DELETE FROM products WHERE productid = %s", (product_id,))
    mysql.connection.commit()
    cursor.close()  

    flash('Product and associated descriptions deleted successfully!', 'success')
    return redirect(url_for('storemanager.manage_store'))  


# -------------------------------Store-Product-Managnment-Ends-Here------------------------------------------