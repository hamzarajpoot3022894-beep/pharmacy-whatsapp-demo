from flask import Flask, render_template_string, request, session
import csv
import os
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = "pharmacy-demo-secret-key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "pharmacy_requests.csv")


# =========================================================
# CUSTOMER CHAT PAGE
# =========================================================

CHAT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>1st Health Pharmacy Demo</title>

    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: Arial, sans-serif;
            background: #e9edef;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .phone {
            width: 100%;
            max-width: 430px;
            height: 760px;
            background: #efeae2;
            border-radius: 22px;
            overflow: hidden;
            box-shadow: 0 12px 35px rgba(0,0,0,0.20);
            display: flex;
            flex-direction: column;
        }

        .header {
            background: #075e54;
            color: white;
            padding: 15px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .logo {
            width: 46px;
            height: 46px;
            background: white;
            color: #075e54;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 18px;
        }

        .header-text {
            flex: 1;
        }

        .header-text h3 {
            font-size: 17px;
            margin-bottom: 3px;
        }

        .header-text p {
            font-size: 12px;
            opacity: 0.85;
        }

        .dashboard-link {
            color: white;
            text-decoration: none;
            font-size: 12px;
            border: 1px solid rgba(255,255,255,0.5);
            padding: 7px 9px;
            border-radius: 8px;
        }

        .chat-area {
            flex: 1;
            overflow-y: auto;
            padding: 18px 14px;
        }

        .date {
            text-align: center;
            margin-bottom: 18px;
        }

        .date span {
            background: white;
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 11px;
            color: #667781;
        }

        .message {
            max-width: 82%;
            padding: 10px 12px;
            margin-bottom: 10px;
            border-radius: 10px;
            line-height: 1.45;
            font-size: 14px;
            white-space: pre-line;
            box-shadow: 0 1px 1px rgba(0,0,0,0.08);
        }

        .bot {
            background: white;
            border-top-left-radius: 3px;
            margin-right: auto;
        }

        .customer {
            background: #d9fdd3;
            border-top-right-radius: 3px;
            margin-left: auto;
        }

        .time {
            display: block;
            text-align: right;
            margin-top: 5px;
            font-size: 10px;
            color: #667781;
        }

        .input-area {
            padding: 10px;
            background: #f0f2f5;
            display: flex;
            gap: 8px;
            align-items: center;
        }

        .input-area input {
            flex: 1;
            padding: 13px 15px;
            border: none;
            border-radius: 24px;
            outline: none;
            font-size: 14px;
        }

        .send-btn {
            width: 46px;
            height: 46px;
            border-radius: 50%;
            border: none;
            background: #00a884;
            color: white;
            font-size: 18px;
            cursor: pointer;
        }

        .demo-badge {
            position: fixed;
            top: 15px;
            right: 15px;
            background: #111827;
            color: white;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 12px;
        }
    </style>
</head>

<body>

<div class="demo-badge">Demo Mode</div>

<div class="phone">

    <div class="header">

        <div class="logo">1H</div>

        <div class="header-text">
            <h3>1st Health Pharmacy</h3>
            <p>WhatsApp Pharmacy Assistant • Online</p>
        </div>

        <a
            href="/dashboard"
            class="dashboard-link"
            target="_blank"
        >
            Dashboard
        </a>

    </div>

    <div class="chat-area">

        <div class="date">
            <span>TODAY</span>
        </div>

        <div class="message bot">Assalam-o-Alaikum 👋

Welcome to <b>1st Health Pharmacy</b>.

How can we help you today?

1️⃣ Medicine Availability
2️⃣ Place an Order
3️⃣ Home Delivery
4️⃣ Talk to Pharmacy Staff

<span class="time">{{ current_time }}</span></div>

        {% if customer_message %}
        <div class="message customer">{{ customer_message }}
<span class="time">{{ current_time }}</span></div>
        {% endif %}

        {% if reply %}
        <div class="message bot">{{ reply }}
<span class="time">{{ current_time }}</span></div>
        {% endif %}

    </div>

    <form method="POST" class="input-area">

        <input
            type="text"
            name="message"
            placeholder="Type a message..."
            autocomplete="off"
            required
        >

        <button
            type="submit"
            class="send-btn"
        >
            ➤
        </button>

    </form>

</div>

</body>
</html>
"""


# =========================================================
# DASHBOARD PAGE
# =========================================================

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>

    <meta charset="UTF-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>1st Health Pharmacy Dashboard</title>

    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: Arial, sans-serif;
            background: #f4f7f8;
            color: #1f2937;
        }

        .topbar {
            background: #075e54;
            color: white;
            padding: 20px 35px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .topbar h2 {
            font-size: 22px;
        }

        .topbar p {
            font-size: 12px;
            margin-top: 4px;
            opacity: 0.8;
        }

        .back-btn {
            color: white;
            text-decoration: none;
            border: 1px solid rgba(255,255,255,0.5);
            padding: 9px 14px;
            border-radius: 8px;
            font-size: 13px;
        }

        .container {
            max-width: 1150px;
            margin: 30px auto;
            padding: 0 20px;
        }

        .title {
            margin-bottom: 20px;
        }

        .title h1 {
            font-size: 26px;
            margin-bottom: 5px;
        }

        .title p {
            color: #6b7280;
            font-size: 14px;
        }

        .cards {
            display: grid;
            grid-template-columns:
                repeat(auto-fit, minmax(200px, 1fr));
            gap: 18px;
            margin-bottom: 28px;
        }

        .card {
            background: white;
            padding: 22px;
            border-radius: 14px;
            box-shadow: 0 3px 15px rgba(0,0,0,0.06);
        }

        .label {
            color: #6b7280;
            font-size: 13px;
            margin-bottom: 10px;
        }

        .number {
            font-size: 30px;
            font-weight: bold;
            color: #075e54;
        }

        .table-box {
            background: white;
            border-radius: 14px;
            padding: 22px;
            box-shadow: 0 3px 15px rgba(0,0,0,0.06);
            overflow-x: auto;
        }

        .table-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 18px;
        }

        .live-badge {
            background: #dcfce7;
            color: #166534;
            padding: 6px 10px;
            border-radius: 20px;
            font-size: 12px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            min-width: 750px;
        }

        th {
            text-align: left;
            padding: 13px;
            background: #f8fafc;
            color: #6b7280;
            font-size: 12px;
            border-bottom: 1px solid #e5e7eb;
        }

        td {
            padding: 14px 13px;
            border-bottom: 1px solid #e5e7eb;
            font-size: 13px;
        }

        .status {
            display: inline-block;
            background: #fef3c7;
            color: #92400e;
            padding: 6px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: bold;
        }

        .empty {
            padding: 50px;
            text-align: center;
            color: #6b7280;
        }

        .footer {
            text-align: center;
            color: #9ca3af;
            font-size: 12px;
            margin-top: 25px;
            margin-bottom: 30px;
        }
    </style>

</head>

<body>

<div class="topbar">

    <div>
        <h2>1st Health Pharmacy</h2>
        <p>Digital Operations Dashboard</p>
    </div>

    <a
        href="/"
        class="back-btn"
    >
        ← Customer Demo
    </a>

</div>

<div class="container">

    <div class="title">

        <h1>Pharmacy Requests Dashboard</h1>

        <p>
            Monitor customer requests and
            home-delivery inquiries.
        </p>

    </div>


    <div class="cards">

        <div class="card">
            <div class="label">Total Requests</div>
            <div class="number">{{ total_requests }}</div>
        </div>

        <div class="card">
            <div class="label">Pending Requests</div>
            <div class="number">{{ pending_requests }}</div>
        </div>

        <div class="card">
            <div class="label">Today's Requests</div>
            <div class="number">{{ today_requests }}</div>
        </div>

    </div>


    <div class="table-box">

        <div class="table-header">

            <h3>Recent Customer Requests</h3>

            <span class="live-badge">
                ● Live Demo
            </span>

        </div>

        {% if requests_list %}

        <table>

            <thead>
                <tr>
                    <th>Date / Time</th>
                    <th>Customer</th>
                    <th>Phone</th>
                    <th>Delivery Address</th>
                    <th>Status</th>
                </tr>
            </thead>

            <tbody>

                {% for item in requests_list %}

                <tr>

                    <td>{{ item["Date/Time"] }}</td>
                    <td>{{ item["Customer Name"] }}</td>
                    <td>{{ item["Phone"] }}</td>
                    <td>{{ item["Delivery Address"] }}</td>

                    <td>
                        <span class="status">
                            {{ item["Status"] }}
                        </span>
                    </td>

                </tr>

                {% endfor %}

            </tbody>

        </table>

        {% else %}

        <div class="empty">
            No customer requests yet.
        </div>

        {% endif %}

    </div>


    <div class="footer">
        Demo system for 1st Health Pharmacy
    </div>

</div>

</body>
</html>
"""


# =========================================================
# CSV FUNCTIONS
# =========================================================

def ensure_csv_exists():

    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:

        with open(
            CSV_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "Date/Time",
                "Customer Name",
                "Phone",
                "Delivery Address",
                "Status"
            ])


