from flask import Blueprint, request, flash, redirect, url_for, render_template, current_app, session
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import MySQLdb.cursors  # For using DictCursor
from helpers import allowed_file  # Import the allowed_file function from helpers.py

# Create a blueprint for store management
store_bp = Blueprint('store', __name__)

# -------------------------------Store-Product-Starts-Here------------------------------------------

# Render the store page and fetch all products
@store_bp.route('/store')
def store():
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    cursor.close()
    return render_template('store.html', products=products)

# Render product details
@store_bp.route('/product/<int:product_id>')
def product(product_id):
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM products WHERE productid = %s', (product_id,))
    product = cursor.fetchone()
    
    if product is None:
        flash('Product not found.', 'danger')
        return redirect(url_for('store.store'))
    
    cursor.execute('SELECT description FROM productdescription WHERE productid = %s', (product_id,))
    descriptions = cursor.fetchall()
    cursor.close()
    
    return render_template('product.html', product=product, descriptions=descriptions)

# # Route for adding product to cart
@store_bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    # Convert product_id to string if necessary
    product_id_str = str(product_id)
    
    # Initialize cart if it's not in the session
    if 'cart' not in session:
        session['cart'] = {}
    
    # Fetch product details from the database
    mysql = current_app.config['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM products WHERE productid = %s', (product_id,))
    product = cursor.fetchone()
    cursor.close()
    
    if product is None:
        flash('Product not found.', 'danger')
        return redirect(url_for('store.store'))
    
    # Add or update product in the cart
    cart = session['cart']
    if product_id_str in cart:
        cart[product_id_str]['quantity'] += 1
    else:
        cart[product_id_str] = {
            'name': product['productname'],
            'price': product['price'],
            'quantity': 1,
            'image': product['imageurl']
        }

    # Save updated cart back to session
    session['cart'] = cart
    flash('Product added to cart!', 'success')

    return redirect(url_for('store.store'))





# Route to display cart
@store_bp.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    total = sum(float(item['price']) * int(item['quantity']) for item in cart.values())
    return render_template('cart.html', cart=cart, total=total)

@store_bp.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    # Convert product_id to string for consistency with how it is stored in the session
    product_id_str = str(product_id)
    
    if 'cart' in session and product_id_str in session['cart']:
        session['cart'].pop(product_id_str)  # Remove item from cart
        flash('Item removed from cart.', 'info')
    else:
        flash('Item not found in cart.', 'danger')
    
    return redirect(url_for('cart'))

# Route for increasing the quantity of a product in the cart
@store_bp.route('/increase_quantity/<int:product_id>', methods=['POST'])
def increase_quantity(product_id):
    print(f'Increasing quantity for product_id: {product_id}')
    product_id_str = str(product_id)  # Convert to string for consistency
    if 'cart' in session and product_id_str in session['cart']:
        session['cart'][product_id_str]['quantity'] += 1
        flash('Quantity increased!', 'success')
    else:
        flash('Item not found in cart.', 'danger')
    
    return redirect(url_for('store.view_cart'))

# Route for decreasing the quantity of a product in the cart
@store_bp.route('/decrease_quantity/<int:product_id>', methods=['POST'])
def decrease_quantity(product_id):
    product_id_str = str(product_id)  # Convert to string for consistency
    if 'cart' in session and product_id_str in session['cart']:
        if session['cart'][product_id_str]['quantity'] > 1:
            session['cart'][product_id_str]['quantity'] -= 1
            flash('Quantity decreased!', 'success')
        else:
            flash('Item quantity cannot be less than 1.', 'danger')
    else:
        flash('Item not found in cart.', 'danger')
    
    return redirect(url_for('store.view_cart'))
@store_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        shipping_address = request.form['address']
        payment_method = request.form['payment_method']

        user_id = session.get('user_id')  # Make sure the user is logged in
        if user_id is None:
            flash('You need to log in to place an order.', 'danger')
            return redirect(url_for('signin.signin'))  # Redirect to the login route

        # Verify user exists in the database
        mysql = current_app.config['mysql']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE userid = %s', (user_id,))
        user = cursor.fetchone()
        if user is None:
            flash('User not found. Please log in again.', 'danger')
            return redirect(url_for('signin.signin'))

        # Fetch current reward points
        current_reward_points = user['rewardpoints']

        # Insert new order into the `orders` table
        cursor.execute(""" 
            INSERT INTO `orders` (userid, totalamount, orderstatus, paymentmethod, orderdate, shippingaddress)
            VALUES (%s, %s, 'pending', %s, NOW(), %s)
        """, (user_id, 0, payment_method, shipping_address))

        order_id = cursor.lastrowid  # Get the new order ID

        # Get cart details from session
        cart = session.get('cart', {})
        total_amount = 0

        # Insert each product in the cart into the `order_detail` table
        for product_id, item in cart.items():
            quantity = int(item['quantity'])  # Ensure quantity is an integer
            price_per_item = float(item['price'])  # Ensure price is a float
            total_amount += quantity * price_per_item  # Safely calculate the total amount

            # Insert into order_detail
            cursor.execute(""" 
                INSERT INTO `order_detail` (orderid, productid, quantity, priceperitem)
                VALUES (%s, %s, %s, %s)
            """, (order_id, product_id, quantity, price_per_item))

            # Decrease the product stock quantity
            cursor.execute(""" 
                UPDATE products
                SET StockQuantity = StockQuantity - %s
                WHERE productid = %s AND StockQuantity >= %s
            """, (quantity, product_id, quantity))

            # Check if stock update was successful
            if cursor.rowcount == 0:
                flash(f'Failed to update stock for product {product_id}. Not enough stock available.', 'danger')
                mysql.connection.rollback()  # Roll back the transaction
                return redirect(url_for('store.view_cart'))

        # Update the total amount for the order
        cursor.execute(""" 
            UPDATE `orders`
            SET totalamount = %s
            WHERE orderid = %s
        """, (total_amount, order_id))

        # Update user's reward points
        new_reward_points = current_reward_points + 50
        cursor.execute(""" 
            UPDATE users
            SET rewardpoints = %s
            WHERE userid = %s
        """, (new_reward_points, user_id))

        # Commit the transaction to save the order, order details, and update reward points
        mysql.connection.commit()
        cursor.close()

        # Clear the cart after placing the order
        session.pop('cart', None)
        flash('Your order has been placed successfully! You have earned 50 reward points.', 'success')

        return redirect(url_for('store.store'))

    return render_template('checkout.html')
