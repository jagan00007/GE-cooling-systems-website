import os
import sqlite3, json, traceback
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_mail import Mail, Message

app = Flask(__name__)
CORS(app)
app.secret_key = "jhqy fnln efjn qtje"  # Use a consistent secret key

# Email Configuration (Update with your credentials)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")  # also move your Flask secret here
   # Replace with your app password
app.config['MAIL_DEFAULT_SENDER'] = 'jagange2@gmail.com'  # Replace with your email
mail = Mail(app)

def send_email(recipient, subject, content):
    """Send an email using Flask-Mail."""
    try:
        msg = Message(subject=subject, recipients=[recipient], body=content)
        mail.send(msg)
        print(f"Email sent successfully to {recipient}")
        return True
    except Exception as e:
        print(f"Error sending email to {recipient}: {str(e)}")
        return False

# ---------- DATABASE SETUP ----------
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
# ---------- END DATABASE SETUP ----------

@app.route('/send-booking-email', methods=['POST'])
def send_booking_email():
    try:
        data = request.json
        recipient = data.get('email')
        subject = "Booking Request Confirmation"
        content = (
            f"Dear {data.get('name')},\n\n"
            f"Thank you for your booking request for {data.get('serviceType')} on {data.get('date')}.\n\n"
            "Here are your details:\n"
            f"Name: {data.get('name')}\n"
            f"Email: {data.get('email')}\n"
            f"Phone: {data.get('phone')}\n"
            f"Address: {data.get('address')}\n\n"
            "Regards,\nGE Cooling Systems"
        )
        if send_email(recipient, subject, content):
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO service_bookings (name, email, phone, serviceType, date, address) VALUES (?, ?, ?, ?, ?, ?)",
                (data.get('name'), data.get('email'), data.get('phone'),
                 data.get('serviceType'), data.get('date'), data.get('address'))
            )
            conn.commit()
            conn.close()
            return jsonify(message="Booking email sent successfully")
        else:
            return jsonify(error="Failed to send booking email"), 500
    except Exception as e:
        traceback.print_exc()
        return jsonify(error=str(e)), 500

@app.route('/send-amc-email', methods=['POST'])
def send_amc_email():
    try:
        data = request.json
        recipient = data.get('email')
        subject = "AMC Subscription Confirmation"
        content = (
            f"Dear {data.get('name')},\n\n"
            f"Thank you for subscribing to the AMC service for your {data.get('brand')} {data.get('model')}.\n"
            f"Plan Type: {data.get('planType')}\n\n"
            "Here are your details:\n"
            f"Name: {data.get('name')}\n"
            f"Email: {data.get('email')}\n"
            f"Phone: {data.get('phone')}\n"
            f"Address: {data.get('address')}\n\n"
            "Regards,\nGE Cooling Systems"
        )
        if send_email(recipient, subject, content):
            # Insert AMC subscription record into database
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO amc_subscriptions (name, email, phone, address, brand, model, planType) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (data.get('name'), data.get('email'), data.get('phone'),
                 data.get('address'), data.get('brand'), data.get('model'), data.get('planType'))
            )
            conn.commit()
            conn.close()
            return jsonify(message="AMC email sent successfully")
        else:
            return jsonify(error="Failed to send AMC email"), 500
    except Exception as e:
        traceback.print_exc()
        return jsonify(error=str(e)), 500

@app.route("/send-order-email", methods=["POST"])
def send_order_email():
    data = request.get_json()
    # Format order details if they come as a list
    order_details = data.get("order_details")
    details_str = ""
    if isinstance(order_details, list):
        details_str = "".join([
            f"<li>{item['name']}: ₹{item['price']} x {item.get('quantity',1)}</li>" 
            for item in order_details
        ])
    else:
        details_str = f"<li>{order_details}</li>"

    client_subject = "Your Order Confirmation - GE Cooling Systems"
    client_body = f"""
    <h2>Order Confirmation</h2>
    <p>Dear {data.get('name')},</p>
    <p>Thank you for your purchase at GE Cooling Systems. Your order is being processed.</p>
    <p><strong>Order Details:</strong></p>
    <ul>
        {details_str}
    </ul>
    <p><strong>Delivery Address:</strong> {data.get('address')}</p>
    <p><strong>Contact:</strong> {data.get('phone')}</p>
    <p>Best Regards,<br>GE Cooling Systems Team</p>
    """
    send_email(data.get('email'), client_subject, client_body)

    admin_body = data.get("adminEmailBody")
    if not admin_body:
        admin_body = f"""
        <h2>New Order Received</h2>
        <p><strong>Name:</strong> {data.get('name')}</p>
        <p><strong>Email:</strong> {data.get('email')}</p>
        <p><strong>Phone:</strong> {data.get('phone')}</p>
        <p><strong>Address:</strong> {data.get('address')}</p>
        <p><strong>Order Details:</strong></p>
        <ul>
            {details_str}
        </ul>
        """
    admin_subject = "New Order Received - GE Cooling Systems"
    send_email(data.get("adminEmail"), admin_subject, admin_body)

    return jsonify({"message": "Emails sent successfully"}), 200

# ------------ ADMIN GET & DELETE ENDPOINTS -------------
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

# DELETE endpoints for individual records
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
        # [DELETE THE CUSTOMER RECORD FROM THE DATABASE]
        # For example using a Customer table (not shown) and ORM:
        # customer = Customer.query.get(customer_id)
        # db.session.delete(customer)
        # db.session.commit()
        return jsonify(message="Customer deleted successfully")
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
