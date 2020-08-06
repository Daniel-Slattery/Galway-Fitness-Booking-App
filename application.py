import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date, timedelta, datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///bookings.db")
today = date.today()
tomorrow = date.today() + timedelta(days=1)

#reset database slots older than today's date
db.execute("DELETE FROM timeslots WHERE date < :today", today=today)

# Count bookings for availability timetable
capacity = 5

@app.route("/")
def index():
    #""" Setup homepage """
    return render_template("index.html")

@app.route("/reservations", methods=["GET", "POST"])
@login_required
def bookings():
    """Show Users Reservations"""
    id = session["user_id"]

    usernames = db.execute("SELECT username FROM users WHERE id = :id", id=id)
    name = usernames[0]["username"]

    bookings = db.execute("SELECT * FROM timeslots WHERE user_id = :id", id=id)

    if not bookings:
        flash("You do not have any appointments!")
    return render_template("reservations.html", bookings=bookings, name=name)

@app.route("/book", methods=["GET", "POST"])
@login_required
def book():
    """Book Available Time Slot"""
    id = session["user_id"]

    # Todays bookings
    slot1_count = db.execute("SELECT COUNT(slot_id) FROM timeslots WHERE slot_id = '8am - 10am' AND date = :today", today=today)
    slot1_capacity = capacity - slot1_count[0]['COUNT(slot_id)']

    slot2_count = db.execute("SELECT COUNT(slot_id) FROM timeslots WHERE slot_id = '10am - 12pm' AND date = :today", today=today)
    slot2_capacity = capacity - slot2_count[0]['COUNT(slot_id)']

    slot3_count = db.execute("SELECT COUNT(slot_id) FROM timeslots WHERE slot_id = '12pm - 2pm' AND date = :today", today=today)
    slot3_capacity = capacity - slot3_count[0]['COUNT(slot_id)']

    slot4_count = db.execute("SELECT COUNT(slot_id) FROM timeslots WHERE slot_id = '2pm - 4pm' AND date = :today", today=today)
    slot4_capacity = capacity - slot4_count[0]['COUNT(slot_id)']

    slot5_count = db.execute("SELECT COUNT(slot_id) FROM timeslots WHERE slot_id = '4pm - 6pm' AND date = :today", today=today)
    slot5_capacity = capacity - slot5_count[0]['COUNT(slot_id)']

    slot6_count = db.execute("SELECT COUNT(slot_id) FROM timeslots WHERE slot_id = '6pm - 8pm' AND date = :today", today=today)
    slot6_capacity = capacity - slot6_count[0]['COUNT(slot_id)']

    # Tomorrows bookings
    slot7_count = db.execute("SELECT COUNT(slot_id) FROM timeslots WHERE slot_id = '8am - 10am' AND date = :tomorrow", tomorrow=tomorrow)
    slot7_capacity = capacity - slot7_count[0]['COUNT(slot_id)']

    slot8_count = db.execute("SELECT COUNT(slot_id) FROM timeslots WHERE slot_id = '10am - 12pm' AND date = :tomorrow", tomorrow=tomorrow)
    slot8_capacity = capacity - slot8_count[0]['COUNT(slot_id)']

    slot9_count = db.execute("SELECT COUNT(slot_id) FROM timeslots WHERE slot_id = '12pm - 2pm' AND date = :tomorrow", tomorrow=tomorrow)
    slot9_capacity = capacity - slot9_count[0]['COUNT(slot_id)']

    slot10_count = db.execute("SELECT COUNT(slot_id) FROM timeslots WHERE slot_id = '2pm - 4pm' AND date = :tomorrow", tomorrow=tomorrow)
    slot10_capacity = capacity - slot10_count[0]['COUNT(slot_id)']

    slot11_count = db.execute("SELECT COUNT(slot_id) FROM timeslots WHERE slot_id = '4pm - 6pm' AND date = :tomorrow", tomorrow=tomorrow)
    slot11_capacity = capacity - slot11_count[0]['COUNT(slot_id)']

    slot12_count = db.execute("SELECT COUNT(slot_id) FROM timeslots WHERE slot_id = '6pm - 8pm' AND date = :tomorrow", tomorrow=tomorrow)
    slot12_capacity = capacity - slot12_count[0]['COUNT(slot_id)']

    if request.method=="GET":

        return render_template("book.html",
        slot1_capacity=slot1_capacity,
        slot2_capacity=slot2_capacity,
        slot3_capacity=slot3_capacity,
        slot4_capacity=slot4_capacity,
        slot5_capacity=slot5_capacity,
        slot6_capacity=slot6_capacity,
        slot7_capacity=slot7_capacity,
        slot8_capacity=slot8_capacity,
        slot9_capacity=slot9_capacity,
        slot10_capacity=slot10_capacity,
        slot11_capacity=slot11_capacity,
        slot12_capacity=slot12_capacity)

    elif request.method=="POST":
        slot_id = request.form.get("timeslot")
        day = request.form.get("day")

        # Booking Day
        if day == "today":
            booking_date = date.today()
        elif day == "tomorrow":
            booking_date = date.today() + timedelta(days=1)

        # Check to see if capacity is full on desired slot
        time_slot_count_dict = db.execute("SELECT COUNT(slot_id) FROM timeslots WHERE slot_id = :slot_id AND date = :booking_date", slot_id=slot_id, booking_date=booking_date)
        time_slot_count = time_slot_count_dict[0]["COUNT(slot_id)"]

        if time_slot_count >= capacity:
            flash("Time Slot Full, Please Choose Another Time")
            return redirect("/book")
        elif time_slot_count < capacity:
            db.execute("INSERT INTO timeslots (user_id, slot_id, date) VALUES (:user_id, :slot_id, :booking_date)",
                        user_id=session["user_id"],
                        slot_id=slot_id,
                        booking_date=booking_date)
            flash("Time Slot Booked!")

            return redirect("/reservations")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
        """Register user"""

        # if user submitted form via POST
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            confirmation = request.form.get("confirmation")

            # Render Apology if username is blank or already exists
            if username is '':
                return apology("must provide username", 400)

            # Render Apology if input is blank or passwords do not match
            if password is '':
                return apology("must provide password", 400)

            # Ensure password and confirmation match
            if password != confirmation:
                return apology("passwords do not match", 400)

            # Insert new user into users, storing a hash of the users password
            # hash the password and insert a new user in the database
            hash = generate_password_hash(request.form.get("password"))
            new_user_id = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
                                     username=request.form.get("username"),
                                     hash=hash)

            # unique username constraint violated?
            if not new_user_id:
                return apology("username taken", 400)

            # Remember which user has logged in
            session["user_id"] = new_user_id

            # Display a flash message
            flash("Registered!")

            # Redirect user to home page
            return redirect("/")


        # User reached route via GET (as by clicking a link or via redirect)
        else:
            return render_template("register.html")



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
