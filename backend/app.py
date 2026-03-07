import os
import uuid
import datetime
from decimal import Decimal
from flask import Flask, render_template, request, redirect, session, jsonify
import boto3
from boto3.dynamodb.conditions import Key

app = Flask(__name__)

# SECURITY: Use environment variables for secrets
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "generate-a-long-random-string-for-prod")

# ---------------- AWS CONNECTION ----------------
# It is better to rely on EC2 IAM Roles than hardcoded regions if possible
REGION = os.environ.get("AWS_REGION", "ap-south-1")
dynamodb = boto3.resource('dynamodb', region_name=REGION)
sns = boto3.client('sns', region_name=REGION)

users_table = dynamodb.Table('travel-Users')
bookings_table = dynamodb.Table('Bookings')

SNS_TOPIC_ARN = "arn:aws:sns:ap-south-1:336449003024:TravelGoNotifications"

# ---------------- STATIC DATA ----------------
bus_data = [
    {"id": "B1", "name": "Super Luxury Bus", "source": "Hyderabad", "dest": "Bangalore", "price": 800},
    {"id": "B2", "name": "Express Bus", "source": "Chennai", "dest": "Hyderabad", "price": 700},
    {"id": "B3", "name": "Night Rider", "source": "Bangalore", "dest": "Mumbai", "price": 900},
    {"id": "B4", "name": "Metro Travels", "source": "Delhi", "dest": "Jaipur", "price": 650},
    {"id": "B5", "name": "Southern Express", "source": "Chennai", "dest": "Coimbatore", "price": 500},
    {"id": "B6", "name": "Coastal Cruise", "source": "Mumbai", "dest": "Goa", "price": 750}
]
train_data = [
    {"id": "T1", "name": "Rajdhani Express", "source": "Hyderabad", "dest": "Delhi", "price": 1500},
    {"id": "T2", "name": "Shatabdi Express", "source": "Chennai", "dest": "Bangalore", "price": 900},
    {"id": "T3", "name": "Duronto Express", "source": "Mumbai", "dest": "Delhi", "price": 1800},
    {"id": "T4", "name": "Garib Rath", "source": "Delhi", "dest": "Kolkata", "price": 1100},
    {"id": "T5", "name": "Vande Bharat", "source": "Bangalore", "dest": "Chennai", "price": 1200}
]
flight_data = [
    {"id": "F1", "name": "Indigo 6E203", "source": "Hyderabad", "dest": "Dubai", "price": 8500},
    {"id": "F2", "name": "Air India AI102", "source": "Delhi", "dest": "Singapore", "price": 9500},
    {"id": "F3", "name": "Singapore Airlines SQ421", "source": "Chennai", "dest": "Singapore", "price": 12000},
    {"id": "F4", "name": "Emirates EK523", "source": "Mumbai", "dest": "Dubai", "price": 11000},
    {"id": "F5", "name": "IndiGo 6E101", "source": "Delhi", "dest": "Bangkok", "price": 7500},
    {"id": "F6", "name": "Air Asia AK21", "source": "Hyderabad", "dest": "Kuala Lumpur", "price": 8000}
]
hotel_data = [
    {"id": "H1", "name": "Grand Palace", "city": "Chennai", "type": "Luxury", "price": 4000},
    {"id": "H2", "name": "Budget Inn", "city": "Hyderabad", "type": "Budget", "price": 1500},
    {"id": "H3", "name": "Goa Beach Resort", "city": "Goa", "type": "Resort", "price": 5500},
    {"id": "H4", "name": "Royal Rajputana", "city": "Jaipur", "type": "Luxury", "price": 6000},
    {"id": "H5", "name": "Sea View Villa", "city": "Mumbai", "type": "Villa", "price": 7000},
    {"id": "H6", "name": "Delhi Comfort Inn", "city": "Delhi", "type": "Budget", "price": 2000}
]
packages_data = [
    {"id": "P1", "name": "Goa Beach Getaway", "duration": "3 Nights / 4 Days", "includes": "Hotel + Bus + Sightseeing", "price": 12000, "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400"},
    {"id": "P2", "name": "Dubai Luxury Tour", "duration": "5 Nights / 6 Days", "includes": "Hotel + Flight + City Tour", "price": 65000, "image": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=400"},
    {"id": "P3", "name": "Singapore City Explorer", "duration": "4 Nights / 5 Days", "includes": "Hotel + Flight + Theme Parks", "price": 45000, "image": "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=400"},
    {"id": "P4", "name": "Rajasthan Heritage Trail", "duration": "6 Nights / 7 Days", "includes": "Hotel + Train + Guide", "price": 18000, "image": "https://images.unsplash.com/photo-1599661046289-e31897846e41?w=400"},
    {"id": "P5", "name": "Thailand Adventure", "duration": "5 Nights / 6 Days", "includes": "Hotel + Flight + Tours", "price": 35000, "image": "https://images.unsplash.com/photo-1506665531195-3566af2b4dfa?w=400"},
    {"id": "P6", "name": "Kerala Backwaters", "duration": "3 Nights / 4 Days", "includes": "Houseboat + Bus + Meals", "price": 14000, "image": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=400"}
]

# ---------------- HELPER FUNCTIONS ----------------

def get_transport_info(t_id):
    """Identifies the service type and details based on the ID."""
    all_services = [bus_data, train_data, flight_data]
    types = ['Bus', 'Train', 'Flight']
    
    for idx, service_list in enumerate(all_services):
        for item in service_list:
            if item['id'] == t_id:
                return {
                    'type': types[idx],
                    'source': item['source'],
                    'destination': item['dest'],
                    'details': f"{item['name']} ({item['source']} - {item['dest']})"
                }
    
    for h in hotel_data:
        if h['id'] == t_id:
            return {
                'type': 'Hotel',
                'source': h['city'],
                'destination': h['city'],
                'details': f"{h['name']} in {h['city']} ({h['type']})"
            }
            
    return {'type': 'General', 'source': 'Unknown', 'destination': 'Unknown', 'details': 'Transport Details'}

# ---------------- ROUTES ----------------

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users_table.put_item(
            Item={
                'email': request.form['email'],
                'name': request.form['name'],
                'password': request.form['password'],
                'logins': 0
            }
        )
        return redirect('/login')
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            response = users_table.get_item(Key={'email': request.form['email']})
            user = response.get('Item')
            if user and user['password'] == request.form['password']:
                session['user'] = user['email']
                session['name'] = user['name']
                return redirect('/dashboard')
            return render_template("login.html", error="Invalid Credentials")
        except Exception as e:
            return render_template("login.html", error=str(e))
    return render_template("login.html")

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    
    # IMPROVED: Using Query with GSI instead of Scan
    # Requires a GSI named 'email-index' on the Bookings table
    try:
        response = bookings_table.query(
            IndexName='email-index',
            KeyConditionExpression=Key('email').eq(session['user'])
        )
        bookings = response.get('Items', [])
    except Exception as e:
        print(f"Query Error: {e}. Falling back to scan (Not recommended for prod)")
        response = bookings_table.scan(FilterExpression=Key('email').eq(session['user']))
        bookings = response.get('Items', [])
    
    return render_template("dashboard.html", name=session.get('name', 'User'), bookings=bookings)

@app.route('/packages')
def packages():
    if 'user' not in session: return redirect('/login')
    return render_template("packages.html", packages=packages_data)

@app.route('/remove_booking', methods=['POST'])
def remove_booking():
    if 'user' not in session: return redirect('/login')
    booking_id = request.form.get('booking_id')
    try:
        bookings_table.delete_item(Key={'booking_id': booking_id})
    except Exception as e:
        print(f"Delete Error: {e}")
    return redirect('/dashboard')

@app.route('/bus')
def bus(): return render_template("bus.html", buses=bus_data)

@app.route('/train')
def train(): return render_template("train.html", trains=train_data)

@app.route('/flight')
def flight(): return render_template("flight.html", flights=flight_data)

@app.route('/hotels')
def hotels(): return render_template("hotels.html", hotels=hotel_data)

@app.route('/seat/<transport_id>/<price>')
def seat(transport_id, price):
    if 'user' not in session: return redirect('/login')
    return render_template("seat.html", id=transport_id, price=price)

@app.route('/book', methods=['POST'])
def book():
    if 'user' not in session: return redirect('/login')
    t_id = request.form['transport_id']
    seats = request.form.get('seat')
    price = request.form['price']
    info = get_transport_info(t_id)
    
    session['booking_flow'] = {
        'transport_id': t_id,
        'type': info['type'],
        'source': info['source'],
        'destination': info['destination'],
        'details': info['details'],
        'seat': seats,
        'price': price,
        'date': str(datetime.date.today())
    }
    return render_template("payment.html", booking=session['booking_flow'])

@app.route('/payment', methods=['POST'])
def payment():
    if 'user' not in session or 'booking_flow' not in session:
        return redirect('/dashboard')

    booking_data = session['booking_flow']
    booking_id = str(uuid.uuid4())[:8]
    booking_data['booking_id'] = booking_id
    booking_data['email'] = session['user']
    booking_data['payment_method'] = request.form.get('method')
    booking_data['payment_reference'] = request.form.get('reference')
    booking_data['price'] = Decimal(str(booking_data['price']))

    bookings_table.put_item(Item=booking_data)

    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="TravelGo Booking Confirmed",
            Message=f"Booking ID: {booking_id}\nType: {booking_data['type']}\nDetails: {booking_data['details']}\nSeats: {booking_data['seat']}\nTotal Paid: Rs. {booking_data['price']}"
        )
    except Exception as e:
        print(f"SNS Error: {e}")

    final_booking = booking_data.copy()
    session.pop('booking_flow', None)
    return render_template("ticket.html", booking=final_booking)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    # Running on 0.0.0.0 for EC2 access, but debug is OFF for safety
    app.run(host='0.0.0.0', port=5000, debug=False)