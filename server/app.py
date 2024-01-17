from flask import request, make_response, jsonify, session, Flask, render_template
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
import uuid
import json
import os
import stripe 
import requests

from config import *
from models import *

load_dotenv()
app.secret_key = os.environ.get('FLASK_SECRET_KEY')
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


@app.get('/me/media')
def get_media():
    # Extract query parameters from the frontend request
    fields = request.args.get('fields')
    access_token = request.args.get('access_token')

    # Forward these parameters in a request to the Instagram API
    instagram_api_url = f"https://graph.instagram.com/me/media?fields={fields}&access_token={access_token}"
    response = requests.get(instagram_api_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Send the Instagram API response back to the frontend
        return jsonify(response.json())
    else:
        # Handle any errors
        return jsonify({'error': 'Failed to fetch data from Instagram'}), response.status_code


def calculate_order_amount(items):
    total = 0

    for item in items:
        
        total += item['quantity'] * item['price']

    total_in_cents = int(total * 100)
    print(total_in_cents)
    return total_in_cents

@app.post('/create-payment-intent')
def create_payment():
    try:
        data = json.loads(request.data)

        total_in_cents = calculate_order_amount(data)
        total_in_dollars = total_in_cents / 100  # Convert cents to dollars

        intent = stripe.PaymentIntent.create(
            amount=total_in_cents,
            currency='usd',
            automatic_payment_methods={
                'enabled': True,
            },
        )
        return jsonify({
            'clientSecret': intent['client_secret'],
            'total_price': total_in_dollars  # Return the total price in dollars
        })
    except Exception as e:
        return jsonify(error=str(e)), 403



@app.get('/check_session')
def check_session():
    admin_id = session.get('admin_id')
    admin = Admin.query.filter(Admin.id == admin_id).first()

    if not admin:
        return {'error': 'Unauthorized'}, 401
    
    return admin.to_dict(), 200

@app.post('/signin')
def sign_in():
    data = request.get_json()
    admin = Admin.query.filter(
        Admin.username == data['username']
    ).first()
    
    if not admin or not admin.authenticate(data['password']):
        return {'error': 'Login failed'}, 401
    
    session['admin_id'] = admin.id
    return admin.to_dict(), 201


def get_or_create_cart_id():
   
    cart_id = request.cookies.get('cart_id')

    if cart_id is None:
 
        cart_id = str(uuid.uuid4()) 
        return cart_id, True 
    return cart_id, False


@app.post('/add_to_cart')
def post_cart_item():
    cart_id, was_created = get_or_create_cart_id()

    data = request.get_json()

    cart = Cart.query.filter_by(id=cart_id).first()

    if not cart:
        cart = Cart(id=cart_id)
        db.session.add(cart)

    price = data.get('price')
    quantity = data.get('quantity')
    total_price=price*quantity
    
    new_cart_item = CartItem(
        product_id = data.get('product_id'),
        quantity = data.get('quantity'),
        price = total_price,
        size = data.get('size'),
        image_path = data.get('image_path'),
        cart_id = cart_id
    )
    
    db.session.add(new_cart_item)
    db.session.commit()

    response = make_response(
        jsonify(new_cart_item.to_dict()),
        201
    )

    if was_created:
        response.set_cookie('cart_id', cart_id)
        
    return response


@app.get('/get_cart_items')
def get_cart_items():
    cart_id = request.cookies.get('cart_id')

    if not cart_id:
        return jsonify([])  

    cart_items = CartItem.query.filter_by(cart_id=cart_id).all()

    cart_items_data = [item.to_dict() for item in cart_items]

    return jsonify(cart_items_data)


@app.delete('/delete_cart_item/<int:id>')
def delete_cart_item(id):
    cart_id = request.cookies.get('cart_id')

    cart_item = CartItem.query.filter(CartItem.cart_id == cart_id, CartItem.id == id).first()


    db.session.delete(cart_item)
    db.session.commit()

    if cart_item is None:
        return jsonify({'message': 'Cart item not found'}), 404
    
    return jsonify({'message': 'Item successfully deleted'}), 200


@app.patch('/update_cart_item/<int:id>')
def update_cart_item(id):
    cart_id = request.cookies.get('cart_id')

    cart_item = CartItem.query.filter(CartItem.cart_id == cart_id, CartItem.product_id == id).first()

    if cart_item:
        data=request.get_json()

        new_quantity=data.get('quantity')
        new_price=data.get('price')

        cart_item.quantity += new_quantity
        cart_item.price += new_price
        
        db.session.commit()

    if cart_item is None:
        return jsonify({'message': 'Cart item not found'}), 404
    
    response = make_response(
        jsonify(cart_item.to_dict()),
        201
    )
    return response

@app.patch('/update_cart_item_from_cart/<int:id>')
def update_cart_item_from_cart(id):
    cart_id = request.cookies.get('cart_id')

    cart_item = CartItem.query.filter(CartItem.cart_id == cart_id, CartItem.id == id).first()

    if cart_item:
        data=request.get_json()

        new_quantity=data.get('quantity')
        new_size=data.get('size')
        
        cart_item.quantity = new_quantity
        cart_item.price = new_quantity * cart_item.product.price
        cart_item.size = new_size
        
        db.session.commit()

    if cart_item is None:
        return jsonify({'message': 'Cart item not found'}), 404
    
    response = make_response(
        jsonify(cart_item.to_dict()),
        201
    )
    return response


@app.get('/events')
def get_all_events():
    events = Event.query.all()
    
    data = [event.to_dict() for event in events]

    return make_response(
        jsonify(data),
        200
    )

@app.post('/events')
def post_event():
    data = request.get_json()

    new_event = Event(
        image_path = data.get('image_path'),
        title = data.get('title'),
        date = data.get('date'),
        location = data.get('location'),
        price = data.get('price')

     )

    db.session.add(new_event)
    db.session.commit()

    return make_response(
        jsonify(new_event.to_dict()),
        201
    )

@app.delete('/events/<int:id>')
def delete_event(id):
    
    event = Event.query.get(id)

    if event is None:
        return jsonify({'message': 'Event not found'}), 404

    db.session.delete(event)
    db.session.commit()

    return jsonify({'message': 'Event successfully deleted'}), 200


@app.get('/events/<int:id>')
def get_event_by_id(id):
    event = Event.query.filter(Event.id == id).first()

    return make_response(
        jsonify(event.to_dict()),
        200
    )


@app.get('/products')
def get_all_products():
    products = Product.query.all()

    data = [product.to_dict() for product in products]

    return make_response(
        jsonify(data),
        200
    )


@app.get('/products/<int:id>')
def get_product_by_id(id):
    product = Product.query.filter(Product.id == id).first()

    return make_response(
        jsonify(product.to_dict()),
        200
    )


@app.post('/order')
def post_Order():
    data = request.get_json()

    # Create Address instance
    address_data = data.get('address')
    address = Address(
        full_name=address_data.get('full_name'),
        email=address_data.get('email'),
        line1=address_data.get('line1'),
        line2=address_data.get('line2'),
        city=address_data.get('city'),
        state=address_data.get('state'),
        postal_code=address_data.get('postal_code'),
        country=address_data.get('country')
    )

    # Create the Order instance
    new_Order = Order(
        total_price=data.get('total_price'),
        address=address,
        address_id=address.id
    )

    # Create a list of OrderItem instances
    order_items_data = data.get('order_items')
    order_items = []
    for item_data in order_items_data:
        order_item = OrderItem(
            quantity=item_data.get('quantity'),
            price=item_data.get('price'),
            order=new_Order, 
            product_id=item_data.get('product_id'),
            order_id=new_Order.id,
            size=item_data.get('size')
        )
        order_items.append(order_item)

    new_Order.order_items = order_items

    db.session.add(new_Order)
    db.session.commit()

    return make_response(
        jsonify(new_Order.to_dict()),
        201
    )





if __name__ == '__main__':
    app.run(port=5555, debug=True)