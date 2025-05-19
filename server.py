import sqlite3, json, traceback
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_mail import Mail, Message

app = Flask(__name__)
CORS(app)
app.secret_key = "jhqy fnln efjn qtje"  # Use a consistent secret key

# ----------------- MAIL CONFIGURATION -----------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jagange2@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'jhqy fnln efjn qtje'   # Replace with your app password
app.config['MAIL_DEFAULT_SENDER'] = 'jagange2@gmail.com'
mail = Mail(app)

# ----------------- DATABASE SETUP -----------------
def get_db_connection():
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS service_bookings (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT, email TEXT, phone TEXT,
          serviceType TEXT, date TEXT, address TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS amc_subscriptions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT, email TEXT, phone TEXT,
          address TEXT, brand TEXT, model TEXT, planType TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_bookings (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT, email TEXT, phone TEXT,
          address TEXT, order_details TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ----------------- ENDPOINTS USING FLASK MAIL -----------------

@app.route('/send-booking-email', methods=['POST'])
def send_booking_email():
    try:
        data = request.json
        name = data.get('name', 'N/A')
        email = data.get('email', 'N/A')
        phone = data.get('phone', 'N/A')
        service = data.get('serviceType', 'N/A')
        date = data.get('date', 'N/A')
        address = data.get('address', 'N/A')
        # Customer confirmation email
        customer_msg = Message(
            subject="Service Booking Confirmation - GE Cooling Systems",
            recipients=[email],
            body=f"Dear {name},\n\nYour service booking for {service} on {date} has been successfully received.\n\nAddress: {address}\nPhone: {phone}\n\nRegards,\nGE Cooling Systems Team"
        )
        mail.send(customer_msg)
        # Admin email with complete details
        admin_msg = Message(
            subject="New Service Booking - GE Cooling Systems",
            recipients=["jagansrini2011@gmail.com"],  # Admin email
            body=f"New Service Booking Received:\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nService: {service}\nPreferred Date: {date}\nAddress: {address}\n"
        )
        mail.send(admin_msg)
        # Insert booking record into database
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO service_bookings (name, email, phone, serviceType, date, address) VALUES (?, ?, ?, ?, ?, ?)",
            (name, email, phone, service, date, address)
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Booking email sent successfully"}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/send-amc-email', methods=['POST'])
def send_amc_email():
    try:
        data = request.json
        name = data.get('name', 'N/A')
        email = data.get('email', 'N/A')
        phone = data.get('phone', 'N/A')
        address = data.get('address', 'N/A')
        brand = data.get('brand', 'N/A')
        model = data.get('model', 'N/A')
        planType = data.get('planType', 'N/A')
        # Customer confirmation email
        customer_msg = Message(
            subject="AMC Subscription Confirmation - GE Cooling Systems",
            recipients=[email],
            body=f"Dear {name},\n\nThank you for subscribing to our AMC service for your {brand} {model}.\nPlan Type: {planType}\n\nAddress: {address}\nPhone: {phone}\n\nRegards,\nGE Cooling Systems Team"
        )
        mail.send(customer_msg)
        # Admin email with complete details
        admin_msg = Message(
            subject="New AMC Subscription - GE Cooling Systems",
            recipients=["jagansrini2011@gmail.com"],  # Admin email
            body=f"New AMC Subscription Received:\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nAddress: {address}\nAC Brand: {brand}\nAC Model: {model}\nPlan Type: {planType}\n"
        )
        mail.send(admin_msg)
        # Insert AMC subscription record into database
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO amc_subscriptions (name, email, phone, address, brand, model, planType) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, email, phone, address, brand, model, planType)
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "AMC email sent successfully"}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/send-order-email', methods=['POST'])
def send_order_email():
    try:
        data = request.json
        name = data.get('name', 'N/A')
        email = data.get('email', 'N/A')
        phone = data.get('phone', 'N/A')
        address = data.get('address', 'N/A')
        order_details = data.get('order_details', [])
        if isinstance(order_details, list) and order_details:
            order_summary = "\n".join(
                [f"📌 {item.get('name', 'Item')} - ₹{item.get('price',0)} x {item.get('quantity',1)}" for item in order_details]
            )
            details_str = "".join([
                f"<li>{item.get('name', 'Item')}: ₹{item.get('price',0)} x {item.get('quantity',1)}</li>" for item in order_details
            ])
        else:
            order_summary = "No order details provided."
            details_str = f"<li>{order_details}</li>"
        # Professional customer email
        customer_msg = Message(
            subject="Your Order Confirmation - GE Cooling Systems",
            recipients=[email],
            body=f"""Hello {name},

Thank you for your order! Your purchase has been successfully placed.

Order Details:
{order_summary}

Delivery Address: {address}
Contact: {phone}

Your order is being processed.
Best Regards,
GE Cooling Systems Team
"""
        )
        mail.send(customer_msg)
        # Professional admin email
        admin_msg = Message(
            subject="New Order Received - GE Cooling Systems",
            recipients=["jagansrini2011@gmail.com"],
            body=f"""New Order Received:

Customer Name: {name}
Email: {email}
Phone: {phone}

Order Details:
{order_summary}

Delivery Address: {address}

Please process this order.
"""
        )
        mail.send(admin_msg)
        # Insert order record into database (store order_details as JSON)
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO order_bookings (name, email, phone, address, order_details) VALUES (?, ?, ?, ?, ?)",
            (name, email, phone, address, json.dumps(order_details))
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Order emails sent successfully"}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ----------------- ADMIN ENDPOINTS -----------------
@app.route('/admin/service-bookings', methods=['GET'])
def get_service_bookings():
    conn = get_db_connection()
    bookings = conn.execute("SELECT * FROM service_bookings").fetchall()
    conn.close()
    return jsonify([dict(row) for row in bookings]), 200

@app.route('/admin/amc-subscriptions', methods=['GET'])
def get_amc_subscriptions():
    conn = get_db_connection()
    subs = conn.execute("SELECT * FROM amc_subscriptions").fetchall()
    conn.close()
    return jsonify([dict(row) for row in subs]), 200

@app.route('/admin/order-bookings', methods=['GET'])
def get_order_bookings():
    conn = get_db_connection()
    orders = conn.execute("SELECT * FROM order_bookings").fetchall()
    conn.close()
    result = []
    for row in orders:
        d = dict(row)
        d["order_details"] = json.loads(d["order_details"])
        result.append(d)
    return jsonify(result), 200

@app.route('/admin/service-bookings/<int:booking_id>', methods=['DELETE'])
def delete_service_booking(booking_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM service_bookings WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Service booking deleted"}), 200

@app.route('/admin/amc-subscriptions/<int:sub_id>', methods=['DELETE'])
def delete_amc_subscription(sub_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM amc_subscriptions WHERE id = ?", (sub_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "AMC subscription deleted"}), 200

@app.route('/admin/order-bookings/<int:order_id>', methods=['DELETE'])
def delete_order_booking(order_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM order_bookings WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Order booking deleted"}), 200

@app.route('/delete-customer', methods=['POST'])
def delete_customer():
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    customer_id = request.json.get('id')
    try:
        # ...existing code to delete customer record...
        return jsonify(message="Customer deleted successfully")
    except Exception as e:
        return jsonify(error=str(e)), 500

# ----------------- RUN FLASK SERVER -----------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)