def ensure_csv_trailing_newline():

    if not os.path.exists(CSV_FILE):
        return

    if os.path.getsize(CSV_FILE) == 0:
        return

    with open(CSV_FILE, "rb+") as file:

        file.seek(-1, os.SEEK_END)

        last_character = file.read(1)

        if last_character not in (b"\n", b"\r"):
            file.seek(0, os.SEEK_END)
            file.write(b"\n")


def save_request(customer_name, phone, address):

    ensure_csv_exists()

    ensure_csv_trailing_newline()

    with open(
        CSV_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(
            file,
            lineterminator="\n"
        )

        writer.writerow([
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            customer_name,
            phone,
            address,
            "Pending"
        ])


def read_requests():

    ensure_csv_exists()

    with open(
        CSV_FILE,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        requests_list = []

        for row in reader:

            if not row.get("Date/Time"):
                continue

            requests_list.append(row)

        return requests_list


# =========================================================
# OTHER FUNCTIONS
# =========================================================

def quantity_is_present(message):

    patterns = [
        r"\b\d+\s*strip",
        r"\b\d+\s*strips",
        r"\b\d+\s*box",
        r"\b\d+\s*boxes",
        r"\b\d+\s*bottle",
        r"\b\d+\s*bottles",
        r"\b\d+\s*pack",
        r"\b\d+\s*packs",
        r"\b\d+\s*tablet",
        r"\b\d+\s*tablets",
        r"\b\d+\s*piece",
        r"\b\d+\s*pieces"
    ]

    for pattern in patterns:

        if re.search(
            pattern,
            message,
            re.IGNORECASE
        ):
            return True

    return False


# =========================================================
# CUSTOMER CHAT
# =========================================================

@app.route("/", methods=["GET", "POST"])
def home():

    reply = None
    customer_message = None

    if request.method == "POST":

        original_message = request.form["message"].strip()

        customer_message = original_message

        message = original_message.lower().strip()

        current_mode = session.get("mode")


        if message in [
            "1",
            "medicine",
            "availability"
        ]:

            session["mode"] = "availability"

            reply = """Please type the medicine name and required quantity. 💊

Example:
Panadol 2 strips"""


        elif message in [
            "2",
            "order",
            "place order"
        ]:

            session["mode"] = "order"

            reply = """Please send the medicine/product name and required quantity. 🛍️

Example:
Panadol 2 strips"""


        elif message in [
            "3",
            "home delivery"
        ]:

            session["mode"] = "delivery_details"

            reply = """Home delivery is available. 🛵

Please send your details in this format:

Name, Phone Number, Delivery Address

Example:
Ali Ahmed, 03001234567, DHA Phase 6 Lahore"""


        elif message in [
            "4",
            "staff",
            "pharmacy staff"
        ]:

            session["mode"] = None

            reply = """Sure. 👨‍⚕️

Your request can be forwarded to a pharmacy staff member for assistance."""


        elif current_mode == "availability":

            if quantity_is_present(message):

                reply = f"""Thank you. 💊

Your medicine availability request has been received.

📋 Request:
{original_message}

⏳ Status: Awaiting Pharmacy Confirmation

A pharmacy team member can check the stock and confirm availability."""

                session["mode"] = None

            else:

                reply = """Please include the required quantity.

Example:
Panadol 2 strips"""


        elif current_mode == "order":

            if quantity_is_present(message):

                session["order_item"] = original_message

                session["mode"] = "order_delivery_choice"

                reply = f"""Thank you. 🛍️

Your order request has been received.

📋 Order:
{original_message}

Would you like this order delivered to your address? 🛵

Reply:

YES / OK — Home Delivery
NO — Store Pickup / Pharmacy Follow-up"""

            else:

                reply = """Please include the required quantity.

Example:
Panadol 2 strips"""


        elif current_mode == "order_delivery_choice":

            if message in [
                "yes",
                "y",
                "ok",
                "okay",
                "home delivery",
                "delivery"
            ]:

                session["mode"] = "delivery_details"

                reply = """Perfect. 🛵

Please send your delivery details in this format:

Name, Phone Number, Delivery Address

Example:
Ali Ahmed, 03001234567, DHA Phase 6 Lahore"""


            elif message in [
                "no",
                "n",
                "pickup",
                "store pickup"
            ]:

                order_item = session.get(
                    "order_item",
                    "Your order"
                )

                reply = f"""Thank you. ✅

📋 Order:
{order_item}

Your order request is awaiting pharmacy confirmation.

A pharmacy team member can contact you regarding stock, price, and pickup."""

                session["mode"] = None

                session.pop(
                    "order_item",
                    None
                )


            else:

                reply = """Please reply:

YES / OK — Home Delivery

NO — Store Pickup / Pharmacy Follow-up"""


        elif current_mode == "delivery_details":

            if "," in original_message:

                parts = [
                    part.strip()
                    for part
                    in original_message.split(",", 2)
                ]

                if len(parts) == 3:

                    customer_name = parts[0]
                    phone = parts[1]
                    address = parts[2]

                    order_item = session.get(
                        "order_item"
                    )

                    save_request(
                        customer_name,
                        phone,
                        address
                    )

                    if order_item:

                        reply = f"""Thank you {customer_name}. ✅

Your order and home-delivery request have been recorded successfully.

🛍️ Order:
{order_item}

📞 Phone:
{phone}

📍 Delivery Address:
{address}

📦 Status:
Pending Pharmacy Confirmation

The pharmacy team can now review your request, confirm stock and price, and process delivery."""

                    else:

                        reply = f"""Thank you {customer_name}. ✅

Your home-delivery request has been recorded successfully.

📞 Phone:
{phone}

📍 Delivery Address:
{address}

📦 Status:
Pending Pharmacy Confirmation

Our pharmacy team can now review your request."""

                    session["mode"] = None

                    session.pop(
                        "order_item",
                        None
                    )

                else:

                    reply = """Please send your details in this format:

Name, Phone Number, Delivery Address"""


            else:

                reply = """Please send all three details separated by commas:

Name, Phone Number, Delivery Address

Example:
Ali Ahmed, 03001234567, DHA Phase 6 Lahore"""


        else:

            reply = """Please choose one option:

1️⃣ Medicine Availability
2️⃣ Place an Order
3️⃣ Home Delivery
4️⃣ Talk to Pharmacy Staff"""


    current_time = datetime.now().strftime(
        "%I:%M %p"
    )

    return render_template_string(
        CHAT_HTML,
        reply=reply,
        customer_message=customer_message,
        current_time=current_time
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    requests_list = read_requests()

    requests_list.reverse()

    total_requests = len(
        requests_list
    )

    pending_requests = sum(
        1
        for item in requests_list
        if item.get("Status") == "Pending"
    )

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    today_requests = sum(
        1
        for item in requests_list
        if item.get(
            "Date/Time",
            ""
        ).startswith(today)
    )

    return render_template_string(
        DASHBOARD_HTML,
        requests_list=requests_list,
        total_requests=total_requests,
        pending_requests=pending_requests,
        today_requests=today_requests
    )


# =========================================================
# START APP
# =========================================================

if __name__ == "__main__":

    ensure_csv_exists()

    app.run(
        debug=True
    )